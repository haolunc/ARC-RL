"""Prompt construction for ARC tasks."""

_BASE_PROMPT = """\
You are an expert puzzle solver and Python programmer specializing in ARC (Abstraction and Reasoning Corpus) tasks.

Each task shows input/output grid examples. Grids are 2D matrices of integers 0-9, where each integer represents a color:
0=black, 1=blue, 2=red, 3=green, 4=yellow, 5=gray, 6=magenta, 7=orange, 8=azure, 9=maroon.

Your goal: study the training examples, discover the transformation rule, and write a Python function `test_transform(input_grid)` that implements it.

Approach:
- Write code to analyze patterns in training examples (e.g., convolution-like operations, spatial relationship detection, color frequency analysis, symmetry checks).
- Observe regularities within inputs, within outputs, and between input-output pairs.
- The function must work on unseen test inputs.

Rules:
- Function signature: def test_transform(input_grid: list[list[int]]) -> list[list[int]]
- You may use only the Python standard library and numpy.
- The output grid dimensions may differ from the input."""

NATIVE_TOOLS_PROMPT = _BASE_PROMPT + """

You have a code interpreter with a limited number of calls. Use it efficiently:
- Combine multiple analyses into a single code block instead of splitting across many calls.
- Double-check variable names and code correctness before running — wasted calls cannot be recovered.
- If code execution fails, do NOT retry the same approach. Fall back to reasoning in text.
Run code to explore shapes, colors, spatial patterns, and transformations in the examples.
When you are confident in the rule, output your final `test_transform` function in a ```python code block."""

SANDBOX_TOOLS_PROMPT = _BASE_PROMPT + """

You can call the `python` tool to execute code and analyze grids.
Pre-loaded variables:
- `train_inputs`: list of input grids (each grid is list[list[int]])
- `train_outputs`: list of output grids
- `test_inputs`: list of test input grids
- numpy is available as `np`

Use `print()` to see results. Run code to explore shapes, colors, spatial patterns, and transformations.
When you are confident in the rule, output your final `test_transform` function in a ```python code block."""

DIRECT_PROMPT = _BASE_PROMPT + """
- Do NOT import any other libraries.
- Output the function inside a single ```python code block.
- Do NOT include test code, example calls, or print statements outside the function."""


def format_grid(grid: list[list[int]]) -> str:
    """Format a 2D grid as a readable string."""
    return "\n".join("[" + ", ".join(str(c) for c in row) + "]" for row in grid)


def _format_training_examples(train_examples):
    parts = []
    for i, ex in enumerate(train_examples, 1):
        parts.append(f"Example {i}:")
        parts.append(f"Input:\n{format_grid(ex['input'])}\n")
        parts.append(f"Output:\n{format_grid(ex['output'])}\n")
    return parts


def build_messages(
    mode: str,
    train_examples: list[dict],
    test_inputs: list[list[list[int]]],
) -> list[dict]:
    """Build the input list for the Responses API.

    Returns a list of message dicts with roles "developer" and "user".
    """
    system_prompt = {
        "native_tools": NATIVE_TOOLS_PROMPT,
        "sandbox_tools": SANDBOX_TOOLS_PROMPT,
        "direct": DIRECT_PROMPT,
    }[mode]

    parts = ["Here are the training examples:\n"]
    parts.extend(_format_training_examples(train_examples))

    parts.append(
        "Study the pattern across all examples. "
        "Think step by step about what transformation rule maps each input to its output. "
        "Then write a Python function `test_transform(input_grid)` that implements this rule.\n"
    )

    if len(test_inputs) == 1:
        parts.append(f"The function will be tested on this input:\n{format_grid(test_inputs[0])}")
    else:
        parts.append("The function will be tested on these inputs:")
        for i, test_input in enumerate(test_inputs, 1):
            parts.append(f"\nTest input {i}:\n{format_grid(test_input)}")

    return [
        {"role": "developer", "content": system_prompt},
        {"role": "user", "content": "\n".join(parts)},
    ]
