"""
LLM-based hypothesis synthesiser with role-aware structured prompts.

Instead of feeding raw grids, we provide the LLM with:
  1. Object-level decomposition (what objects exist, their properties)
  2. Role assignments (which objects correspond across examples)
  3. Transformation descriptions (what changed from input to output)
  4. The raw grids as backup context

The LLM then reasons about the abstract rule and produces the output grid.
"""

from __future__ import annotations

import os
import re

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from .grid_utils import Grid, grid_to_str, describe_objects
from .role_inducer import TaskAnalysis, ExampleAnalysis

load_dotenv()

REQUEST_TIMEOUT = httpx.Timeout(180.0, connect=30.0)

COLOR_NAMES = {
    0: "black", 1: "blue", 2: "red", 3: "green", 4: "yellow",
    5: "grey", 6: "magenta", 7: "orange", 8: "cyan", 9: "maroon",
}


def get_client(model_key: str = "qwen") -> tuple[OpenAI, str]:
    configs = {
        "qwen": {
            "base_url": os.getenv("QWEN_API_BASE"),
            "api_key": os.getenv("QWEN_API_KEY"),
            "model": os.getenv("QWEN_MODEL"),
        },
        "gpt": {
            "base_url": os.getenv("GPT_API_BASE"),
            "api_key": os.getenv("GPT_API_KEY"),
            "model": os.getenv("GPT_MODEL"),
        },
    }
    cfg = configs[model_key]
    return OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"], timeout=REQUEST_TIMEOUT), cfg["model"]


def _describe_example(ex: ExampleAnalysis, include_grid: bool = True, max_objects: int = 15) -> str:
    """Build a structured description of one demonstration example."""
    parts = []

    in_h, in_w = len(ex.input_grid), len(ex.input_grid[0])
    out_h, out_w = len(ex.output_grid), len(ex.output_grid[0])

    parts.append(f"Input grid ({in_h}x{in_w}):")
    if include_grid:
        parts.append(grid_to_str(ex.input_grid))

    in_objs = ex.input_objects[:max_objects]
    parts.append(f"\nInput objects ({len(ex.input_objects)} total, showing {len(in_objs)}):")
    parts.append(describe_objects(in_objs))

    parts.append(f"\nInput object roles:")
    for ro in ex.input_roles[:max_objects]:
        tag = ro.role_tag or "unassigned"
        parts.append(f"  Object #{ro.obj.obj_id} -> Role {tag}")

    parts.append(f"\nOutput grid ({out_h}x{out_w}):")
    if include_grid:
        parts.append(grid_to_str(ex.output_grid))

    out_objs = ex.output_objects[:max_objects]
    parts.append(f"\nOutput objects ({len(ex.output_objects)} total, showing {len(out_objs)}):")
    parts.append(describe_objects(out_objs))

    parts.append("\nTransformations:")
    for ro in ex.input_roles[:max_objects]:
        if ro.transform:
            tag = ro.role_tag or f"#{ro.obj.obj_id}"
            cn = COLOR_NAMES.get(ro.obj.color, str(ro.obj.color))
            parts.append(f"  Role {tag} ({cn}): {ro.transform}")

    return "\n".join(parts)


def build_role_aware_prompt(
    analysis: TaskAnalysis,
    test_input: Grid,
    test_input_objects_desc: str,
) -> str:
    """Build the full structured prompt for the LLM."""
    sections = []

    sections.append(
        "You are solving an ARC (Abstraction and Reasoning Corpus) puzzle.\n"
        "Each puzzle has demonstration input-output pairs that reveal a hidden "
        "transformation rule. I have pre-analyzed the grids into objects and assigned "
        "ROLES to objects that play analogous structural positions across examples.\n"
        "Your task:\n"
        "1. Study the examples, objects, roles, and transformations carefully.\n"
        "2. Identify the abstract rule that maps input to output.\n"
        "3. Apply that rule to the test input.\n"
        "4. Reply with ONLY the output grid: one row per line, values separated by spaces.\n"
        "   Do NOT include any explanation or extra text."
    )

    if analysis.global_pattern:
        sections.append(f"\n=== Global Pattern Summary ===\n{analysis.global_pattern}")

    for ex in analysis.examples:
        sections.append(f"\n=== Demonstration {ex.idx + 1} ===")
        sections.append(_describe_example(ex))

    test_h, test_w = len(test_input), len(test_input[0])
    sections.append("\n=== Test ===")
    sections.append(f"Input grid ({test_h}x{test_w}):")
    sections.append(grid_to_str(test_input))
    sections.append(f"\nTest input objects:")
    sections.append(test_input_objects_desc)
    sections.append("\nOutput:")

    return "\n".join(sections)


def build_verification_retry_prompt(
    original_prompt: str,
    previous_answer: str,
    feedback: str,
) -> str:
    """Build a retry prompt incorporating verification feedback."""
    return (
        f"{original_prompt}\n\n"
        f"--- PREVIOUS ATTEMPT ---\n"
        f"Your previous answer:\n{previous_answer}\n\n"
        f"Feedback: {feedback}\n\n"
        f"Please try again. Output ONLY the corrected grid, "
        f"one row per line, values separated by spaces."
    )


def call_llm(
    client: OpenAI,
    model: str,
    prompt: str,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> str:
    """Call the LLM and return raw text response."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def parse_grid_response(text: str) -> Grid | None:
    """Extract a 2D integer grid from the model's response."""
    lines = text.strip().splitlines()
    grid: Grid = []
    for line in lines:
        nums = re.findall(r"\d+", line)
        if nums:
            grid.append([int(n) for n in nums])
    return grid if grid else None
