"""Pluggable LLM access for resume parsing/tailoring assistance.

Providers, selected via LLM_PROVIDER:
  - "ollama"     Free, local, no API key. Default. Talks to a local/self-hosted Ollama server.
  - "groq"       Free tier, cloud. Needs a free GROQ_API_KEY from console.groq.com.
  - "anthropic"  Paid, optional upgrade for higher-quality extraction/tailoring.
  - "none"       Disables the LLM entirely; callers fall back to rule-based/template logic.

All providers speak through this one `complete_json` entry point, so callers (resume_parser,
tailoring_engine) don't need to know which provider is active.
"""

import json

import httpx

from app.core.config import get_settings


class LLMUnavailableError(RuntimeError):
    pass


def is_llm_configured() -> bool:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return True  # no key required; reachability is only known at call time
    if settings.llm_provider == "groq":
        return bool(settings.groq_api_key)
    if settings.llm_provider == "anthropic":
        return bool(settings.anthropic_api_key)
    return False


def complete_json(system: str, user: str, max_tokens: int = 2000) -> dict:
    """Send a prompt instructing the model to reply with a single JSON object, and parse it."""
    provider = get_settings().llm_provider
    if provider == "ollama":
        return _complete_json_ollama(system, user)
    if provider == "groq":
        return _complete_json_groq(system, user, max_tokens)
    if provider == "anthropic":
        return _complete_json_anthropic(system, user, max_tokens)
    raise LLMUnavailableError(f"No LLM provider configured (LLM_PROVIDER={provider!r})")


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def _complete_json_ollama(system: str, user: str) -> dict:
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "format": "json",
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMUnavailableError(
            f"Could not reach Ollama at {settings.ollama_base_url} (is it running? "
            f"try `ollama pull {settings.ollama_model}` first): {exc}"
        ) from exc
    return _parse_json_response(response.json()["message"]["content"])


def _complete_json_groq(system: str, user: str, max_tokens: int) -> dict:
    settings = get_settings()
    if not settings.groq_api_key:
        raise LLMUnavailableError("GROQ_API_KEY is not set")
    try:
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={
                "model": settings.groq_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMUnavailableError(f"Groq request failed: {exc}") from exc
    return _parse_json_response(response.json()["choices"][0]["message"]["content"])


def _complete_json_anthropic(system: str, user: str, max_tokens: int) -> dict:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise LLMUnavailableError("ANTHROPIC_API_KEY is not set")
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise LLMUnavailableError(
            "The 'anthropic' package isn't installed. Run `pip install anthropic` to use "
            "LLM_PROVIDER=anthropic, or switch to the free ollama/groq providers."
        ) from exc

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return _parse_json_response(text)
