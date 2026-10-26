# Final storage audit

Verified on 2026-10-26 after installation, benchmarking, reporting, testing, and the production build.

## Resolved paths

| Item | Resolved location | Status |
|---|---|---|
| Project root | `D:\Robot_Navigation_FYP` | Verified |
| Python executable | `D:\Robot_Navigation_FYP\.venv\Scripts\python.exe` | Verified |
| Python prefix | `D:\Robot_Navigation_FYP\.venv` | Verified |
| Site-packages | `D:\Robot_Navigation_FYP\.venv\Lib\site-packages` | Verified |
| Python temporary directory | `D:\Robot_Navigation_FYP\.tmp` | Verified |
| pip cache | `D:\Robot_Navigation_FYP\.cache\pip` | Verified |
| npm cache | `D:\Robot_Navigation_FYP\.cache\npm` | Verified |
| frontend dependencies | `D:\Robot_Navigation_FYP\frontend\node_modules` | Verified |
| frontend production build | `D:\Robot_Navigation_FYP\frontend\dist` | Verified |
| Ollama runtime | `D:\Robot_Navigation_FYP\tools\ollama` | Verified |
| `OLLAMA_MODELS` | `D:\Robot_Navigation_FYP\models\ollama` | Verified |
| Ollama identity/cache target | `D:\Robot_Navigation_FYP\.ollama-home` | Verified |
| benchmark database | `D:\Robot_Navigation_FYP\backend\data\experiments.db` | Verified |
| raw experiment exports | `D:\Robot_Navigation_FYP\experiments\results` | Verified |
| reports | `D:\Robot_Navigation_FYP\reports\generated` | Verified |

D: had 399.28 GB free at the final audit.

## Point-in-time directory sizes

| Directory | Size |
|---|---:|
| `.venv` | 88.73 MB |
| `.cache` | 1,874.94 MB |
| `frontend\node_modules` | 280.75 MB |
| `frontend\dist` | 6.14 MB |
| `models\ollama` | 1,884.57 MB |
| `tools\ollama` | 2,127.69 MB |
| raw result exports | 0.04 MB |
| generated reports | 0.01 MB |
| backend data | 0.04 MB |

## Unavoidable and pre-existing C: usage

- Node.js, Git, Windows components, the Codex runtime, and user-supplied attachments were already installed or stored on C:. They were used in place and not copied into the project.
- Ollama expects `%USERPROFILE%\.ollama` and does not expose a supported `OLLAMA_HOME` variable. `C:\Users\USER\.ollama` is therefore a Windows junction, not a second data copy; its resolved target is `D:\Robot_Navigation_FYP\.ollama-home`.
- No machine-wide environment variables or existing application installations were changed.

All project-created package payloads, caches, downloaded archives, model blobs, temporary files, logs, datasets/scenarios, build artifacts, experiment evidence, and reports reside on D:.
