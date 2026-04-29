"""LLM API client using OpenAI SDK."""

import os
import time
from openai import (
    OpenAI,
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    PermissionDeniedError,
    BadRequestError,
)

from .config import (
    API_BASE_URL,
    API_KEY,
    MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)

_client: OpenAI | None = None


class LLMCallError(RuntimeError):
    """Typed error for LLM call failures."""

    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


def _get_client() -> OpenAI:
    global _client
    if _client is not None:
        return _client

    runtime_api_key = (
        os.getenv("ARC_API_KEY")
        or os.getenv("DASHSCOPE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or API_KEY
    )
    if not runtime_api_key:
        raise RuntimeError(
            "No API key found. Set ARC_API_KEY, DASHSCOPE_API_KEY, or OPENAI_API_KEY."
        )

    _client = OpenAI(
        base_url=API_BASE_URL,
        api_key=runtime_api_key,
        timeout=120.0,
        max_retries=0,
    )
    return _client


def call_llm(
    messages: list[dict],
    temperature: float = DEFAULT_TEMPERATURE,
    model: str = MODEL,
    max_api_retries: int = 2,
    api_timeout: float = 120.0,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Call the LLM endpoint and return the assistant's response text."""
    if max_api_retries < 1:
        raise ValueError("max_api_retries must be >= 1")
    if api_timeout <= 0:
        raise ValueError("api_timeout must be > 0")

    for attempt in range(max_api_retries):
        try:
            start = time.time()
            client = _get_client()

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=api_timeout,
                max_tokens=max_tokens,
            )

            elapsed = time.time() - start
            print(f"  API call finished in {elapsed:.2f}s", flush=True)

            content = response.choices[0].message.content
            if content is None:
                raise RuntimeError("LLM response content is None")

            return content

        except (AuthenticationError, PermissionDeniedError, BadRequestError) as e:
            raise LLMCallError(
                "api_auth_error",
                f"LLM request is not retriable ({type(e).__name__}): {e}"
            ) from e

        except RateLimitError as e:
            if attempt < max_api_retries - 1:
                wait = min(60, 2 ** (attempt + 1))
                print(f"  Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise LLMCallError(
                    "api_rate_limit",
                    f"LLM API rate-limited after {max_api_retries} attempts: {e}",
                ) from e

        except APITimeoutError as e:
            if attempt < max_api_retries - 1:
                wait = min(60, 2 ** (attempt + 1))
                print(f"  API timeout: {e}, retrying in {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise LLMCallError(
                    "api_timeout",
                    f"LLM API timed out after {max_api_retries} attempts: {e}"
                ) from e

        except APIConnectionError as e:
            if attempt < max_api_retries - 1:
                wait = min(60, 2 ** (attempt + 1))
                print(f"  Connection error: {e}, retrying in {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise LLMCallError(
                    "api_connection_error",
                    f"LLM API connection failed after {max_api_retries} attempts: {e}",
                ) from e

        except APIStatusError as e:
            if attempt < max_api_retries - 1:
                wait = min(60, 2 ** (attempt + 1))
                print(
                    f"  API status error ({e.status_code}): {e}, retrying in {wait}s...",
                    flush=True,
                )
                time.sleep(wait)
            else:
                raise LLMCallError(
                    "api_status_error",
                    f"LLM API status error after {max_api_retries} attempts: status={e.status_code}, error={e}",
                ) from e

        except APIError as e:
            if attempt < max_api_retries - 1:
                wait = min(60, 2 ** (attempt + 1))
                print(f"  API error: {e}, retrying in {wait}s...", flush=True)
                time.sleep(wait)
            else:
                raise LLMCallError(
                    "api_error",
                    f"LLM API failed after {max_api_retries} attempts: {e}"
                ) from e

        except Exception as e:
            raise LLMCallError(
                "api_unknown_error",
                f"Unexpected LLM call error ({type(e).__name__}): {e}",
            ) from e

    raise LLMCallError("api_error", "LLM API failed: exhausted retries")