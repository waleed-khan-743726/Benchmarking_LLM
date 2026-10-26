# AI Agent Handoff — Rebuild NavLab on a New Windows PC

Give this file and the repository to an AI coding agent. The agent must read this entire file and `PROJECT_MASTER_DOCUMENTATION.md` before acting. The required outcome is a verified, locally running NavLab installation with all project-specific storage on D:.

## Non-negotiable instructions for the receiving agent

1. Use `D:\Robot_Navigation_FYP` as the project root and `D:\Robot_Navigation_FYP\.venv` as the virtual environment.
2. Keep packages, npm modules, caches, downloads, Ollama runtime/models, temporary files, logs, databases, builds, results, and reports on D:.
3. Inspect D: free space before downloading. Require at least 20 GB free for a comfortable setup. Never silently fall back to C:.
4. Extract/copy the source directly to D:. Do not install project dependencies globally or download them to C: before moving them.
5. Use `scripts\project-env.ps1`; do not create machine-wide environment variables without user approval.
6. Existing Windows, Node, Git, or other system executables may remain where already installed. Do not move system files.
7. Never upload, print, or commit credentials, private keys, tokens, or secrets.
8. Do not delete or relocate an existing `%USERPROFILE%\.ollama`. The installer stops if it is not the correct D:-backed junction. Inspect it and ask before destructive migration.
9. Install only the three approved model tags below, sequentially. Verify every installed bundle's licence.
10. Run every verification step and report observed facts. Do not claim completion after a failed or skipped check.

## Product summary

NavLab is a local research application for safe LLM-assisted robot navigation. A selectable local LLM converts a natural-language instruction into a strict task schema. It does not plan or authorize movement. Deterministic four-directional A*, an independent route validator, and the backend-authoritative simulation decide every robot step. The React/Three.js frontend offers a 3D editable warehouse, model switching, live inference metrics, sequential benchmarking, analytics, and JSON/CSV/HTML/PDF reports.

## Expected directories

```text
D:\Robot_Navigation_FYP\
├── .venv\                 Python environment
├── .cache\                pip/npm/download/XDG caches
├── .tmp\                  temporary files
├── .ollama-home\          Ollama identity/cache target
├── backend\               API, planner, simulator, LLM, benchmark, reporting
├── frontend\              React/TypeScript/Three.js application
├── models\ollama\         model manifests and blobs
├── tools\ollama\          standalone runtime
├── experiments\           scenarios and result exports
├── reports\generated\     generated reports
├── logs\                  service logs
├── scripts\               lifecycle scripts
└── tests\                 automated tests
```

## Prerequisites and official links

- Windows 10/11 x64, PowerShell, 8 GB RAM minimum, and at least 20 GB free on D:.
- Python 3.11–3.13 x64 installed on D:. Tested: Python 3.13.5 at `D:\Miniconda3\python.exe`.
- Node.js LTS with `node.exe` and `npm.cmd` on `PATH`. Tested: Node 24.
- Git on `PATH`.
- Internet access for the initial installation.

Official sources:

- Miniconda/conda Windows instructions: https://docs.conda.io/projects/conda/en/stable/user-guide/install/windows.html
- Node.js: https://nodejs.org/en/download
- Git for Windows: https://git-scm.com/download/win
- Ollama releases: https://github.com/ollama/ollama/releases

Install Python itself on D:. Node and Git are system tools and may use an existing installation, but all project packages/caches are redirected to D:.

## Project-scoped storage configuration

Dot-sourcing `scripts\project-env.ps1` configures:

| Variable | D: target |
|---|---|
| `PIP_CACHE_DIR` | `.cache\pip` |
| `npm_config_cache` | `.cache\npm` |
| `npm_config_prefix` | `.cache\npm-prefix` |
| `XDG_CACHE_HOME` | `.cache\xdg` |
| `HF_HOME` | `.cache\huggingface` |
| `TEMP`, `TMP` | `.tmp` |
| `PYTHONPYCACHEPREFIX` | `.cache\pycache` |
| `OLLAMA_MODELS` | `models\ollama` |
| `OLLAMA_NOHISTORY` | `1` |
| data/result/report variables | directories inside the project |

These variables apply only to the active process and its children.

## Libraries

`pyproject.toml` is authoritative for Python:

- FastAPI `>=0.115,<1`, Uvicorn Standard `>=0.32,<1`
- HTTPX `>=0.27,<1`, psutil `>=6,<8`
- Pydantic Settings `>=2.6,<3`, SQLAlchemy `>=2,<3`
- ReportLab `>=4.2,<5`
- pytest `>=8,<10`, pytest-asyncio `>=0.24,<2`, pytest-cov `>=6,<8`, Ruff `>=0.8,<1`

`frontend/package.json` and `package-lock.json` are authoritative for JavaScript:

- React/React DOM `^19.2.0`
- Three.js `^0.180.0`, React Three Fiber `^9.4.0`, Drei `^10.7.6`
- Lucide React `^0.552.0`
- TypeScript `~5.9.3`, Vite `^7.2.0`, Vite React plugin `^5.1.0`
- Matching React, React DOM, and Three.js type packages

Use the lock file. Do not globally install project libraries.

## Pinned Ollama runtime

`scripts\install-ollama.ps1` reproducibly installs:

- Version: `v0.40.11`
- Asset: https://github.com/ollama/ollama/releases/download/v0.40.11/ollama-windows-amd64.zip
- SHA-256: `bda4a493ba8a7c24d57263cd843cd68cee84f44aed4299eeed532acad7eda12a`
- Download: `D:\Robot_Navigation_FYP\.cache\downloads`
- Runtime: `D:\Robot_Navigation_FYP\tools\ollama`
- Models: `D:\Robot_Navigation_FYP\models\ollama`
- Identity/cache: `D:\Robot_Navigation_FYP\.ollama-home`

Ollama expects `%USERPROFILE%\.ollama`. The installer creates that path as a Windows junction to the D: identity directory and refuses to overwrite a normal directory or an unrelated junction.

## Approved local models

| Exact tag | Approx. size | Official link | Required installed licence |
|---|---:|---|---|
| `qwen2.5:0.5b` | 398 MB | https://ollama.com/library/qwen2.5:0.5b | Apache License 2.0 |
| `qwen3:0.6b` | 523 MB | https://ollama.com/library/qwen3:0.6b | Apache License 2.0 |
| `smollm2:1.7b-instruct-q4_K_M` | 1.1 GB | https://ollama.com/library/smollm2:1.7b-instruct-q4_K_M | Apache License 2.0 |

Reference IDs are `a8b0c5157701`, `7df6b6e09427`, and `8ea75f835db9` respectively. If upstream republishes a tag, record the new ID, verify its licence, rerun readiness/tests, and do not claim exact equivalence to the reference benchmark.

## Deployment procedure

### 1. Inspect before installing

```powershell
Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion,OsArchitecture
Get-PSDrive D | Select-Object Name,Used,Free
Get-Command git,node,npm -ErrorAction SilentlyContinue
Test-Path D:\Miniconda3\python.exe
```

Stop if D: is unavailable or undersized.

### 2. Place source and load the environment

Place the repository directly at `D:\Robot_Navigation_FYP`, then:

```powershell
Set-Location D:\Robot_Navigation_FYP
. .\scripts\project-env.ps1
```

Confirm `pyproject.toml`, `frontend\package.json`, and `scripts\project-env.ps1` exist at this level.

### 3. Install dependencies

```powershell
.\scripts\setup.ps1 -IncludeReportDependencies
```

If Python is at another D:-based location:

```powershell
.\scripts\setup.ps1 -IncludeReportDependencies -BasePython 'D:\Path\To\python.exe'
```

The setup refuses a base Python outside D:, creates `.venv`, installs `.[dev,report]`, and installs frontend dependencies under `frontend\node_modules`.

### 4. Install runtime and start services

```powershell
.\scripts\install-ollama.ps1
.\scripts\run.ps1
```

Wait up to 20 seconds. The local endpoints are:

- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000
- Ollama: http://127.0.0.1:11434

### 5. Pull models one at a time

```powershell
.\scripts\pull-model.ps1 -Model 'qwen2.5:0.5b'
.\scripts\pull-model.ps1 -Model 'qwen3:0.6b'
.\scripts\pull-model.ps1 -Model 'smollm2:1.7b-instruct-q4_K_M'

.\tools\ollama\ollama.exe list
.\tools\ollama\ollama.exe show 'qwen2.5:0.5b' --license
.\tools\ollama\ollama.exe show 'qwen3:0.6b' --license
.\tools\ollama\ollama.exe show 'smollm2:1.7b-instruct-q4_K_M' --license
```

Each pull checks its estimated size plus a 5 GB D: safety margin.

### 6. Automated verification

```powershell
. .\scripts\project-env.ps1
.\.venv\Scripts\python.exe -m ruff check backend tests
.\.venv\Scripts\python.exe -m pytest -q

Push-Location .\frontend
npm run typecheck
npm run build
Pop-Location

.\scripts\health-check.ps1
```

Reference result: Ruff passes, 28 tests pass, TypeScript passes, Vite builds, all three services are ready, and three models are detected. Investigate errors; do not hide them.

### 7. Browser acceptance

At http://127.0.0.1:5173 verify:

1. Backend Ready and Language model 3 ready.
2. The 3D warehouse renders and map editing works.
3. The selector lists the three exact model tags.
4. Select Qwen3 and submit: “Navigate to the destination using the shortest safe route. Replan if the corridor becomes blocked.” Verify structured metrics and a valid route.
5. Verify Play, Pause, Step, Reset, speed, start/goal editing, and obstacle editing.
6. Block the next route cell and verify the robot stops before replanning.
7. Model Laboratory shows three installed cards and official links.
8. Results & Analysis loads stored evidence. Treat bundled reference evidence as reference data, not a measurement from the new PC.
9. If machine-specific evidence is required, run a new benchmark and preserve failures.
10. Generate JSON, CSV, HTML, and PDF exports; visually inspect the PDF.

### 8. Storage audit

```powershell
. .\scripts\project-env.ps1
.\.venv\Scripts\python.exe -c "import sys,site,tempfile; print(sys.executable); print(sys.prefix); print(site.getsitepackages()); print(tempfile.gettempdir())"
.\.venv\Scripts\python.exe -m pip cache dir
npm config get cache
$env:OLLAMA_MODELS
Get-Item "$env:USERPROFILE\.ollama" -Force | Select-Object FullName,LinkType,Target
```

Every project path must resolve under D:. Report unavoidable existing system-tool use on C: honestly.

## Lifecycle and logs

```powershell
D:\Robot_Navigation_FYP\run.bat
D:\Robot_Navigation_FYP\scripts\health-check.ps1
D:\Robot_Navigation_FYP\scripts\stop.ps1
```

Error logs are `logs\backend.err.log`, `logs\frontend.err.log`, and `logs\ollama.err.log`.

## Troubleshooting safeguards

- **No D: drive:** stop and ask. Do not silently rewrite the project for C:.
- **Python missing:** install it on D: or pass a D:-based `-BasePython`.
- **Node missing:** install Node LTS and put `node.exe`/`npm.cmd` on `PATH`; reinstall dependencies directly in the project.
- **Existing `.ollama`:** inspect and ask before migration. Never delete it automatically.
- **Model pull failure:** check D: space, network, logs, and `OLLAMA_MODELS`; retry only the allow-listed failed tag.
- **Port conflict:** inspect `Get-NetTCPConnection -State Listen -LocalPort 5173,8000,11434`; never kill an unrelated process without approval.
- **Temporary offline UI:** wait for startup, refresh once, run the health check, then inspect logs.

## Files that define reproducibility

- `pyproject.toml`
- `frontend/package.json` and `frontend/package-lock.json`
- `scripts/project-env.ps1`, `setup.ps1`, `install-ollama.ps1`, `pull-model.ps1`
- `scripts/run.ps1`, `stop.ps1`, `health-check.ps1`
- `backend/llm/catalog.py` and `backend/llm/prompts.py`
- `experiments/scenarios`
- `docs/model-license-evidence.md` and `docs/final-storage-audit.md`
- `PROJECT_MASTER_DOCUMENTATION.md`

## Required completion report

The receiving agent must report:

- OS, CPU, RAM, Python, Node, npm, Git, and Ollama versions.
- D: free space before and after setup.
- Resolved venv, site-packages, pip/npm caches, temp, runtime, model, database, export, report, and log paths.
- Ollama archive checksum result.
- Exact model tags, IDs, sizes, and licence output.
- Ruff, pytest, typecheck, build, health-check, and browser-test results.
- Any unavoidable C: usage.
- Every warning, deviation, failure, or user decision.
- Running application/API URLs.

The setup is complete only when these facts have been observed and reported.
