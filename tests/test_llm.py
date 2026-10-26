import json

import httpx
import pytest

from backend.llm.client import OllamaClient, OllamaResponseError, OllamaUnavailableError
from backend.llm.schemas import InterpretationRequest, NavigationTask


def test_navigation_task_requires_reason_for_clarification() -> None:
    with pytest.raises(ValueError):
        NavigationTask(objective="unsupported", clarification_needed=True)


def test_cache_key_normalizes_equivalent_whitespace_and_case() -> None:
    first = InterpretationRequest(instruction="Reach  the GOAL", model="test")
    second = InterpretationRequest(instruction=" reach the goal ", model="test")
    assert OllamaClient._cache_key(first, "v1") == OllamaClient._cache_key(second, "v1")
    assert OllamaClient._cache_key(first, "v1") != OllamaClient._cache_key(first, "v2")


@pytest.mark.asyncio
async def test_valid_structured_response_and_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    content = json.dumps(
        {
            "objective": "navigate",
            "start": None,
            "goal": None,
            "movement_preference": "shortest",
            "avoid_areas": [],
            "replan_on_obstacle": True,
            "clarification_needed": False,
            "clarification_reason": None,
        }
    )
    calls = 0

    async def fake_post(self, url, **kwargs):
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={
                "model": "test:small",
                "message": {"content": content},
                "total_duration": 2_000_000,
                "load_duration": 500_000,
                "prompt_eval_count": 20,
                "eval_count": 8,
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    client = OllamaClient("http://local.test")
    request = InterpretationRequest(instruction="Use the shortest route", model="test:small")
    first = await client.interpret(request)
    second = await client.interpret(request)
    assert first.task.movement_preference == "shortest"
    assert first.metrics.total_duration_ms == 2.0
    assert second.metrics.cache_hit is True
    assert calls == 1


@pytest.mark.asyncio
async def test_malformed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(self, url, **kwargs):
        return httpx.Response(
            200,
            json={"model": "test", "message": {"content": "not-json"}},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    with pytest.raises(OllamaResponseError):
        await OllamaClient("http://local.test").interpret(
            InterpretationRequest(instruction="Go to the goal", model="test")
        )


@pytest.mark.asyncio
async def test_unavailable_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get(self, url, **kwargs):
        raise httpx.ConnectError("unavailable")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    client = OllamaClient("http://local.test")
    assert await client.health() is False
    with pytest.raises(OllamaUnavailableError):
        await client.list_models()

