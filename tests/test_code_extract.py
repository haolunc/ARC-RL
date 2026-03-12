"""Tests for arc.eval.code_extract."""

from arc.eval.code_extract import extract_thinking, strip_thinking, extract_code
from .conftest import load_solution


# --- extract_thinking ---

def test_extract_thinking_basic():
    text = "<think>reasoning here</think> answer"
    thinking, stripped = extract_thinking(text)
    assert thinking == "reasoning here"
    assert stripped == "answer"


def test_extract_thinking_multiple():
    text = "<think>part1</think> middle <think>part2</think> end"
    thinking, stripped = extract_thinking(text)
    assert "part1" in thinking
    assert "part2" in thinking
    assert "<think>" not in stripped
    assert stripped == "middle  end"


def test_extract_thinking_none():
    text = "no thinking tags here"
    thinking, stripped = extract_thinking(text)
    assert thinking is None
    assert stripped == text


def test_extract_thinking_multiline():
    text = "<think>\nline1\nline2\n</think>\nresult"
    thinking, stripped = extract_thinking(text)
    assert "line1" in thinking
    assert "line2" in thinking
    assert stripped == "result"


# --- strip_thinking ---

def test_strip_thinking():
    text = "<think>remove me</think> keep this"
    assert strip_thinking(text) == "keep this"


def test_strip_thinking_no_tags():
    text = "nothing to strip"
    assert strip_thinking(text) == text


# --- extract_code ---

def test_extract_code_python_block():
    text = "Here's the code:\n```python\ndef transform(grid):\n    return grid\n```"
    code = extract_code(text)
    assert code is not None
    assert "def transform" in code
    assert "return grid" in code


def test_extract_code_generic_block():
    text = "Here:\n```\ndef transform(grid):\n    return grid[::-1]\n```"
    code = extract_code(text)
    assert code is not None
    assert "def transform" in code


def test_extract_code_multiple_blocks_takes_last():
    text = (
        "First attempt:\n```python\ndef transform(grid):\n    return grid\n```\n"
        "Better version:\n```python\ndef transform(grid):\n    return grid[::-1]\n```"
    )
    code = extract_code(text)
    assert code is not None
    assert "grid[::-1]" in code


def test_extract_code_raw_fallback():
    text = "def transform(grid):\n    return [[0]]\n\nSome trailing text."
    code = extract_code(text)
    assert code is not None
    assert "def transform" in code
    assert "return [[0]]" in code
    assert "trailing text" not in code


def test_extract_code_no_transform():
    text = "```python\ndef helper(x):\n    return x + 1\n```"
    assert extract_code(text) is None


def test_extract_code_returns_none_for_empty():
    assert extract_code("no code here at all") is None


def test_extract_code_with_thinking():
    text = (
        "<think>Let me think about this...</think>\n"
        "```python\ndef transform(grid):\n    return grid\n```"
    )
    code = extract_code(text)
    assert code is not None
    assert "def transform" in code
    assert "<think>" not in code


def test_extract_code_real_solution():
    """Wrap a real reference solution in markdown and verify extraction."""
    solution = load_solution("007bbfb7")
    wrapped = f"Here is the solution:\n```python\n{solution}\n```"
    code = extract_code(wrapped)
    assert code is not None
    assert "def transform" in code
    # Extracted code should be functionally the same
    assert "grid[br][bc]" in code or "grid[i][j]" in code
