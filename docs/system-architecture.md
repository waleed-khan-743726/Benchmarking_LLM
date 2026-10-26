# System architecture

```text
React + TypeScript UI
  | REST / WebSocket
FastAPI application
  |-- task interpretation -> Ollama adapter -> schema validator
  |-- deterministic simulation service
        |-- grid/world model
        |-- A* planner
        |-- independent route validator
        `-- dynamic-obstacle replan policy
  |-- benchmark runner -> SQLite/raw JSON/CSV
  `-- report builder -> HTML/PDF
```

The language model is an interpreter, never the route planner. It may select supported task parameters, but A* and the independent validator decide whether movement is legal. The simulation service owns the logical robot position; the 3D frontend interpolates between authoritative states for display only.

## Coordinate convention

Coordinates are `(x, z)` integer grid cells. `x` increases left-to-right and `z` increases from the near edge toward the far edge in the default camera view. The 3D world maps them to `(x, y, z)`, with `y` used only for height. Four-directional moves have cost 1. Diagonal movement is intentionally excluded from version 1.

## Boundaries

- `backend/planning`: pure deterministic algorithms with no web or model dependencies.
- `backend/simulation`: world mutations, movement, dynamic obstacles, and replanning.
- `backend/llm`: Ollama health, model catalogue, prompts, parsing, and cache.
- `backend/benchmarking`: controlled scenarios, sequential execution, measurements, and persistence.
- `backend/reporting`: evidence-based exports.
- `frontend`: presentation, interaction, local animation, and API state.

## Storage

SQLite holds run metadata and measurements. Raw JSON and CSV exports remain portable. Generated reports never invent observations; an empty database produces a clearly labelled no-results report.

