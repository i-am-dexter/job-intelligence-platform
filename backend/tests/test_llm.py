import httpx
import pytest

from app.core.config import get_settings
from app.services import llm


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_ollama_is_always_considered_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert llm.is_llm_configured() is True


def test_groq_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert llm.is_llm_configured() is False

    get_settings.cache_clear()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    assert llm.is_llm_configured() is True


def test_none_provider_is_never_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "none")
    assert llm.is_llm_configured() is False


def test_none_provider_raises_on_complete_json(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "none")
    with pytest.raises(llm.LLMUnavailableError):
        llm.complete_json(system="sys", user="hello")


def test_ollama_complete_json_parses_response(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": '{"foo": "bar"}'}}

    def fake_post(url, json=None, timeout=None):
        assert "/api/chat" in url
        assert json["format"] == "json"
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    result = llm.complete_json(system="sys", user="hello")
    assert result == {"foo": "bar"}


def test_ollama_unreachable_raises_llm_unavailable(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")

    def fake_post(url, json=None, timeout=None):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(llm.LLMUnavailableError):
        llm.complete_json(system="sys", user="hello")


def test_groq_complete_json_parses_openai_style_response(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": '{"foo": "baz"}'}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        assert "groq.com" in url
        assert headers["Authorization"] == "Bearer test-key"
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    result = llm.complete_json(system="sys", user="hello")
    assert result == {"foo": "baz"}


def test_groq_without_key_raises_before_network_call(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    def fake_post(*args, **kwargs):
        raise AssertionError("should not attempt a network call without an API key")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(llm.LLMUnavailableError):
        llm.complete_json(system="sys", user="hello")


def test_json_response_strips_markdown_code_fence():
    assert llm._parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm._parse_json_response('{"a": 1}') == {"a": 1}
