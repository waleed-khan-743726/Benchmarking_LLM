from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Any

import httpx
from pydantic import ValidationError

from .prompts import (
    BASELINE_PROMPT_VERSION,
    BASELINE_SYSTEM_PROMPT,
    OPTIMIZED_PROMPT_VERSION,
    OPTIMIZED_SYSTEM_PROMPT,
)
from .schemas import (
    InterpretationMetrics,
    InterpretationRequest,
    InterpretationResult,
    NavigationTask,
)


class OllamaUnavailableError(RuntimeError):
    pass


class OllamaResponseError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: float = 90.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds, connect=3.0)
        self._cache: dict[str, InterpretationResult] = {}

    async def list_models(self) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
        except (httpx.HTTPError, OSError) as exc:
            raise OllamaUnavailableError(
                "Ollama is not reachable on the configured local endpoint"
            ) from exc
        return response.json().get("models", [])

    async def health(self) -> bool:
        try:
            await self.list_models()
        except OllamaUnavailableError:
            return False
        return True

    async def interpret(self, request: InterpretationRequest) -> InterpretationResult:
        prompt, version = self._prompt(request.prompt_mode)
        cache_key = self._cache_key(request, version)
        if request.use_cache and cache_key in self._cache:
            cached = self._cache[cache_key].model_copy(deep=True)
            cached.metrics.cache_hit = True
            cached.metrics.wall_time_ms = 0.0
            return cached

        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": request.instruction.strip()},
            ],
            "format": NavigationTask.model_json_schema(),
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42},
            "keep_alive": "2m",
        }
        started = perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
        except (httpx.HTTPError, OSError) as exc:
            raise OllamaUnavailableError("Local Ollama inference failed or timed out") from exc

        wall_time_ms = (perf_counter() - started) * 1000
        body = response.json()
        content = body.get("message", {}).get("content", "")
        try:
            task = NavigationTask.model_validate_json(content)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise OllamaResponseError("The model returned invalid structured task data") from exc

        result = InterpretationResult(
            model=body.get("model", request.model),
            prompt_version=version,
            task=task,
            metrics=InterpretationMetrics(
                wall_time_ms=wall_time_ms,
                total_duration_ms=self._ns_to_ms(body.get("total_duration")),
                load_duration_ms=self._ns_to_ms(body.get("load_duration")),
                prompt_tokens=body.get("prompt_eval_count"),
                generated_tokens=body.get("eval_count"),
            ),
            raw_response=content,
        )
        if request.use_cache:
            self._cache[cache_key] = result.model_copy(deep=True)
        return result

    @staticmethod
    def _prompt(mode: str) -> tuple[str, str]:
        if mode == "baseline":
            return BASELINE_SYSTEM_PROMPT, BASELINE_PROMPT_VERSION
        return OPTIMIZED_SYSTEM_PROMPT, OPTIMIZED_PROMPT_VERSION

    @staticmethod
    def _cache_key(request: InterpretationRequest, version: str) -> str:
        normalized = " ".join(request.instruction.lower().split())
        material = json.dumps(
            {"instruction": normalized, "model": request.model, "prompt_version": version},
            sort_keys=True,
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    @staticmethod
    def _ns_to_ms(value: int | None) -> float | None:
        return None if value is None else value / 1_000_000

