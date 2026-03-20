"""Tests for arc.eval.run — task loading, evaluation, and pipeline."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from arc.eval.run import load_tasks, evaluate_single_task
from arc.eval.db import ResultDB
from arc.eval.llm import LLMResult


_TRAINING_DIR = str(Path(__file__).parent.parent / "ARC-AGI-2" / "data" / "training")


def test_load_tasks():
    tasks = load_tasks(_TRAINING_DIR)
    assert isinstance(tasks, dict)
    assert "992798f6" in tasks
    assert "8d5021e8" in tasks
    task = tasks["8d5021e8"]
    assert "train" in task and "test" in task
    assert isinstance(task["train"], list)
    assert isinstance(task["test"], list)
    assert "input" in task["train"][0] and "output" in task["train"][0]


def test_load_tasks_count():
    tasks = load_tasks(_TRAINING_DIR)
    assert len(tasks) == 1000


@pytest.mark.api
def test_evaluate_single_task_success(qwen_client, cfg, puzzle_8d5021e8, tmp_path):
    cfg_direct = {**cfg, "eval": {**cfg["eval"], "mode": "direct"}}
    db = ResultDB(tmp_path / "results.db")
    result = evaluate_single_task(
        "8d5021e8", puzzle_8d5021e8, qwen_client, cfg_direct, db, "test_run",
    )
    assert result["status"] in ("success", "wrong_answer", "error_extract")
    assert db.get_completed_task_ids("test_run") == {"8d5021e8"}


def test_evaluate_single_task_error_extract(cfg, puzzle_8d5021e8, tmp_path):
    mock_result = LLMResult(text="no code here at all", usage={"input": 10, "output": 5, "reasoning": 0, "cached": 0}, tool_rounds=0)
    db = ResultDB(tmp_path / "results.db")
    with patch("arc.eval.run.call_llm", return_value=mock_result):
        result = evaluate_single_task(
            "8d5021e8", puzzle_8d5021e8, None, cfg, db, "test_run",
        )
    assert result["status"] == "error_extract"
    assert db.get_completed_task_ids("test_run") == {"8d5021e8"}


def test_evaluate_single_task_error_llm(cfg, puzzle_8d5021e8, tmp_path):
    db = ResultDB(tmp_path / "results.db")
    with patch("arc.eval.run.call_llm", side_effect=RuntimeError("API down")):
        result = evaluate_single_task(
            "8d5021e8", puzzle_8d5021e8, None, cfg, db, "test_run",
        )
    assert result["status"] == "error_llm"
    assert "API down" in result["error_message"]
    assert db.get_completed_task_ids("test_run") == {"8d5021e8"}
