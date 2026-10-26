import json
from pathlib import Path

import pytest

from backend.benchmarking import BenchmarkConfig, BenchmarkRunner, load_scenarios
from backend.llm.schemas import InterpretationMetrics, InterpretationResult, NavigationTask
from backend.storage.repository import ExperimentRepository, ResultRecord


def test_repository_persists_and_exports(tmp_path: Path) -> None:
    repository = ExperimentRepository(tmp_path / "experiments.db")
    experiment_id = repository.create_experiment("Persistence test", {"seed": 42})
    repository.add_result(
        experiment_id,
        ResultRecord(
            model="test",
            prompt_mode="optimized",
            scenario_id="basic",
            repetition=1,
            success=True,
            interpretation_correct=True,
            route_valid=True,
        ),
    )
    repository.complete_experiment(experiment_id)
    stored = repository.get_experiment(experiment_id)
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["results"][0]["success"] is True

    json_path = repository.export_json(experiment_id, tmp_path / "result.json")
    csv_path = repository.export_csv(experiment_id, tmp_path / "result.csv")
    assert json.loads(json_path.read_text(encoding="utf-8"))["id"] == experiment_id
    assert "interpretation_correct" in csv_path.read_text(encoding="utf-8-sig")
    repository.close()


def test_load_versioned_scenarios() -> None:
    scenarios = load_scenarios(Path("experiments/scenarios"))
    assert {item.id for item in scenarios} == {"basic-shortest-v1", "restricted-area-v1"}


class FakeOllama:
    async def interpret(self, request):
        return InterpretationResult(
            model=request.model,
            prompt_version="test-v1",
            task=NavigationTask(
                objective="navigate",
                movement_preference="shortest",
                replan_on_obstacle=True,
            ),
            metrics=InterpretationMetrics(wall_time_ms=3.0),
            raw_response='{"objective":"navigate"}',
        )


@pytest.mark.asyncio
async def test_runner_records_real_outcome_structure(tmp_path: Path) -> None:
    repository = ExperimentRepository(tmp_path / "bench.db")
    scenarios = load_scenarios(Path("experiments/scenarios"))[:1]
    runner = BenchmarkRunner(repository, FakeOllama())
    experiment_id = await runner.run(
        "Test run", scenarios, BenchmarkConfig(models=("fake:small",), repetitions=1)
    )
    stored = repository.get_experiment(experiment_id)
    assert stored is not None
    assert stored["status"] == "completed"
    assert len(stored["results"]) == 2
    assert {row["prompt_mode"] for row in stored["results"]} == {"baseline", "optimized"}
    assert all(row["success"] for row in stored["results"])
    repository.close()

