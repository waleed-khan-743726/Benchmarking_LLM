from __future__ import annotations

import shutil
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.api.registry import registry
from backend.api.schemas import (
    HealthResponse,
    ObstacleRequest,
    PlanRequest,
    PlanResponse,
    SimulationActionRequest,
    SimulationCreateRequest,
    SimulationResponse,
)
from backend.benchmarking import BenchmarkConfig, BenchmarkRunner, load_scenarios
from backend.benchmarking.api_schemas import BenchmarkStartRequest
from backend.benchmarking.manager import BenchmarkManager
from backend.config import get_settings
from backend.llm import (
    CANDIDATE_MODELS,
    InterpretationRequest,
    OllamaClient,
    OllamaUnavailableError,
)
from backend.llm.client import OllamaResponseError
from backend.llm.schemas import InterpretationResult
from backend.planning import AStarPlanner, GridMap
from backend.reporting import ReportGenerator
from backend.storage import ExperimentRepository

settings = get_settings()
ollama = OllamaClient(settings.ollama_host, settings.ollama_timeout_seconds)
repository = ExperimentRepository(settings.data_dir / "experiments.db")
benchmark_runner = BenchmarkRunner(repository, ollama)
benchmark_manager = BenchmarkManager(benchmark_runner)
report_generator = ReportGenerator()

app = FastAPI(
    title="Robot Navigation FYP API",
    version="0.1.0",
    description="Authoritative planning, simulation, local LLM, and benchmark API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    disk = shutil.disk_usage(settings.project_root)
    return HealthResponse(
        version=app.version,
        offline_mode=settings.offline_mode,
        project_root=str(settings.project_root),
        data_dir=str(settings.data_dir),
        results_dir=str(settings.results_dir),
        report_dir=str(settings.report_dir),
        free_space_gb=round(disk.free / (1024**3), 2),
    )


@app.get(f"{settings.api_prefix}/models")
async def model_status() -> dict:
    try:
        installed_models = await ollama.list_models()
        ollama_ready = True
    except OllamaUnavailableError:
        installed_models = []
        ollama_ready = False
    installed_names = {item.get("name") for item in installed_models} | {
        item.get("model") for item in installed_models
    }
    return {
        "ollama_ready": ollama_ready,
        "endpoint": settings.ollama_host,
        "offline_mode": settings.offline_mode,
        "candidates": [
            {**asdict(candidate), "installed": candidate.tag in installed_names}
            for candidate in CANDIDATE_MODELS
        ],
        "installed_models": installed_models,
    }


@app.post(f"{settings.api_prefix}/interpret", response_model=InterpretationResult)
async def interpret_instruction(request: InterpretationRequest) -> InterpretationResult:
    try:
        return await ollama.interpret(request)
    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is unavailable. Use manual simulator controls or start the local runtime."
            ),
        ) from exc
    except OllamaResponseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get(f"{settings.api_prefix}/experiments")
def list_experiments() -> list[dict]:
    return repository.list_experiments()


@app.get(f"{settings.api_prefix}/experiments/{{experiment_id}}")
def get_experiment(experiment_id: str) -> dict:
    experiment = repository.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    return experiment


@app.post(f"{settings.api_prefix}/benchmarks", status_code=202)
def start_benchmark(request: BenchmarkStartRequest) -> dict:
    available = load_scenarios(settings.project_root / "experiments" / "scenarios")
    selected = (
        [item for item in available if item.id in request.scenario_ids]
        if request.scenario_ids
        else available
    )
    if not selected:
        raise HTTPException(status_code=422, detail="no matching scenarios were selected")
    allowed_modes = {"baseline", "optimized"}
    if not set(request.prompt_modes).issubset(allowed_modes):
        raise HTTPException(status_code=422, detail="unsupported prompt mode")
    job = benchmark_manager.start(
        request.name,
        selected,
        BenchmarkConfig(
            models=tuple(request.models),
            prompt_modes=tuple(request.prompt_modes),
            repetitions=request.repetitions,
        ),
    )
    return asdict(job)


@app.get(f"{settings.api_prefix}/benchmarks/jobs/{{job_id}}")
def benchmark_job(job_id: str) -> dict:
    job = benchmark_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="benchmark job not found")
    return job


@app.post(f"{settings.api_prefix}/experiments/{{experiment_id}}/exports/{{format_name}}")
def export_experiment(experiment_id: str, format_name: str) -> dict:
    experiment = repository.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    safe_id = "".join(
        character
        for character in experiment_id
        if character.isalnum() or character == "-"
    )
    export_root = settings.results_dir / safe_id
    try:
        if format_name == "json":
            path = repository.export_json(experiment_id, export_root / "results.json")
        elif format_name == "csv":
            path = repository.export_csv(experiment_id, export_root / "results.csv")
        elif format_name == "html":
            path = report_generator.generate_html(
                experiment, settings.report_dir / safe_id / "research-report.html"
            )
        elif format_name == "pdf":
            path = report_generator.generate_pdf(
                experiment, settings.report_dir / safe_id / "research-report.pdf"
            )
        else:
            raise HTTPException(status_code=422, detail="format must be json, csv, html, or pdf")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"format": format_name, "path": str(Path(path))}



@app.post(f"{settings.api_prefix}/plan", response_model=PlanResponse)
def plan(request: PlanRequest) -> PlanResponse:
    try:
        grid = GridMap(
            request.grid.width,
            request.grid.depth,
            {cell.as_tuple() for cell in request.grid.obstacles},
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = AStarPlanner().plan(grid, request.start.as_tuple(), request.goal.as_tuple())
    return PlanResponse.from_result(result)


@app.post(f"{settings.api_prefix}/simulations", response_model=SimulationResponse, status_code=201)
def create_simulation(request: SimulationCreateRequest) -> SimulationResponse:
    try:
        simulation_id, record = registry.create(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SimulationResponse.from_snapshot(simulation_id, record.name, record.engine.snapshot())


def _get_simulation(simulation_id: str):
    record = registry.get(simulation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return record


@app.get(f"{settings.api_prefix}/simulations/{{simulation_id}}", response_model=SimulationResponse)
def get_simulation(simulation_id: str) -> SimulationResponse:
    record = _get_simulation(simulation_id)
    return SimulationResponse.from_snapshot(simulation_id, record.name, record.engine.snapshot())


@app.post(
    f"{settings.api_prefix}/simulations/{{simulation_id}}/actions",
    response_model=SimulationResponse,
)
def simulation_action(
    simulation_id: str, request: SimulationActionRequest
) -> SimulationResponse:
    record = _get_simulation(simulation_id)
    engine = record.engine
    if request.action == "plan":
        engine.plan()
    elif request.action == "play":
        engine.play()
    elif request.action == "pause":
        engine.pause()
    elif request.action == "step":
        engine.step()
    else:
        engine.reset()
    return SimulationResponse.from_snapshot(simulation_id, record.name, engine.snapshot())


@app.post(
    f"{settings.api_prefix}/simulations/{{simulation_id}}/obstacles",
    response_model=SimulationResponse,
)
def change_obstacle(simulation_id: str, request: ObstacleRequest) -> SimulationResponse:
    record = _get_simulation(simulation_id)
    try:
        if request.operation == "add":
            record.engine.add_dynamic_obstacle(request.cell.as_tuple())
        else:
            record.engine.remove_obstacle(request.cell.as_tuple())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SimulationResponse.from_snapshot(
        simulation_id, record.name, record.engine.snapshot()
    )

