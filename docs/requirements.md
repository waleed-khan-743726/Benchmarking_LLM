# Requirements

## Product goal

Build a local, zero-inference-cost research application that demonstrates how an open-weight language model translates a natural-language navigation instruction into a validated task while deterministic A* planning and route validation remain authoritative.

## Functional requirements

- Render an interactive 3D grid with a robot, start, goal, static and dynamic obstacles, explored cells, and the current route.
- Support four-directional A* planning, route validation, explicit no-path results, and deterministic seeded scenarios.
- Play, pause, step, resume, and reset robot movement while keeping backend state authoritative.
- Stop before a newly blocked transition, replan on the changed map, and never invoke the LLM merely because an obstacle changed.
- Parse instructions through configurable local Ollama models into a versioned, validated schema; preserve a clearly labelled offline mode.
- Run repeatable baseline and optimized benchmarks sequentially, persist raw measurements, and export JSON, CSV, HTML, and PDF where supported.
- Keep historical runs and distinguish real model measurements from deterministic test data.

## Non-functional requirements

- Windows-first installation; all project-specific storage, caches, dependencies, models, reports, and temporary files are confined to `D:\Robot_Navigation_FYP`.
- Responsive simulator under ordinary grid sizes; long-running inference and benchmarks must not block rendering.
- Accessible contrast, keyboard-reachable controls, plain-language error states, and progressive disclosure.
- No paid services, fabricated results, silent fallbacks, global project dependencies, or secrets in source control.
- Repeatable automated tests with fixed seeds and separate benchmark evidence.

## Environment assessment (2026-10-26)

- Project drive: D:, 465.76 GB total, 405.47 GB free at initial inspection.
- Available D:-based Python: Miniconda Python 3.13.5.
- Node.js 24.19.0 and npm 11.17.0 are installed on C: as existing system tools; local packages and npm cache are redirected to D:.
- Git 2.53.0 is available through the Codex runtime on C:; repository content is on D:.
- Ollama was not found on `PATH` during initial inspection. The simulator therefore starts in offline development mode until Ollama is installed and health-checked.

## Initial storage estimate

- Source, documentation, results, and reports: under 1 GB for normal development.
- Python environment and cache: approximately 0.5–1.5 GB.
- Frontend dependencies, npm cache, and builds: approximately 0.5–1.5 GB.
- Three small quantized Ollama models: approximately 3–8 GB depending on selected tags.
- Recommended safety reserve before model pulls: at least 20 GB free on D:.

## Key risks

- Eight GB RAM limits model size and model concurrency. Mitigation: small quantized models, sequential runs, explicit warm-up measurement.
- Python 3.13 package compatibility may vary. Mitigation: keep dependencies lean and pin a tested set.
- Browser GPU capability may vary. Mitigation: simple geometry, bounded grids, demand-based scene updates, and a graceful 2D status fallback.
- Model output can be malformed. Mitigation: strict schema validation, bounded retries only in optimized mode, and manual controls.

