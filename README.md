# NavLab — 3D Robot Navigation & Local LLM Research

NavLab is a Windows-first FYP research application that separates natural-language task interpretation from deterministic robot motion. A local Ollama model may translate an instruction into a validated schema, but A* and an independent route validator remain authoritative.

The complete beginner-friendly project guide and chronological evidence record is [PROJECT_MASTER_DOCUMENTATION.md](PROJECT_MASTER_DOCUMENTATION.md).

## Storage promise

Project source, Python environment, packages, npm dependencies, caches, temporary files, Ollama runtime/models, logs, experiments, exports, and reports are configured beneath `D:\Robot_Navigation_FYP`. Existing Node/Git executables may run from C: as preinstalled system tools. Ollama's required user-profile directory is a junction whose target is `D:\Robot_Navigation_FYP\.ollama-home`.

## Quick start

Open PowerShell:

```powershell
Set-Location D:\Robot_Navigation_FYP
.\scripts\setup.ps1
.\scripts\run.ps1
```

Then open `http://127.0.0.1:5173`.

`run.ps1` starts the project-local Ollama server, backend, and frontend. The main simulator lets you choose any installed model from the **Local LLM model** dropdown, enter an instruction, and select **Interpret and plan route**. A* validates the route after the LLM interprets the request.

Use the left navigation to open **Benchmark Studio**, run an experiment, view factual aggregates in **Results & Analysis**, and export JSON, CSV, HTML, or PDF from **Research Report**. To inspect the setup:

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

## Reinstall runtime or models

The supplied standalone runtime is installed under `tools\ollama`. To reproduce that installation, the installer downloads the official version-pinned archive directly to D:, verifies its official SHA-256, and extracts it locally:

```powershell
.\scripts\install-ollama.ps1
```

Pull one approved Apache-2.0 model at a time. The script checks D: free space and uses `OLLAMA_MODELS` on D:.

```powershell
.\scripts\pull-model.ps1 -Model 'qwen2.5:0.5b'
.\scripts\pull-model.ps1 -Model 'qwen3:0.6b'
.\scripts\pull-model.ps1 -Model 'smollm2:1.7b-instruct-q4_K_M'
```

Never treat “installed” as “benchmark-ready” until the Model Laboratory reports a successful readiness check and a structured test inference has completed.

