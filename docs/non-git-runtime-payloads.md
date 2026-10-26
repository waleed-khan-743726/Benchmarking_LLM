# Runtime payloads intentionally not stored in ordinary Git

The working installation is fully operational, but the following generated or machine-specific payloads are excluded from GitHub. This is not missing project logic: each payload is recreated by the committed scripts and lockfiles.

| Payload | Reference location | Reason excluded | Reproduction source |
|---|---|---|---|
| Python virtual environment | `.venv` | OS/Python-specific binaries; not portable | `scripts/setup.ps1`, `pyproject.toml` |
| Frontend dependencies | `frontend/node_modules` | Generated platform-specific dependency tree | `package.json`, `package-lock.json` |
| Python/npm/download caches | `.cache` | Regenerable cache; includes very large archive | package managers and installer scripts |
| Temporary files | `.tmp`, `tmp` | Ephemeral generated data | created automatically |
| Ollama runtime | `tools/ollama` | About 2.1 GB; individual binaries exceed GitHub limits | pinned `scripts/install-ollama.ps1` |
| Model data | `models/ollama` | About 1.9 GB; blobs exceed GitHub's 100 MB ordinary-file limit | allow-listed `scripts/pull-model.ps1` |
| Ollama identity/private key | `.ollama-home` | Contains machine identity and private key material | created locally by Ollama |
| Logs | `logs` | Machine/session-specific runtime output | created by lifecycle scripts |
| Frontend build | `frontend/dist` | Generated output | `npm run build` |
| Local process IDs | `.tmp/*.pid` | Meaningless on another machine | `scripts/run.ps1` |

The repository does include all source code, dependency declarations/lockfiles, exact model tags and links, the pinned Ollama URL and SHA-256, setup/lifecycle scripts, benchmark SQLite database, raw experiment exports, generated research reports, documentation, and tests.

Secrets are never appropriate for source control. `.env`, Ollama identity keys, GitHub credentials, API tokens, and private keys must remain local even when a user requests a “complete” upload.
