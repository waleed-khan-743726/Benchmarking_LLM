from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class TaskCoordinate(BaseModel):
    x: int
    z: int


class NavigationTask(BaseModel):
    objective: Literal["navigate", "unsupported"]
    start: TaskCoordinate | None
    goal: TaskCoordinate | None
    movement_preference: Literal["shortest", "safe", "unspecified"]
    avoid_areas: list[str] = Field(max_length=20)
    replan_on_obstacle: bool
    clarification_needed: bool
    clarification_reason: str | None = Field(max_length=300)

    @model_validator(mode="after")
    def clarification_has_reason(self) -> NavigationTask:
        if self.clarification_needed and not self.clarification_reason:
            raise ValueError("clarification_reason is required when clarification_needed is true")
        if self.objective == "unsupported" and not self.clarification_needed:
            raise ValueError("unsupported tasks must require clarification")
        return self


class InterpretationRequest(BaseModel):
    instruction: str = Field(min_length=2, max_length=1_000)
    model: str
    prompt_mode: Literal["baseline", "optimized"] = "optimized"
    use_cache: bool = True


class InterpretationMetrics(BaseModel):
    wall_time_ms: float
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    prompt_tokens: int | None = None
    generated_tokens: int | None = None
    cache_hit: bool = False


class InterpretationResult(BaseModel):
    model: str
    prompt_version: str
    task: NavigationTask
    metrics: InterpretationMetrics
    raw_response: str

