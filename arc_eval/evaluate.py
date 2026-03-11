"""Grid comparison and evaluation logic."""


def compare_grids(
    predicted: list[list[int]], expected: list[list[int]]
) -> dict:
    """Compare predicted and expected grids.

    Returns:
        {
            "correct": bool,        # pixel-perfect match
            "shape_match": bool,    # same dimensions
            "cell_accuracy": float, # fraction of cells correct (0.0 if shape mismatch)
            "predicted_shape": [rows, cols],
            "expected_shape": [rows, cols],
        }
    """
    pred_rows = len(predicted)
    pred_cols = len(predicted[0]) if pred_rows > 0 else 0
    exp_rows = len(expected)
    exp_cols = len(expected[0]) if exp_rows > 0 else 0

    result = {
        "predicted_shape": [pred_rows, pred_cols],
        "expected_shape": [exp_rows, exp_cols],
        "shape_match": pred_rows == exp_rows and pred_cols == exp_cols,
    }

    if not result["shape_match"]:
        result["correct"] = False
        result["cell_accuracy"] = 0.0
        return result

    total = exp_rows * exp_cols
    if total == 0:
        result["correct"] = True
        result["cell_accuracy"] = 1.0
        return result

    correct_cells = sum(
        predicted[r][c] == expected[r][c]
        for r in range(exp_rows)
        for c in range(exp_cols)
    )

    result["correct"] = correct_cells == total
    result["cell_accuracy"] = correct_cells / total
    return result


def verify_on_train(code: str, train_examples: list[dict], execute_fn, timeout: int) -> dict:
    """Run code against all training examples.

    Returns:
        {
            "passed": bool,
            "error_msg": str or None,  # error message for retry prompt
            "details": list of per-example results,
        }
    """
    from .prompt import format_grid

    details = []
    for i, ex in enumerate(train_examples, 1):
        result = execute_fn(code, ex["input"], timeout=timeout)
        if not result["success"]:
            return {
                "passed": False,
                "error_msg": f"Error on training example {i}:\n{result['error']}",
                "details": details,
            }

        cmp = compare_grids(result["output"], ex["output"])
        details.append(cmp)

        if not cmp["correct"]:
            msg_parts = [f"Wrong output for training example {i}:"]
            msg_parts.append(f"Expected:\n{format_grid(ex['output'])}")
            msg_parts.append(f"Got:\n{format_grid(result['output'])}")
            if not cmp["shape_match"]:
                msg_parts.append(
                    f"Shape mismatch: expected {cmp['expected_shape']}, "
                    f"got {cmp['predicted_shape']}"
                )
            else:
                msg_parts.append(f"Cell accuracy: {cmp['cell_accuracy']:.1%}")
            return {
                "passed": False,
                "error_msg": "\n".join(msg_parts),
                "details": details,
            }

    return {"passed": True, "error_msg": None, "details": details}
