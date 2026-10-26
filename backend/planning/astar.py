from __future__ import annotations

import heapq
from itertools import count
from time import perf_counter

from .grid import Coordinate, GridMap
from .models import PlanResult, RouteValidation
from .validator import validate_route


class AStarPlanner:
    """Deterministic four-directional A* with Manhattan distance."""

    @staticmethod
    def heuristic(left: Coordinate, right: Coordinate) -> int:
        return abs(left[0] - right[0]) + abs(left[1] - right[1])

    def plan(self, grid: GridMap, start: Coordinate, goal: Coordinate) -> PlanResult:
        started = perf_counter()
        if not grid.in_bounds(start) or not grid.in_bounds(goal):
            return self._failure(started, "invalid", "start or goal is outside the grid")
        if grid.is_blocked(start) or grid.is_blocked(goal):
            return self._failure(started, "invalid", "start or goal is blocked")

        order = count()
        frontier: list[tuple[int, int, Coordinate]] = [
            (self.heuristic(start, goal), next(order), start)
        ]
        came_from: dict[Coordinate, Coordinate | None] = {start: None}
        cost_so_far: dict[Coordinate, int] = {start: 0}
        explored: list[Coordinate] = []

        while frontier:
            _, _, current = heapq.heappop(frontier)
            explored.append(current)
            if current == goal:
                path = self._reconstruct(came_from, goal)
                validation = validate_route(grid, path, start, goal)
                elapsed = (perf_counter() - started) * 1000
                if not validation.valid:
                    return PlanResult(
                        status="invalid_route",
                        explored=tuple(explored),
                        expanded_nodes=len(explored),
                        planning_time_ms=elapsed,
                        validation=validation,
                        message="planner output failed independent validation",
                    )
                return PlanResult(
                    status="success",
                    path=tuple(path),
                    explored=tuple(explored),
                    expanded_nodes=len(explored),
                    path_length=len(path) - 1,
                    planning_time_ms=elapsed,
                    validation=validation,
                )

            for neighbour in grid.neighbours(current):
                new_cost = cost_so_far[current] + 1
                if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                    cost_so_far[neighbour] = new_cost
                    priority = new_cost + self.heuristic(neighbour, goal)
                    heapq.heappush(frontier, (priority, next(order), neighbour))
                    came_from[neighbour] = current

        elapsed = (perf_counter() - started) * 1000
        return PlanResult(
            status="no_path",
            explored=tuple(explored),
            expanded_nodes=len(explored),
            planning_time_ms=elapsed,
            validation=RouteValidation(False, "no route exists"),
            message="destination is unreachable",
        )

    @staticmethod
    def _reconstruct(
        came_from: dict[Coordinate, Coordinate | None], goal: Coordinate
    ) -> list[Coordinate]:
        path = [goal]
        current = goal
        while came_from[current] is not None:
            current = came_from[current]  # type: ignore[assignment]
            path.append(current)
        path.reverse()
        return path

    @staticmethod
    def _failure(started: float, status: str, message: str) -> PlanResult:
        return PlanResult(
            status=status,
            planning_time_ms=(perf_counter() - started) * 1000,
            validation=RouteValidation(False, message),
            message=message,
        )

