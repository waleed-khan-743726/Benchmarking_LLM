from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

Coordinate = tuple[int, int]


@dataclass(slots=True)
class GridMap:
    """Finite four-neighbour occupancy grid using (x, z) coordinates."""

    width: int
    depth: int
    obstacles: set[Coordinate] = field(default_factory=set)
    min_size: int = 2
    max_size: int = 200

    def __post_init__(self) -> None:
        if not (self.min_size <= self.width <= self.max_size):
            raise ValueError(f"width must be between {self.min_size} and {self.max_size}")
        if not (self.min_size <= self.depth <= self.max_size):
            raise ValueError(f"depth must be between {self.min_size} and {self.max_size}")
        invalid = [cell for cell in self.obstacles if not self.in_bounds(cell)]
        if invalid:
            raise ValueError(f"obstacles outside grid: {invalid[:5]}")

    def in_bounds(self, cell: Coordinate) -> bool:
        x, z = cell
        return 0 <= x < self.width and 0 <= z < self.depth

    def is_blocked(self, cell: Coordinate) -> bool:
        return cell in self.obstacles

    def is_traversable(self, cell: Coordinate) -> bool:
        return self.in_bounds(cell) and not self.is_blocked(cell)

    def neighbours(self, cell: Coordinate) -> Iterator[Coordinate]:
        x, z = cell
        for candidate in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if self.is_traversable(candidate):
                yield candidate

    def add_obstacle(self, cell: Coordinate, protected: Iterable[Coordinate] = ()) -> None:
        if not self.in_bounds(cell):
            raise ValueError(f"obstacle {cell} is outside the grid")
        if cell in set(protected):
            raise ValueError(f"obstacle {cell} conflicts with a protected cell")
        self.obstacles.add(cell)

    def remove_obstacle(self, cell: Coordinate) -> None:
        self.obstacles.discard(cell)

    def copy(self) -> GridMap:
        return GridMap(self.width, self.depth, set(self.obstacles))

