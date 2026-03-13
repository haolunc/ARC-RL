"""
Verifier: check predicted grids against ground truth,
provide structured feedback for retry, and compute scoring metrics.
"""

from __future__ import annotations

from .grid_utils import Grid, grids_equal, grid_diff, grid_to_str


def verify(predicted: Grid | None, expected: Grid) -> tuple[bool, str]:
    """
    Verify a predicted grid against the expected output.
    Returns (is_correct, feedback_message).
    """
    if predicted is None:
        return False, "Failed to parse a valid grid from the response."

    if len(predicted) != len(expected):
        return False, (
            f"Wrong number of rows: got {len(predicted)}, expected {len(expected)}. "
            f"The output grid should have exactly {len(expected)} rows."
        )

    for i, (pr, er) in enumerate(zip(predicted, expected)):
        if len(pr) != len(er):
            return False, (
                f"Row {i} has wrong width: got {len(pr)}, expected {len(er)}. "
                f"Each row should have exactly {len(er)} values."
            )

    if grids_equal(predicted, expected):
        return True, "Correct!"

    diffs = grid_diff(predicted, expected)
    total_cells = len(expected) * len(expected[0])
    accuracy = 1.0 - len(diffs) / total_cells

    diff_summary = []
    for r, c, got, want in diffs[:10]:
        diff_summary.append(f"  ({r},{c}): got {got}, expected {want}")
    if len(diffs) > 10:
        diff_summary.append(f"  ... and {len(diffs) - 10} more differences")

    feedback = (
        f"Grid dimensions are correct ({len(expected)}x{len(expected[0])}), "
        f"but {len(diffs)}/{total_cells} cells differ "
        f"(cell accuracy: {accuracy:.1%}).\n"
        f"Differences:\n" + "\n".join(diff_summary)
    )
    return False, feedback


def hamming_similarity(predicted: Grid | None, expected: Grid) -> float:
    """Partial credit: fraction of cells that match."""
    if predicted is None:
        return 0.0
    if len(predicted) != len(expected):
        return 0.0

    matches = 0
    total = 0
    for pr, er in zip(predicted, expected):
        if len(pr) != len(er):
            return 0.0
        for a, b in zip(pr, er):
            total += 1
            if a == b:
                matches += 1
    return matches / total if total > 0 else 0.0


def dimension_match(predicted: Grid | None, expected: Grid) -> bool:
    """Check if at least dimensions are correct."""
    if predicted is None:
        return False
    if len(predicted) != len(expected):
        return False
    return all(len(pr) == len(er) for pr, er in zip(predicted, expected))


def score_hypothesis(
    predicted: Grid | None,
    expected: Grid,
    prompt_length: int = 0,
    lambda_mdl: float = 0.001,
) -> dict:
    """
    Score a hypothesis with fit, partial credit, and MDL penalty.
    Returns a dict with all scoring components.
    """
    correct, feedback = verify(predicted, expected)
    sim = hamming_similarity(predicted, expected)
    dim_ok = dimension_match(predicted, expected)
    mdl_penalty = lambda_mdl * prompt_length

    return {
        "correct": correct,
        "hamming_similarity": round(sim, 4),
        "dimension_match": dim_ok,
        "mdl_penalty": round(mdl_penalty, 4),
        "score": round(sim - mdl_penalty, 4),
        "feedback": feedback,
    }
