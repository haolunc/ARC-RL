"""LLM API client using OpenAI SDK."""

import time
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

from .config import API_BASE_URL, API_KEY, MODEL, DEFAULT_TEMPERATURE

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def call_llm(
    messages: list[dict],
    temperature: float = DEFAULT_TEMPERATURE,
    model: str = MODEL,
    max_api_retries: int = 3,
) -> str:
    """Call the LLM endpoint and return the assistant's response text."""
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
