"""LLM API client using OpenAI SDK."""

import time
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

import arc.eval.config as cfg

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Return a cached OpenAI client, creating it on first call."""
    global _client
    if _client is None:
        _client = OpenAI(base_url=cfg.API_BASE_URL, api_key=cfg.API_KEY)
    return _client


def call_llm(
    messages: list[dict],
    temperature: float = None,
    model: str = None,
    max_api_retries: int = 3,
) -> str:
    """Call the LLM and return the assistant's response text."""
    if temperature is None:
        temperature = cfg.DEFAULT_TEMPERATURE
    if model is None:
        model = cfg.MODEL

    client = _get_client()

    for attempt in range(max_api_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except RateLimitError:
            wait = 2 ** (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
        except (APIError, APITimeoutError) as e:
            if attempt < max_api_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  API error: {e}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"LLM API failed after {max_api_retries} attempts: {e}") from e

    raise RuntimeError("LLM API failed: exhausted retries")
