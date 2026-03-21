"""Prompt constants and message building for ARC evaluation."""


_BASE_PROMPT = """\
You are an expert puzzle solver and Python programmer specializing in ARC (Abstraction and Reasoning Corpus) tasks.

Each task shows input/output grid examples. Grids are 2D matrices of integers 0-9, where each integer represents a color:
0=black, 1=blue, 2=red, 3=green, 4=yellow, 5=gray, 6=magenta, 7=orange, 8=azure, 9=maroon.

Your goal: study the training examples, discover the transformation rule, and write a Python function `test_transform(input_grid)` that implements it.

Approach:
- Write code to analyze patterns in training examples.
- Observe regularities within inputs, within outputs, and between input-output pairs.
- The function must work on unseen test inputs.

Rules:
- Function signature: def test_transform(input_grid: list[list[int]]) -> list[list[int]]
- You may use only the Python standard library and numpy. Do NOT import any other libraries.
- The output grid dimensions may differ from the input."""

SANDBOX_TOOLS_INSTRUCTION = _BASE_PROMPT + """
You have access to a Python code interpreter. \
You are encouraged to write Python code to explore and verify your ideas — \
for example: convolution-like operations, spatial relationship detection, \
color frequency analysis, symmetry checks, etc. \
Don't just think — actively write code to experiment.
You have a limited number of calls. Use them efficiently:
- Combine multiple analyses into a single code block instead of splitting across many calls.
- Double-check variable names and code correctness before running — wasted calls cannot be recovered.
When you are confident in the rule, output your final `test_transform` function in a ```python code block."""

DIRECT_INSTRUCTION = _BASE_PROMPT + """
- Output the function inside a single ```python code block.
- Do NOT include test code, example calls, or print statements outside the function."""

TOOL_CALL_WARNING = (
    "You have {remaining} tool call rounds remaining. "
    "Please finalize your answer soon."
)

TOOL_CALL_FINAL = (
    "CRITICAL: This is your FINAL round. You MUST NOT make any more tool calls — "
    "any tool call will be rejected. Output your final `test_transform` function "
    "now in a ```python code block. If you are unsure, provide your best attempt."
)


def format_grid(grid: list[list[int]]) -> str:
    """Format a 2D grid as a readable string."""
    return "\n".join("[" + ", ".join(str(c) for c in row) + "]" for row in grid)


def build_messages(
    train_examples: list[dict],
    test_inputs: list[list[list[int]]],
) -> list[dict]:
    """Build the initial user message with training examples and test inputs."""
    parts = ["Here are the training examples:\n"]

    for i, ex in enumerate(train_examples, 1):
        parts.append(f"Example {i}:")
        parts.append(f"Input:\n{format_grid(ex['input'])}\n")
        parts.append(f"Output:\n{format_grid(ex['output'])}\n")

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

    return [{"role": "user", "content": "\n".join(parts)}]
