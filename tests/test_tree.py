"""Tests for tree search — PUCT selection, scoring, and full tree search."""

import json
import math
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from arc.eval.tree import (
    TreeNode,
    TreeSearch,
    score_on_training,
    _puct_score,
    _select,
    _backpropagate,
    _collect_scores,
)
from arc.eval.prompt import build_refinement_message
from arc.eval.llm import LLMResult


# ── PUCT score ──────────────────────────────────────────────────────────

def test_puct_score_basic():
    child = TreeNode(id=1, parent=None, value=0.5, visit_count=3)
    parent_visits = 10
    c_puct = 1.4
    expected = 0.5 + 1.4 * math.sqrt(math.log(10)) / (1 + 3)
    assert abs(_puct_score(child, parent_visits, c_puct) - expected) < 1e-9


def test_puct_score_unvisited_child():
    child = TreeNode(id=1, parent=None, value=0.0, visit_count=0)
    score = _puct_score(child, parent_visits=5, c_puct=1.4)
    # Unvisited child: denominator = 1, so exploration is large
    assert score > 1.0


def test_puct_score_zero_parent_visits():
    child = TreeNode(id=1, parent=None, value=0.5, visit_count=2)
    score = _puct_score(child, parent_visits=0, c_puct=1.4)
    assert score == float("inf")


# ── Selection ───────────────────────────────────────────────────────────

def test_select_forces_min_children():
    root = TreeNode(id=0, parent=None, depth=0)
    root.children = [TreeNode(id=1, parent=root, depth=1, score=0.5)]
    result = _select(root, min_children=3, max_depth=3, c_puct=1.4)
    assert result is root


def test_select_returns_best_leaf():
    root = TreeNode(id=0, parent=None, depth=0, visit_count=10)
    c1 = TreeNode(id=1, parent=root, depth=1, value=0.9, visit_count=5)
    c2 = TreeNode(id=2, parent=root, depth=1, value=0.2, visit_count=5)
    root.children = [c1, c2]
    result = _select(root, min_children=2, max_depth=3, c_puct=1.4)
    assert result is c1


def test_select_skips_terminal():
    root = TreeNode(id=0, parent=None, depth=0, visit_count=10)
    c1 = TreeNode(id=1, parent=root, depth=1, value=0.9, visit_count=5, terminal=True)
    c2 = TreeNode(id=2, parent=root, depth=1, value=0.2, visit_count=5)
    root.children = [c1, c2]
    result = _select(root, min_children=2, max_depth=3, c_puct=1.4)
    assert result is c2


def test_select_respects_max_depth():
    root = TreeNode(id=0, parent=None, depth=0, visit_count=10)
    c1 = TreeNode(id=1, parent=root, depth=1, value=0.9, visit_count=5)
    c1_1 = TreeNode(id=2, parent=c1, depth=2, value=0.8, visit_count=3)
    c1.children = [c1_1]
    root.children = [c1]
    # max_depth=2, so c1_1 at depth 2 should be returned (not traversed further)
    result = _select(root, min_children=1, max_depth=2, c_puct=1.4)
    assert result is c1_1


# ── Backpropagation ─────────────────────────────────────────────────────

def test_backpropagate_updates_ancestors():
    root = TreeNode(id=0, parent=None, depth=0)
    child = TreeNode(id=1, parent=root, depth=1, code="x", score=0.8)
    root.children = [child]

    _backpropagate(child)

    assert child.visit_count == 1
    assert root.visit_count == 1
    assert abs(root.value - 0.8) < 1e-9


def test_backpropagate_multiple_children():
    root = TreeNode(id=0, parent=None, depth=0)
    c1 = TreeNode(id=1, parent=root, depth=1, code="x", score=0.6)
    c2 = TreeNode(id=2, parent=root, depth=1, code="y", score=0.8)
    root.children = [c1, c2]

    _backpropagate(c1)
    _backpropagate(c2)

    assert root.visit_count == 2
    assert abs(root.value - 0.7) < 1e-9  # mean of 0.6 and 0.8


# ── score_on_training ───────────────────────────────────────────────────

def test_score_on_training_none_code(python_path):
    score, details = score_on_training(None, [{"input": [[1]], "output": [[1]]}], python_path)
    assert score == 0.0


def test_score_on_training_correct(python_path):
    code = "def test_transform(grid): return grid"
    examples = [{"input": [[1, 2], [3, 4]], "output": [[1, 2], [3, 4]]}]
    score, details = score_on_training(code, examples, python_path)
    assert score == 1.0
    assert details[0]["correct"] is True


def test_score_on_training_wrong(python_path):
    code = "def test_transform(grid): return [[0]*len(grid[0]) for _ in grid]"
    examples = [{"input": [[1, 2], [3, 4]], "output": [[1, 2], [3, 4]]}]
    score, details = score_on_training(code, examples, python_path)
    assert score == 0.0
    assert details[0]["correct"] is False


def test_score_on_training_broken_code(python_path):
    code = "def test_transform(grid): raise ValueError('broken')"
    examples = [{"input": [[1]], "output": [[1]]}]
    score, details = score_on_training(code, examples, python_path)
    assert score == 0.0


# ── build_refinement_message ────────────────────────────────────────────

def test_build_refinement_message_includes_code():
    msg = build_refinement_message(
        parent_code="def test_transform(g): return g",
        parent_score=0.5,
        train_details=[
            {"correct": True, "cell_accuracy": 1.0},
            {"correct": False, "cell_accuracy": 0.3, "error": None,
             "predicted_shape": (2, 2), "expected_shape": (2, 2)},
        ],
        train_examples=[{"input": [[1]], "output": [[1]]}, {"input": [[2]], "output": [[3]]}],
    )
    assert msg["role"] == "user"
    assert "50%" in msg["content"]
    assert "def test_transform" in msg["content"]
    assert "Example 2" in msg["content"]


def test_build_refinement_message_shape_mismatch():
    msg = build_refinement_message(
        parent_code="def test_transform(g): return g",
        parent_score=0.0,
        train_details=[
            {"correct": False, "cell_accuracy": 0.0, "error": None,
             "predicted_shape": (2, 2), "expected_shape": (3, 3)},
        ],
        train_examples=[{"input": [[1]], "output": [[1]]}],
    )
    assert "shape mismatch" in msg["content"]


# ── Full tree search (mocked LLM) ──────────────────────────────────────

def _make_llm_result(code_str):
    text = f"```python\n{code_str}\n```"
    return LLMResult(
        text=text,
        extracted_code=code_str if "def test_transform" in code_str else None,
        usage={"input": 100, "output": 50, "reasoning": 0, "cached": 0},
        tool_rounds=1,
        raw_responses=[],
    )


def test_tree_search_mocked_early_stop(python_path, puzzle_8d5021e8, tmp_path):
    """Tree search with mocked LLM that returns identity transform.

    puzzle_8d5021e8 may not be identity, but we test the flow.
    """
    cfg = {
        "python_path": python_path,
        "endpoint": {"model": "mock", "base_url": "http://x", "api_key": "x"},
        "eval": {
            "mode": "tree_search",
            "tree_search": {
                "max_nodes": 4,
                "max_depth": 2,
                "min_children": 2,
                "exploration_weight": 1.4,
                "early_stop": True,
                "max_output_tokens": 8192,
                "max_tool_rounds": 4,
                "token_budget": 60000,
            },
        },
    }

    identity_code = "def test_transform(grid): return grid"
    mock_result = _make_llm_result(identity_code)

    with patch("arc.eval.tree.call_llm", return_value=mock_result):
        tree = TreeSearch("mock_task", puzzle_8d5021e8, None, cfg, None)
        best = tree.run()

    # Should have explored at least min_children nodes
    assert len(tree.all_nodes) >= 3  # root + 2 fresh attempts
    assert best is not None
    assert "def test_transform" in best


# ── API test ────────────────────────────────────────────────────────────

_API_OUTPUT_DIR = Path(__file__).parent / "api_output"


@pytest.mark.api
def test_tree_search_full(qwen_client, cfg, puzzle_8d5021e8, tmp_path):
    """Full tree search with live API. Run with -s to see printed output."""
    from arc.eval.db import ResultDB, LogDB
    from arc.eval.run import evaluate_single_task

    tree_cfg = {
        **cfg,
        "eval": {
            **cfg["eval"],
            "mode": "tree_search",
            "tree_search": {
                "max_nodes": 4,
                "max_depth": 2,
                "min_children": 2,
                "exploration_weight": 1.4,
                "early_stop": True,
                "max_output_tokens": 8192,
                "max_tool_rounds": 4,
                "token_budget": 60000,
            },
        },
    }

    db = ResultDB(tmp_path / "results.db")
    log_db = LogDB(tmp_path / "logs.db")

    result = evaluate_single_task(
        "8d5021e8", puzzle_8d5021e8, qwen_client, tree_cfg, db, log_db,
    )

    # Save output for inspection
    _API_OUTPUT_DIR.mkdir(exist_ok=True)
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = _API_OUTPUT_DIR / f"tree_search_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"Tree search result saved to {out_path}")
    print(f"Status: {result['status']}")
    print(f"Token usage: {result['token_usage']}")
    print(f"Tool rounds: {result['tool_rounds']}")
    if result.get("extracted_code"):
        print(f"Code:\n{result['extracted_code'][:500]}")
    print(f"{'='*60}")

    assert result["status"] in ("success", "wrong_answer", "error_extract", "error_exec")
    assert db.get_completed_task_ids() == {"8d5021e8"}
