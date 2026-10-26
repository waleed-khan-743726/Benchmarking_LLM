from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from backend.llm.schemas import NavigationTask


class ScenarioGrid(BaseModel):
    width: int = Field(ge=2, le=200)
    depth: int = Field(ge=2, le=200)
    obstacles: list[tuple[int, int]] = Field(default_factory=list)


class BenchmarkScenario(BaseModel):
    id: str
    name: str
    instruction: str
    grid: ScenarioGrid
    start: tuple[int, int]
    goal: tuple[int, int]
    expected_task: NavigationTask


def load_scenarios(directory: Path) -> list[BenchmarkScenario]:
    scenarios: list[BenchmarkScenario] = []
    for path in sorted(directory.glob("*.json")):
        scenarios.append(BenchmarkScenario.model_validate_json(path.read_text(encoding="utf-8")))
    return scenarios

