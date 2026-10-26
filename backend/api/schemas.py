from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from backend.planning import PlanResult
from backend.simulation import SimulationSnapshot


class CoordinateSchema(BaseModel):
    x: int
    z: int

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.z

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> CoordinateSchema:
        return cls(x=value[0], z=value[1])


class GridSchema(BaseModel):
    width: int = Field(default=20, ge=2, le=200)
    depth: int = Field(default=20, ge=2, le=200)
    obstacles: list[CoordinateSchema] = Field(default_factory=list, max_length=20_000)

    @field_validator("obstacles")
    @classmethod
    def obstacles_must_be_unique(cls, value: list[CoordinateSchema]) -> list[CoordinateSchema]:
        cells = [cell.as_tuple() for cell in value]
        if len(cells) != len(set(cells)):
            raise ValueError("obstacles must be unique")
        return value


class PlanRequest(BaseModel):
    grid: GridSchema
    start: CoordinateSchema
    goal: CoordinateSchema


class ValidationSchema(BaseModel):
    valid: bool
    reason: str | None = None
    invalid_index: int | None = None


class PlanResponse(BaseModel):
    status: str
    path: list[CoordinateSchema]
    explored: list[CoordinateSchema]
    expanded_nodes: int
    path_length: int
    planning_time_ms: float
    validation: ValidationSchema
    message: str | None = None

    @classmethod
    def from_result(cls, result: PlanResult) -> PlanResponse:
        return cls(
            status=result.status,
            path=[CoordinateSchema.from_tuple(cell) for cell in result.path],
            explored=[CoordinateSchema.from_tuple(cell) for cell in result.explored],
            expanded_nodes=result.expanded_nodes,
            path_length=result.path_length,
            planning_time_ms=result.planning_time_ms,
            validation=ValidationSchema(
                valid=result.validation.valid,
                reason=result.validation.reason,
                invalid_index=result.validation.invalid_index,
            ),
            message=result.message,
        )


class SimulationCreateRequest(PlanRequest):
    name: str = Field(default="Untitled scenario", min_length=1, max_length=80)


class EventSchema(BaseModel):
    kind: str
    message: str
    position: CoordinateSchema
    planning_time_ms: float | None = None


class SimulationResponse(BaseModel):
    id: str
    name: str
    status: str
    position: CoordinateSchema
    goal: CoordinateSchema
    route: list[CoordinateSchema]
    route_index: int
    replans: int
    events: list[EventSchema]

    @classmethod
    def from_snapshot(
        cls, simulation_id: str, name: str, snapshot: SimulationSnapshot
    ) -> SimulationResponse:
        return cls(
            id=simulation_id,
            name=name,
            status=snapshot.status,
            position=CoordinateSchema.from_tuple(snapshot.position),
            goal=CoordinateSchema.from_tuple(snapshot.goal),
            route=[CoordinateSchema.from_tuple(cell) for cell in snapshot.route],
            route_index=snapshot.route_index,
            replans=snapshot.replans,
            events=[
                EventSchema(
                    kind=event.kind,
                    message=event.message,
                    position=CoordinateSchema.from_tuple(event.position),
                    planning_time_ms=event.planning_time_ms,
                )
                for event in snapshot.events
            ],
        )


class SimulationActionRequest(BaseModel):
    action: Literal["plan", "play", "pause", "step", "reset"]


class ObstacleRequest(BaseModel):
    cell: CoordinateSchema
    operation: Literal["add", "remove"] = "add"


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
    offline_mode: bool
    project_root: str
    data_dir: str
    results_dir: str
    report_dir: str
    free_space_gb: float

