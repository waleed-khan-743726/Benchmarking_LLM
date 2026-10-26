from __future__ import annotations

from dataclasses import dataclass, field

from .grid import Coordinate


@dataclass(frozen=True, slots=True)
class RouteValidation:
    valid: bool
    reason: str | None = None
    invalid_index: int | None = None


@dataclass(frozen=True, slots=True)
class PlanResult:
    status: str
    path: tuple[Coordinate, ...] = ()
    explored: tuple[Coordinate, ...] = ()
    expanded_nodes: int = 0
    path_length: int = 0
    planning_time_ms: float = 0.0
    validation: RouteValidation = field(
        default_factory=lambda: RouteValidation(False, "not validated")
    )
    message: str | None = None

