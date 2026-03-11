"""LLM API client using OpenAI SDK."""

import time
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

from .config import (
    API_BASE_URL,
    API_KEY,
    MODEL,
    DEFAULT_TEMPERATURE,
)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
    timeout=120.0,   # more realistic for 30B
)


def call_llm(
    messages: list[dict],
    temperature: float = DEFAULT_TEMPERATURE,
    model: str = MODEL,
    max_api_retries: int = 2,
    max_tokens: int = 400,
) -> str:
    """Call the LLM endpoint and return the assistant's response text."""
    for attempt in range(max_api_retries):
        try:
            start = time.time()

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            elapsed = time.time() - start
            print(f"  API call finished in {elapsed:.2f}s")

            content = response.choices[0].message.content
            if content is None:
                raise RuntimeError("LLM response content is None")

            return content

        except RateLimitError:
            wait = 2 ** (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)

        except APITimeoutError as e:
            if attempt < max_api_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  API timeout: {e}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"LLM API timed out after {max_api_retries} attempts: {e}"
                ) from e

        except APIError as e:
            if attempt < max_api_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  API error: {e}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"LLM API failed after {max_api_retries} attempts: {e}"
                ) from e

    raise RuntimeError("LLM API failed: exhausted retries")