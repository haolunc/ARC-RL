"""LLM API client using OpenAI SDK."""

import time
from dataclasses import dataclass, field
from openai import OpenAI

_client: OpenAI | None = None
_default_model: str | None = None
_default_temperature: float | None = None


@dataclass
class LLMResponse:
    """Structured response from an LLM API call."""
    # Content
    content: str | None = None
    tool_calls: list | None = None

    # Metadata
    response_id: str | None = None
    actual_model: str | None = None
    finish_reason: str | None = None

    # Token usage
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None

    # Timing
    duration_seconds: float | None = None

    # Request context
    requested_model: str | None = None
    temperature: float | None = None


def _extract_response(response, requested_model: str, temperature: float,
                      duration: float) -> LLMResponse:
    """Extract all useful fields from an OpenAI API response."""
    choice = response.choices[0]
    usage = response.usage

    # Safely extract cached tokens (may not exist on all endpoints)
    cached = None
    if usage:
        details = getattr(usage, 'prompt_tokens_details', None)
        if details:
            cached = getattr(details, 'cached_tokens', None)

    return LLMResponse(
        content=choice.message.content,
        tool_calls=choice.message.tool_calls,
        response_id=response.id,
        actual_model=response.model,
        finish_reason=choice.finish_reason,
        input_tokens=usage.prompt_tokens if usage else None,
        output_tokens=usage.completion_tokens if usage else None,
        cached_tokens=cached,
        duration_seconds=round(duration, 3),
        requested_model=requested_model,
        temperature=temperature,
    )


def init_client(base_url: str, api_key: str, model: str, temperature: float,
                timeout: float = 180.0):
    """Initialize the LLM client. Must be called before call_llm()."""
    global _client, _default_model, _default_temperature
    _client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
    _default_model = model
    _default_temperature = temperature


def _call_with_retry(kwargs: dict, max_retries: int = 3, retry_delay: float = 2.0) -> LLMResponse:
    """Shared retry wrapper for LLM API calls."""
    if _client is None:
        raise RuntimeError("LLM client not initialized. Call init_client() first.")

    model = kwargs.get("model", _default_model)
    temperature = kwargs.get("temperature", _default_temperature)
    kwargs.setdefault("model", model)
    kwargs.setdefault("temperature", temperature)

    t0 = time.time()
    last_error = None
    for attempt in range(max_retries):
        try:
            response = _client.chat.completions.create(**kwargs)
            return _extract_response(response, model, temperature, time.time() - t0)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = retry_delay * (2 ** attempt)
                print(f"  LLM request attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)

    raise RuntimeError(f"LLM API failed after {max_retries} attempts: {last_error}") from last_error


def call_llm(
    messages: list[dict],
    tools: list[dict] = None,
    temperature: float = None,
    model: str = None,
    max_api_retries: int = 3,
) -> LLMResponse:
    """Call the LLM and return structured response with metadata."""
    kwargs = dict(messages=messages)
    if tools is not None:
        kwargs["tools"] = tools
    if temperature is not None:
        kwargs["temperature"] = temperature
    if model is not None:
        kwargs["model"] = model
    return _call_with_retry(kwargs, max_retries=max_api_retries)
