from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from backend.planning import AStarPlanner, Coordinate, GridMap, PlanResult


@dataclass(frozen=True, slots=True)
class SimulationEvent:
    kind: str
    message: str
    position: Coordinate
    planning_time_ms: float | None = None


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    status: str
    position: Coordinate
    goal: Coordinate
    route: tuple[Coordinate, ...]
    route_index: int
    replans: int
    events: tuple[SimulationEvent, ...]


class SimulationEngine:
    """Authoritative logical simulation with safe dynamic-obstacle replanning."""

    def __init__(
        self,
        grid: GridMap,
        start: Coordinate,
        goal: Coordinate,
        planner: AStarPlanner | None = None,
    ) -> None:
        self.grid = grid
        self.start = start
        self.goal = goal
        self.position = start
        self.planner = planner or AStarPlanner()
        self.route: tuple[Coordinate, ...] = ()
        self.route_index = 0
        self.status = "idle"
        self.replans = 0
        self.events: list[SimulationEvent] = []

    def plan(self) -> PlanResult:
        result = self.planner.plan(self.grid, self.position, self.goal)
        if result.status == "success":
            self.route = result.path
            self.route_index = 0
            self.status = "ready" if self.position != self.goal else "completed"
            self.events.append(
                SimulationEvent(
                    "planned",
                    "A valid route was calculated",
                    self.position,
                    result.planning_time_ms,
                )
            )
        else:
            self.route = ()
            self.route_index = 0
            self.status = "no_path" if result.status == "no_path" else "invalid"
            self.events.append(
                SimulationEvent(result.status, result.message or result.status, self.position)
            )
        return result

    def play(self) -> None:
        if self.status in {"ready", "paused"}:
            self.status = "running"

    def pause(self) -> None:
        if self.status == "running":
            self.status = "paused"

    def step(self) -> SimulationSnapshot:
        if self.status not in {"running", "ready", "paused"}:
            return self.snapshot()
        if not self.route:
            self.plan()
        if self.status in {"no_path", "invalid", "completed"}:
            return self.snapshot()
        if self.route_index >= len(self.route) - 1:
            self.status = "completed"
            return self.snapshot()

        next_cell = self.route[self.route_index + 1]
        if self.grid.is_blocked(next_cell):
            self.status = "replanning"
            self.events.append(
                SimulationEvent(
                    "route_blocked",
                    f"Stopped before newly blocked cell {next_cell}",
                    self.position,
                )
            )
            before = perf_counter()
            result = self.planner.plan(self.grid, self.position, self.goal)
            elapsed = (perf_counter() - before) * 1000
            self.replans += 1
            if result.status != "success":
                self.route = ()
                self.route_index = 0
                self.status = "no_path"
                self.events.append(
                    SimulationEvent(
                        "replan_failed",
                        "No safe alternative route exists",
                        self.position,
                        elapsed,
                    )
                )
                return self.snapshot()
            self.route = result.path
            self.route_index = 0
            self.status = "running"
            self.events.append(
                SimulationEvent(
                    "replanned",
                    "Route updated around the obstacle",
                    self.position,
                    elapsed,
                )
            )
            if len(self.route) < 2:
                self.status = "completed"
            # Replanning consumes this authoritative tick. This makes the safety
            # stop observable and prevents a render client from skipping over it.
            return self.snapshot()

        self.position = next_cell
        self.route_index += 1
        if self.position == self.goal:
            self.status = "completed"
            self.events.append(SimulationEvent("completed", "Destination reached", self.position))
        return self.snapshot()

    def add_dynamic_obstacle(self, cell: Coordinate) -> SimulationSnapshot:
        self.grid.add_obstacle(cell, protected=(self.position, self.goal))
        self.events.append(
            SimulationEvent("obstacle_added", f"Obstacle added at {cell}", self.position)
        )
        return self.snapshot()

    def remove_obstacle(self, cell: Coordinate) -> SimulationSnapshot:
        self.grid.remove_obstacle(cell)
        self.events.append(
            SimulationEvent("obstacle_removed", f"Obstacle removed at {cell}", self.position)
        )
        return self.snapshot()

    def reset(self) -> SimulationSnapshot:
        self.position = self.start
        self.route = ()
        self.route_index = 0
        self.status = "idle"
        self.replans = 0
        self.events.clear()
        return self.snapshot()

    def snapshot(self) -> SimulationSnapshot:
        return SimulationSnapshot(
            status=self.status,
            position=self.position,
            goal=self.goal,
            route=self.route,
            route_index=self.route_index,
            replans=self.replans,
            events=tuple(self.events[-50:]),
        )

