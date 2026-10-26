# Acceptance criteria

Status values: `TODO`, `IN PROGRESS`, `VERIFIED`, `BLOCKED`.

| Area | Criterion | Status |
|---|---|---|
| Storage | Project and project-specific caches are on D: | VERIFIED |
| Planning | A* finds and validates legal four-directional paths | VERIFIED |
| Planning | Invalid, blocked, and unreachable requests have explicit outcomes | VERIFIED |
| Simulation | Movement controls follow authoritative planned steps | VERIFIED |
| Replanning | A newly blocked next step stops movement and safely replans | VERIFIED |
| API | Health, planning, simulation actions, and obstacle validation work | VERIFIED |
| 3D UI | Grid, robot, goal, route, obstacles, camera, and editing work | VERIFIED |
| LLM | Ollama health/model readiness are verified, not assumed | VERIFIED (runtime currently unavailable) |
| LLM | At least three practical model tags are configurable | VERIFIED as candidates; not installed/tested |
| Benchmark | Baseline/optimized engine persists real measurements | VERIFIED with controlled adapter; no live model run |
| Export | Historical data exports as JSON and CSV | VERIFIED |
| Report | HTML/PDF reports are generated from stored evidence | VERIFIED |
| Delivery | Windows setup, launch, health check, tests, and troubleshooting work | VERIFIED |

