# Design decisions

1. **Four-directional A*.** Manhattan distance is admissible and easy to audit; diagonal corner rules are avoided in the first release.
2. **Backend-authoritative simulation.** Visual interpolation cannot create or validate navigation state.
3. **Offline-first development.** All deterministic functions work when Ollama is missing; offline results are excluded from model leaderboards.
4. **Sequential model execution.** This fits an 8 GB machine and makes warm/cold latency explicit.
5. **React Three Fiber.** It provides Three.js rendering with React lifecycle management while allowing lightweight instanced grid geometry.
6. **SQLite plus portable exports.** SQLite supports history without infrastructure; JSON/CSV support research inspection.
7. **Project-scoped storage redirection.** PowerShell launch/setup scripts set pip, npm, XDG, Hugging Face, temp, bytecode, result, report, and Ollama paths to D: for their child processes.
8. **Guarded model pulls.** The release installs its approved models sequentially after a D: space check; future pulls remain explicit, allow-listed, and never required for deterministic simulation.

