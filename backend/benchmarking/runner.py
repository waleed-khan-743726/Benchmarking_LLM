from __future__ import annotations

import platform
from dataclasses import dataclass

import psutil

from backend.llm import InterpretationRequest, OllamaClient
from backend.planning import AStarPlanner, GridMap
from backend.storage.repository import ExperimentRepository, ResultRecord

from .scenarios import BenchmarkScenario


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    models: tuple[str, ...]
    prompt_modes: tuple[str, ...] = ("baseline", "optimized")
    repetitions: int = 3


class BenchmarkRunner:
    def __init__(self, repository: ExperimentRepository, ollama: OllamaClient) -> None:
        self.repository = repository
        self.ollama = ollama

    async def run(
        self, name: str, scenarios: list[BenchmarkScenario], config: BenchmarkConfig
    ) -> str:
        if not scenarios:
            raise ValueError("at least one benchmark scenario is required")
        if not config.models:
            raise ValueError("at least one model is required")
        experiment_id = self.repository.create_experiment(
            name,
            {
                "models": list(config.models),
                "prompt_modes": list(config.prompt_modes),
                "repetitions": config.repetitions,
                "scenario_ids": [scenario.id for scenario in scenarios],
                "environment": {
                    "platform": platform.platform(),
                    "processor": platform.processor() or "not reported by Windows",
                    "logical_cpu_count": psutil.cpu_count(logical=True),
                    "physical_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                },
            },
        )
        final_status = "completed"
        try:
            for model in config.models:
                for prompt_mode in config.prompt_modes:
                    for scenario in scenarios:
                        for repetition in range(1, config.repetitions + 1):
                            await self._run_one(
                                experiment_id, model, prompt_mode, scenario, repetition
                            )
        except Exception:
            final_status = "failed"
            raise
        finally:
            self.repository.complete_experiment(experiment_id, final_status)
        return experiment_id

    async def _run_one(
        self,
        experiment_id: str,
        model: str,
        prompt_mode: str,
        scenario: BenchmarkScenario,
        repetition: int,
    ) -> None:
        memory_before = psutil.Process().memory_info().rss
        try:
            interpretation = await self.ollama.interpret(
                InterpretationRequest(
                    instruction=scenario.instruction,
                    model=model,
                    prompt_mode=prompt_mode,
                    use_cache=prompt_mode == "optimized",
                )
            )
            task_correct = self._task_matches(interpretation.task, scenario.expected_task)
            grid = GridMap(
                scenario.grid.width,
                scenario.grid.depth,
                set(scenario.grid.obstacles),
            )
            plan = AStarPlanner().plan(grid, scenario.start, scenario.goal)
            route_valid = plan.status == "success" and plan.validation.valid
            memory_after = psutil.Process().memory_info().rss
            self.repository.add_result(
                experiment_id,
                ResultRecord(
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_version=interpretation.prompt_version,
                    scenario_id=scenario.id,
                    repetition=repetition,
                    success=task_correct and route_valid,
                    interpretation_correct=task_correct,
                    route_valid=route_valid,
                    wall_time_ms=interpretation.metrics.wall_time_ms,
                    total_duration_ms=interpretation.metrics.total_duration_ms,
                    load_duration_ms=interpretation.metrics.load_duration_ms,
                    prompt_tokens=interpretation.metrics.prompt_tokens,
                    generated_tokens=interpretation.metrics.generated_tokens,
                    cache_hit=interpretation.metrics.cache_hit,
                    path_length=plan.path_length,
                    expanded_nodes=plan.expanded_nodes,
                    planning_time_ms=plan.planning_time_ms,
                    peak_memory_mb=max(memory_before, memory_after) / (1024**2),
                    raw_response=interpretation.raw_response,
                ),
            )
        except Exception as exc:
            self.repository.add_result(
                experiment_id,
                ResultRecord(
                    model=model,
                    prompt_mode=prompt_mode,
                    scenario_id=scenario.id,
                    repetition=repetition,
                    success=False,
                    interpretation_correct=False,
                    route_valid=False,
                    failure_reason=f"{type(exc).__name__}: {exc}",
                ),
            )

    @staticmethod
    def _task_matches(actual, expected) -> bool:
        return (
            actual.objective == expected.objective
            and actual.movement_preference == expected.movement_preference
            and actual.replan_on_obstacle == expected.replan_on_obstacle
            and set(actual.avoid_areas) == set(expected.avoid_areas)
            and actual.clarification_needed == expected.clarification_needed
        )

