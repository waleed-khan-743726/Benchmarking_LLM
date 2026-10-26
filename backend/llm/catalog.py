from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelCandidate:
    tag: str
    family: str
    approximate_size_mb: int
    context: str
    license_summary: str
    source_url: str
    rationale: str


CANDIDATE_MODELS: tuple[ModelCandidate, ...] = (
    ModelCandidate(
        tag="qwen3:0.6b",
        family="Qwen3",
        approximate_size_mb=523,
        context="40K",
        license_summary="Apache 2.0 model family; verify bundled model metadata at pull time",
        source_url="https://ollama.com/library/qwen3:0.6b",
        rationale=(
            "Smallest selected candidate and supports structured instruction-following tests."
        ),
    ),
    ModelCandidate(
        tag="gemma3:1b",
        family="Gemma 3",
        approximate_size_mb=806,
        context="32K",
        license_summary="Gemma Terms of Use; review before redistribution",
        source_url="https://ollama.com/library/gemma3:1b",
        rationale="Compact text model explicitly presented for resource-limited devices.",
    ),
    ModelCandidate(
        tag="smollm2:1.7b-instruct-q4_K_M",
        family="SmolLM2",
        approximate_size_mb=1100,
        context="8K",
        license_summary="Apache 2.0 model family; verify bundled model metadata at pull time",
        source_url="https://ollama.com/library/smollm2:1.7b-instruct-q4_K_M",
        rationale="Instruction-tuned Q4 candidate small enough for an 8 GB machine.",
    ),
)

