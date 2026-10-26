# Ollama runtime and model evidence

Verified on 2026-10-26. Values below come from the installed runtime and retained release metadata, not estimates presented as measurements.

## Runtime

- Ollama version: `0.40.11`
- Executable: `D:\Robot_Navigation_FYP\tools\ollama\ollama.exe`
- Official archive SHA-256: `bda4a493ba8a7c24d57263cd843cd68cee84f44aed4299eeed532acad7eda12a`
- Model storage: `D:\Robot_Navigation_FYP\models\ollama`
- Identity/cache storage: `D:\Robot_Navigation_FYP\.ollama-home`

## Installed model bundles

| Exact tag | Ollama ID | Listed size | Installed licence check |
|---|---|---:|---|
| `qwen2.5:0.5b` | `a8b0c5157701` | 397 MB | Apache License 2.0 |
| `qwen3:0.6b` | `7df6b6e09427` | 522 MB | Apache License 2.0 |
| `smollm2:1.7b-instruct-q4_K_M` | `8ea75f835db9` | about 1.1 GB | Apache License 2.0 |

The licence result was checked against each exact installed bundle with `ollama show --license`. Official model URLs are also exposed by the backend and Model Laboratory UI. “Free” here means no paid inference service is used and the installed bundle reports Apache License 2.0; users remain responsible for compliance with that licence.

## Storage boundary

The runtime archive, executable, model manifests/blobs, project dependencies, caches, benchmark database, exports, reports, and temporary build data are on D:. `%USERPROFILE%\.ollama` is an unavoidable name expected by Ollama; it is a Windows junction whose target and contents are on D:. Existing Node, Git, Codex, Windows components, and the supplied attachments were already present on C: and were not relocated.
