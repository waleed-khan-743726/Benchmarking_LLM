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
        tag="qwen2.5:0.5b",
        family="Qwen2.5",
        approximate_size_mb=398,
        context="32K",
        license_summary="Apache License 2.0",
        source_url="https://ollama.com/library/qwen2.5:0.5b",
        rationale="Small structured-output baseline with strong JSON instruction support.",
    ),
    ModelCandidate(
        tag="qwen3:0.6b",
        family="Qwen3",
        approximate_size_mb=523,
        context="40K",
        license_summary="Apache License 2.0",
        source_url="https://ollama.com/library/qwen3:0.6b",
        rationale=(
            "Compact newer Qwen candidate for structured instruction-following comparison."
        ),
    ),
    ModelCandidate(
        tag="smollm2:1.7b-instruct-q4_K_M",
        family="SmolLM2",
        approximate_size_mb=1100,
        context="8K",
        license_summary="Apache License 2.0",
        source_url="https://ollama.com/library/smollm2:1.7b-instruct-q4_K_M",
        rationale="Instruction-tuned Q4 candidate small enough for an 8 GB machine.",
    ),
)

