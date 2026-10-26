from __future__ import annotations

from collections.abc import Sequence

from .grid import Coordinate, GridMap
from .models import RouteValidation


def validate_route(
    grid: GridMap,
    path: Sequence[Coordinate],
    start: Coordinate,
    goal: Coordinate,
) -> RouteValidation:
    if not path:
        return RouteValidation(False, "route is empty")
    if path[0] != start:
        return RouteValidation(False, "route does not start at the requested start", 0)
    if path[-1] != goal:
        return RouteValidation(False, "route does not end at the requested goal", len(path) - 1)

    for index, cell in enumerate(path):
        if not grid.in_bounds(cell):
            return RouteValidation(False, f"cell {cell} is outside the grid", index)
        if grid.is_blocked(cell):
            return RouteValidation(False, f"cell {cell} is blocked", index)
        if index:
            previous = path[index - 1]
            distance = abs(cell[0] - previous[0]) + abs(cell[1] - previous[1])
            if distance != 1:
                return RouteValidation(False, f"illegal transition {previous} -> {cell}", index)
    return RouteValidation(True)

