from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, selectinload

from .models import Base, BenchmarkResult, Experiment


@dataclass(slots=True)
class ResultRecord:
    model: str
    prompt_mode: str
    scenario_id: str
    repetition: int
    success: bool
    interpretation_correct: bool
    route_valid: bool
    prompt_version: str | None = None
    wall_time_ms: float | None = None
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    prompt_tokens: int | None = None
    generated_tokens: int | None = None
    cache_hit: bool = False
    path_length: int | None = None
    expanded_nodes: int | None = None
    planning_time_ms: float | None = None
    peak_memory_mb: float | None = None
    failure_reason: str | None = None
    raw_response: str | None = None


class ExperimentRepository:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = database_path
        self.engine = create_engine(f"sqlite:///{database_path.as_posix()}", future=True)
        Base.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def create_experiment(self, name: str, config: dict[str, Any]) -> str:
        experiment_id = str(uuid4())
        with Session(self.engine) as session:
            session.add(
                Experiment(
                    id=experiment_id,
                    name=name,
                    status="running",
                    config_json=json.dumps(config, sort_keys=True),
                )
            )
            session.commit()
        return experiment_id

    def add_result(self, experiment_id: str, record: ResultRecord) -> None:
        with Session(self.engine) as session:
            if session.get(Experiment, experiment_id) is None:
                raise KeyError(f"experiment {experiment_id} does not exist")
            session.add(BenchmarkResult(experiment_id=experiment_id, **asdict(record)))
            session.commit()

    def complete_experiment(self, experiment_id: str, status: str = "completed") -> None:
        with Session(self.engine) as session:
            experiment = session.get(Experiment, experiment_id)
            if experiment is None:
                raise KeyError(f"experiment {experiment_id} does not exist")
            experiment.status = status
            experiment.completed_at = datetime.now(UTC)
            session.commit()

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        with Session(self.engine) as session:
            statement = (
                select(Experiment)
                .options(selectinload(Experiment.results))
                .where(Experiment.id == experiment_id)
            )
            experiment = session.scalar(statement)
            if experiment is None:
                return None
            return self._serialize(experiment)

    def list_experiments(self) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            statement = (
                select(Experiment)
                .options(selectinload(Experiment.results))
                .order_by(Experiment.created_at.desc())
            )
            return [self._serialize(item) for item in session.scalars(statement).all()]

    def export_json(self, experiment_id: str, destination: Path) -> Path:
        data = self.get_experiment(experiment_id)
        if data is None:
            raise KeyError(f"experiment {experiment_id} does not exist")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return destination

    def export_csv(self, experiment_id: str, destination: Path) -> Path:
        data = self.get_experiment(experiment_id)
        if data is None:
            raise KeyError(f"experiment {experiment_id} does not exist")
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = data["results"]
        fields = list(rows[0]) if rows else ["experiment_id", "notice"]
        with destination.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            if rows:
                writer.writerows(rows)
            else:
                writer.writerow(
                    {"experiment_id": experiment_id, "notice": "No benchmark results recorded"}
                )
        return destination

    @staticmethod
    def _serialize(experiment: Experiment) -> dict[str, Any]:
        return {
            "id": experiment.id,
            "name": experiment.name,
            "status": experiment.status,
            "created_at": experiment.created_at.isoformat(),
            "completed_at": (
                experiment.completed_at.isoformat() if experiment.completed_at else None
            ),
            "config": json.loads(experiment.config_json),
            "results": [
                {
                    column.name: getattr(result, column.name)
                    for column in BenchmarkResult.__table__.columns
                }
                for result in experiment.results
            ],
        }

