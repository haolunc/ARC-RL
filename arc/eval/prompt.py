"""Prompt construction for ARC tasks."""

SYSTEM_PROMPT = """\
You are an expert puzzle solver and Python programmer specializing in ARC (Abstraction and Reasoning Corpus) tasks.

Each task shows input/output grid examples. Grids are 2D matrices of integers 0-9, where each integer represents a color:
0=black, 1=blue, 2=red, 3=green, 4=yellow, 5=gray, 6=magenta, 7=orange, 8=azure, 9=maroon.

Your job: study the training examples, discover the transformation rule, then write a Python function that implements it.

Rules:
- Write a function: def transform(input_grid: list[list[int]]) -> list[list[int]]
- You may use only the Python standard library and numpy.
- Do NOT import any other libraries.
- Output the function inside a single ```python code block.
- Do NOT include test code, example calls, or print statements outside the function.
- The output grid dimensions may differ from the input."""


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


def build_initial_messages(
    train_examples: list[dict],
    test_input: list[list[int]],
) -> list[dict]:
    """Build the initial chat messages (system + first user prompt).

    Returns a list of message dicts that forms the conversation start.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    parts = ["Here are the training examples:\n"]
    parts.extend(_format_training_examples(train_examples))

    parts.append(
        "Study the pattern across all examples. "
        "Think step by step about what transformation rule maps each input to its output. "
        "Then write a Python function `transform(input_grid)` that implements this rule.\n"
    )
    parts.append(f"The function will be tested on this input:\n{format_grid(test_input)}")

    messages.append({"role": "user", "content": "\n".join(parts)})
    return messages


AGENTIC_SYSTEM_PROMPT = """\
You are an expert puzzle solver and Python programmer specializing in ARC (Abstraction and Reasoning Corpus) tasks.

Each task shows input/output grid examples. Grids are 2D matrices of integers 0-9, where each integer represents a color:
0=black, 1=blue, 2=red, 3=green, 4=yellow, 5=gray, 6=magenta, 7=orange, 8=azure, 9=maroon.

Your job: study the training examples, discover the transformation rule, then write and submit a Python function that implements it.

You have 3 tools available:

1. **run_python(code)** — Execute arbitrary Python code to analyze grids. Pre-loaded variables:
   - `train_inputs`: list of input grids
   - `train_outputs`: list of output grids
   - `test_input`: the test input grid
   - numpy is available as `np`
   - Use `print()` to see results

2. **test_transform(code)** — Test a `def transform(input_grid)` function on ALL training examples. Shows detailed pass/fail results per example.

3. **submit_transform(code)** — Submit your final `def transform(input_grid)` function for test evaluation. Returns only pass/fail (no expected output shown). Use this when confident.

**Recommended workflow:**
1. Use `run_python` to analyze grid shapes, colors, patterns, and differences between inputs and outputs.
2. Formulate a hypothesis about the transformation rule.
3. Write a `transform` function and test it with `test_transform`.
4. Iterate and fix until all training examples pass.
5. Submit with `submit_transform` when ready.

Rules for your transform function:
- Signature: `def transform(input_grid: list[list[int]]) -> list[list[int]]`
- You may use only the Python standard library and numpy.
- The output grid dimensions may differ from the input."""


def build_agentic_messages(
    train_examples: list[dict],
    test_input: list[list[int]],
) -> list[dict]:
    """Build initial messages for agentic mode (system + user with grid data)."""
    messages = [{"role": "system", "content": AGENTIC_SYSTEM_PROMPT}]

    parts = ["Here are the training examples:\n"]
    parts.extend(_format_training_examples(train_examples))

    parts.append(f"Test input:\n{format_grid(test_input)}")
    parts.append(
        "\nAnalyze the patterns, write a transform function, test it, and submit when ready."
    )

    messages.append({"role": "user", "content": "\n".join(parts)})
    return messages


def append_retry(
    messages: list[dict],
    llm_response: str,
    error_msg: str,
) -> list[dict]:
    """Append a failed attempt and error feedback to the conversation.

    This keeps the FULL history so the LLM sees all previous attempts.
    Returns a new list (does not mutate the input).
    """
    new_messages = list(messages)
    new_messages.append({"role": "assistant", "content": llm_response})
    new_messages.append({
        "role": "user",
        "content": (
            "Your previous code did not produce the correct output. "
            f"Here is the feedback:\n\n{error_msg}\n\n"
            "Please analyze what went wrong and write a corrected `transform` function."
        ),
    })
    return new_messages
