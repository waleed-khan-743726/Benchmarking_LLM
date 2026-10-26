from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from backend.planning import GridMap
from backend.simulation import SimulationEngine

from .schemas import SimulationCreateRequest


@dataclass(slots=True)
class SimulationRecord:
    name: str
    engine: SimulationEngine


class SimulationRegistry:
    def __init__(self) -> None:
        self._records: dict[str, SimulationRecord] = {}
        self._lock = RLock()

    def create(self, request: SimulationCreateRequest) -> tuple[str, SimulationRecord]:
        grid = GridMap(
            request.grid.width,
            request.grid.depth,
            {cell.as_tuple() for cell in request.grid.obstacles},
        )
        record = SimulationRecord(
            name=request.name,
            engine=SimulationEngine(grid, request.start.as_tuple(), request.goal.as_tuple()),
        )
        record.engine.plan()
        simulation_id = str(uuid4())
        with self._lock:
            self._records[simulation_id] = record
        return simulation_id, record

    def get(self, simulation_id: str) -> SimulationRecord | None:
        with self._lock:
            return self._records.get(simulation_id)


registry = SimulationRegistry()

