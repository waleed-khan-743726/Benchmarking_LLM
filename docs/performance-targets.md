# Performance targets

These are test targets, not claims.

- A* p95 under 50 ms on a 50 x 50 grid at moderate obstacle density on the inspected laptop.
- API planning response under 150 ms p95 excluding network startup effects.
- 30–60 FPS camera interaction for the default 20 x 20 arena where browser/GPU support permits.
- UI remains interactive throughout model inference and benchmark execution.
- Dynamic-obstacle detection occurs before the robot enters the blocked next cell.
- Only one local model benchmark runs at a time.
- Model pulls require at least the estimated model size plus a 5 GB safety margin on D:.

Measurements will record grid size, seed, obstacle density, machine metadata, application version, and whether latency is cold or warm.

