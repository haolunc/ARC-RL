"""Extract Python code from LLM responses."""

import re


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> tags from Qwen3 responses."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def extract_code(response: str) -> str | None:
    """Extract Python code from an LLM response.

    Tries in order:
    1. ```python ... ``` code blocks (takes the last one)
    2. ``` ... ``` code blocks
    3. Raw function definition fallback

    Returns None if no valid code found.
    """
    text = strip_thinking(response)

    # Try ```python blocks
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        code = matches[-1].strip()
        if "def transform" in code:
            return code

    # Try generic ``` blocks
    matches = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        for m in reversed(matches):
            code = m.strip()
            if "def transform" in code:
                return code

    # Fallback: find def transform in raw text
    match = re.search(r"(def transform\b.*)", text, re.DOTALL)
    if match:
        code = match.group(1)
        # Try to find the end of the function (next top-level definition or end)
        lines = code.split("\n")
        func_lines = [lines[0]]
        for line in lines[1:]:
            # Stop at next top-level definition or empty-ish end
            if line and not line[0].isspace() and not line.startswith("#"):
                break
            func_lines.append(line)
        code = "\n".join(func_lines).rstrip()
        if code:
            return code

    return None
