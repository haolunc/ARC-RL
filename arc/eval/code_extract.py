"""Extract Python code from LLM responses."""

import re


def extract_thinking(text: str) -> tuple[str | None, str]:
    """Extract <think>...</think> content and return (thinking, stripped_text).

    Returns the thinking content separately for logging, and the text
    with thinking tags removed.
    """
    thinking_parts = re.findall(r"<think>(.*?)</think>", text, flags=re.DOTALL)
    thinking = "\n\n".join(thinking_parts).strip() if thinking_parts else None
    stripped = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return thinking, stripped


def extract_code(response: str) -> str | None:
    """Extract Python code containing test_transform (or transform) from an LLM response.

    Tries in order:
    1. ```python ... ``` code blocks with def test_transform (takes last)
    2. ```python ... ``` code blocks with def transform (takes last, renames to test_transform)
    3. ``` ... ``` code blocks (same priority)
    4. Raw function definition fallback

    Returns None if no valid code found.
    """
    _, text = extract_thinking(response)

    # Try ```python blocks — prefer test_transform, fallback to transform
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        code = matches[-1].strip()
        if "def test_transform" in code:
            return code
        if "def transform" in code:
            return code.replace("def transform", "def test_transform", 1)

    # Try generic ``` blocks
    matches = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        for m in reversed(matches):
            code = m.strip()
            if "def test_transform" in code:
                return code
            if "def transform" in code:
                return code.replace("def transform", "def test_transform", 1)

    # Fallback: find def test_transform or def transform in raw text
    for func_name in ("def test_transform", "def transform"):
        match = re.search(rf"({func_name}\b.*)", text, re.DOTALL)
        if match:
            code = match.group(1)
            lines = code.split("\n")
            func_lines = [lines[0]]
            for line in lines[1:]:
                if line and not line[0].isspace() and not line.startswith("#"):
                    break
                func_lines.append(line)
            code = "\n".join(func_lines).rstrip()
            if code:
                if "def transform(" in code and "def test_transform" not in code:
                    code = code.replace("def transform", "def test_transform", 1)
                return code

    return None
