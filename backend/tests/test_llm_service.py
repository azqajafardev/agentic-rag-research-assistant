"""Unit tests for LLM provider selection and behavior. No real network calls."""

from types import SimpleNamespace

import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import LLMError
from app.models.conversation import Message
from app.services.llm_service import LLMService

pytestmark = pytest.mark.filterwarnings("ignore")


def _settings(**overrides) -> Settings:
    base = dict(llm_provider="anthropic", llm_model="claude-opus-5", llm_api_key="test-key")
    base.update(overrides)
    return Settings(**base)


def _history() -> list[Message]:
    return []


# --------------------------------------------------------------------------
# Provider selection
# --------------------------------------------------------------------------


def test_invalid_provider_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        LLMService(_settings(llm_provider="unknown-provider"))


def test_anthropic_provider_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _FakeMessages:
        def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(type="text", text="ok")])

    class _FakeAnthropicClient:
        def __init__(self, api_key=None):
            self.messages = _FakeMessages()

    monkeypatch.setattr(anthropic, "Anthropic", _FakeAnthropicClient)

    service = LLMService(_settings(llm_provider="anthropic"))
    assert service._provider.__class__.__name__ == "_AnthropicProvider"


def test_groq_provider_selected() -> None:
    service = LLMService(_settings(llm_provider="groq", llm_model="openai/gpt-oss-20b"))
    assert service._provider.__class__.__name__ == "_GroqProvider"


def test_groq_default_model_applied_when_unset() -> None:
    settings = Settings(llm_provider="groq", llm_api_key="test-key")
    assert settings.llm_model == "openai/gpt-oss-20b"


def test_anthropic_default_model_unaffected() -> None:
    # Checks the field defaults directly (not a bare Settings()) so this test
    # doesn't depend on whether a local backend/.env happens to exist.
    assert Settings.model_fields["llm_provider"].default == "anthropic"
    assert Settings.model_fields["llm_model"].default == "claude-opus-5"


# --------------------------------------------------------------------------
# Anthropic behavior remains functional (unchanged)
# --------------------------------------------------------------------------


def test_anthropic_generate_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    captured = {}

    class _FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(content=[SimpleNamespace(type="text", text="Grounded answer.")])

    class _FakeAnthropicClient:
        def __init__(self, api_key=None):
            self.messages = _FakeMessages()

    monkeypatch.setattr(anthropic, "Anthropic", _FakeAnthropicClient)

    service = LLMService(_settings(llm_provider="anthropic"))
    answer = service.generate("What dataset?", "SOURCE 1: ...", _history())

    assert answer == "Grounded answer."
    assert captured["model"] == "claude-opus-5"
    assert captured["messages"][-1]["role"] == "user"


# --------------------------------------------------------------------------
# Groq: success + error mapping
# --------------------------------------------------------------------------


def _groq_service() -> LLMService:
    return LLMService(_settings(llm_provider="groq", llm_model="openai/gpt-oss-20b"))


class _FakeResponse:
    def __init__(self, status_code: int, json_body: dict | None = None):
        self.status_code = status_code
        self._json_body = json_body or {}

    def json(self):
        return self._json_body


def test_groq_generate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse(200, {"choices": [{"message": {"content": "Grounded groq answer."}}]})

    monkeypatch.setattr("app.services.llm_service.httpx.post", fake_post)

    service = _groq_service()
    answer = service.generate("What dataset?", "SOURCE 1: ...", _history())

    assert answer == "Grounded groq answer."
    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert captured["json"]["model"] == "openai/gpt-oss-20b"
    assert captured["json"]["messages"][0]["role"] == "system"
    assert captured["json"]["messages"][-1]["role"] == "user"
    assert "Bearer test-key" == captured["headers"]["Authorization"]
    # The key must never leak into an exception/log path either.
    assert "test-key" not in repr(captured["url"])


def test_groq_401_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_service.httpx.post", lambda *a, **k: _FakeResponse(401, {})
    )
    service = _groq_service()
    with pytest.raises(LLMError, match="not configured correctly"):
        service.generate("q", "ctx", _history())


def test_groq_429_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_service.httpx.post", lambda *a, **k: _FakeResponse(429, {})
    )
    service = _groq_service()
    with pytest.raises(LLMError, match="rate-limited"):
        service.generate("q", "ctx", _history())


def test_groq_server_error_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_service.httpx.post", lambda *a, **k: _FakeResponse(500, {})
    )
    service = _groq_service()
    with pytest.raises(LLMError, match="currently unavailable"):
        service.generate("q", "ctx", _history())


def test_groq_timeout_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr("app.services.llm_service.httpx.post", fake_post)
    service = _groq_service()
    with pytest.raises(LLMError, match="timed out"):
        service.generate("q", "ctx", _history())


def test_groq_connection_error_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr("app.services.llm_service.httpx.post", fake_post)
    service = _groq_service()
    with pytest.raises(LLMError, match="Could not reach"):
        service.generate("q", "ctx", _history())


def test_groq_unexpected_response_shape_maps_to_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_service.httpx.post", lambda *a, **k: _FakeResponse(200, {"unexpected": True})
    )
    service = _groq_service()
    with pytest.raises(LLMError, match="unexpected response"):
        service.generate("q", "ctx", _history())
