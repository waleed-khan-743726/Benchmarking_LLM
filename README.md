# NavLab — 3D Robot Navigation & Local LLM Research

NavLab is a Windows-first FYP research application that separates natural-language task interpretation from deterministic robot motion. A local Ollama model may translate an instruction into a validated schema, but A* and an independent route validator remain authoritative.

The complete beginner-friendly project guide and chronological evidence record is [PROJECT_MASTER_DOCUMENTATION.md](PROJECT_MASTER_DOCUMENTATION.md).

## Storage promise

Project source, Python environment, packages, npm dependencies, caches, temporary files, Ollama models, logs, experiments, exports, and reports are configured beneath `D:\Robot_Navigation_FYP`. Existing Node/Git executables may run from C: as preinstalled system tools. No model has been downloaded automatically.

## Quick start

Open PowerShell:

```powershell
Set-Location D:\Robot_Navigation_FYP
.\scripts\setup.ps1
.\scripts\run.ps1
```

Then open `http://127.0.0.1:5173`.

The simulator works without Ollama. To inspect the setup:

```powershell
.\scripts\health-check.ps1
```

To stop project processes started by the launch script:

```powershell
.\scripts\stop.ps1
```

## Test and build

```powershell
. .\scripts\project-env.ps1
.\.venv\Scripts\python.exe -m ruff check backend tests
.\.venv\Scripts\python.exe -m pytest -q --cov=backend --cov-report=term-missing
Set-Location .\frontend
npm run typecheck
npm run build
```

## Optional local model pull

Ollama is not installed by this project. After installing a compatible Ollama runtime and ensuring it is on `PATH`, pull one approved model at a time. The script checks D: free space and uses `OLLAMA_MODELS` on D:.

```powershell
.\scripts\pull-model.ps1 -Model 'qwen3:0.6b'
```

Never treat “installed” as “benchmark-ready” until the Model Laboratory reports a successful readiness check and a structured test inference has completed.

