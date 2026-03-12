"""Prompt construction for ARC tasks."""

SYSTEM_PROMPT = """\
You solve ARC tasks by writing Python code.

Write exactly one function:
def transform(input_grid: list[list[int]]) -> list[list[int]]

Rules:
- Use only Python standard library and numpy.
- Do not import any other libraries.
- Output only one ```python code block.
- Do not include explanations, test code, or print statements.
- The output grid size may differ from the input.
"""


def format_grid(grid: list[list[int]]) -> str:
    """Format a 2D grid as a readable string."""
    return "\n".join("[" + ", ".join(str(c) for c in row) + "]" for row in grid)


def build_initial_messages(
    train_examples: list[dict],
    test_input: list[list[int]],
) -> list[dict]:
    """Build the initial chat messages."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    parts = ["Training examples:\n"]
    for i, ex in enumerate(train_examples, 1):
        parts.append(f"Example {i}:")
        parts.append(f"Input:\n{format_grid(ex['input'])}")
        parts.append(f"Output:\n{format_grid(ex['output'])}\n")

    parts.append("Infer the rule from the training examples.")
    parts.append("Write a correct Python function `transform(input_grid)`.")
    parts.append(f"Test input:\n{format_grid(test_input)}")

    messages.append({"role": "user", "content": "\n".join(parts)})
    return messages


def append_retry(
    messages: list[dict],
    llm_response: str,
    error_msg: str,
) -> list[dict]:
    """Append a failed attempt and feedback, keeping context compact.

    Keeps:
    - original system prompt
    - original task prompt
    - most recent assistant response
    - latest retry instruction
    """
    system_msg = messages[0]
    initial_user_msg = messages[1]

    compact_response = llm_response
    if len(compact_response) > 4000:
        compact_response = compact_response[:4000] + "\n... (truncated)"

    compact_error = error_msg
    if len(compact_error) > 2000:
        compact_error = compact_error[:2000] + "\n... (truncated)"

    retry_user_msg = {
        "role": "user",
        "content": (
            "Your previous code was incorrect.\n\n"
            f"Feedback:\n{compact_error}\n\n"
            "Write a corrected `transform(input_grid)` function."
        ),
    }

    assistant_msg = {"role": "assistant", "content": compact_response}

    return [system_msg, initial_user_msg, assistant_msg, retry_user_msg]