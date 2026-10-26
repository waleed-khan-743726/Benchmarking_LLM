from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config_json: Mapped[str] = mapped_column(Text)
    results: Mapped[list[BenchmarkResult]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id"), index=True)
    model: Mapped[str] = mapped_column(String(120))
    prompt_mode: Mapped[str] = mapped_column(String(20))
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    scenario_id: Mapped[str] = mapped_column(String(80))
    repetition: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean)
    interpretation_correct: Mapped[bool] = mapped_column(Boolean)
    route_valid: Mapped[bool] = mapped_column(Boolean)
    wall_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    load_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    path_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expanded_nodes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planning_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_memory_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    experiment: Mapped[Experiment] = relationship(back_populates="results")

