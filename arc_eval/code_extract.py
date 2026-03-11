"""Extract Python code from LLM responses."""

import re


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> tags from Qwen responses."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def extract_code(response: str) -> str | None:
    """Extract Python code from an LLM response."""

    text = strip_thinking(response)

    # Try ```python blocks
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        code = matches[-1].strip()
        if "def solve" in code or "def transform" in code:
            return code

    # Try generic ``` blocks
    matches = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if matches:
        for m in reversed(matches):
            code = m.strip()
            if "def solve" in code or "def transform" in code:
                return code

    # Fallback search
    match = re.search(r"(def (solve|transform)\b.*)", text, re.DOTALL)
    if match:
        code = match.group(1)

        lines = code.split("\n")
        func_lines = [lines[0]]

        for line in lines[1:]:
            if line and not line[0].isspace() and not line.startswith("#"):
                break
            func_lines.append(line)

        return "\n".join(func_lines).rstrip()

    return None