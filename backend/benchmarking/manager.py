from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from typing import Literal
from uuid import uuid4

from .runner import BenchmarkConfig, BenchmarkRunner
from .scenarios import BenchmarkScenario


@dataclass(slots=True)
class BenchmarkJob:
    id: str
    status: Literal["queued", "running", "completed", "failed"] = "queued"
    experiment_id: str | None = None
    error: str | None = None


class BenchmarkManager:
    def __init__(self, runner: BenchmarkRunner) -> None:
        self.runner = runner
        self.jobs: dict[str, BenchmarkJob] = {}
        self.tasks: dict[str, asyncio.Task] = {}

    def start(
        self, name: str, scenarios: list[BenchmarkScenario], config: BenchmarkConfig
    ) -> BenchmarkJob:
        job = BenchmarkJob(id=str(uuid4()))
        self.jobs[job.id] = job
        self.tasks[job.id] = asyncio.create_task(self._execute(job, name, scenarios, config))
        return job

    def get(self, job_id: str) -> dict | None:
        job = self.jobs.get(job_id)
        return asdict(job) if job else None

    async def _execute(
        self,
        job: BenchmarkJob,
        name: str,
        scenarios: list[BenchmarkScenario],
        config: BenchmarkConfig,
    ) -> None:
        job.status = "running"
        try:
            job.experiment_id = await self.runner.run(name, scenarios, config)
            job.status = "completed"
        except Exception as exc:
            job.status = "failed"
            job.error = f"{type(exc).__name__}: {exc}"

