"""Tests for arc.eval.db — SQLite result database."""

import json
import sqlite3

from arc.eval.db import ResultDB


def _make_result(**overrides):
    base = {
        "run_name": "test_run",
        "task_id": "992798f6",
        "mode": "direct",
        "endpoint_name": "qwen_official",
        "status": "success",
        "raw_response": "Here is a solution...",
        "extracted_code": "def test_transform(g): return g",
        "test_passed": 1,
        "test_total": 1,
        "correct": 1,
        "token_usage": json.dumps({"input": 100, "output": 50, "reasoning": 30, "cached": 10}),
        "tool_rounds": 0,
        "duration_s": 2.5,
        "error_message": None,
    }
    base.update(overrides)
    return base


def test_init_creates_table(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    conn = sqlite3.connect(tmp_path / "results.db")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
    assert cursor.fetchone() is not None

    cursor = conn.execute("PRAGMA table_info(results)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {
        "run_name", "task_id", "mode", "endpoint_name", "status",
        "raw_response", "extracted_code", "test_passed", "test_total", "correct",
        "token_usage", "tool_rounds", "duration_s", "error_message", "created_at",
    }
    assert columns == expected
    conn.close()


def test_save_result_and_retrieve(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    result = _make_result()
    db.save_result(result)

    conn = sqlite3.connect(tmp_path / "results.db")
    row = conn.execute("SELECT * FROM results WHERE task_id = '992798f6'").fetchone()
    assert row is not None

    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM results WHERE task_id = '992798f6'").fetchone()
    assert row["status"] == "success"
    assert row["test_passed"] == 1
    assert row["correct"] == 1
    assert row["duration_s"] == 2.5
    conn.close()


def test_save_result_upsert(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    db.save_result(_make_result(status="wrong_answer", correct=0))
    db.save_result(_make_result(status="success", correct=1))

    conn = sqlite3.connect(tmp_path / "results.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM results WHERE task_id = '992798f6'").fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == "success"
    assert rows[0]["correct"] == 1
    conn.close()


def test_get_completed_task_ids(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    db.save_result(_make_result(task_id="aaa"))
    db.save_result(_make_result(task_id="bbb"))
    db.save_result(_make_result(task_id="ccc"))
    db.save_result(_make_result(run_name="other_run", task_id="ddd"))

    ids_r1 = db.get_completed_task_ids("test_run")
    assert ids_r1 == {"aaa", "bbb", "ccc"}

    ids_r2 = db.get_completed_task_ids("other_run")
    assert ids_r2 == {"ddd"}

    ids_empty = db.get_completed_task_ids("nonexistent")
    assert ids_empty == set()


def test_get_run_summary(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    db.save_result(_make_result(
        task_id="a", status="success", correct=1, duration_s=2.0,
        token_usage=json.dumps({"input": 100, "output": 50, "reasoning": 20, "cached": 10}),
    ))
    db.save_result(_make_result(
        task_id="b", status="wrong_answer", correct=0, duration_s=3.0,
        token_usage=json.dumps({"input": 200, "output": 80, "reasoning": 40, "cached": 20}),
    ))
    db.save_result(_make_result(
        task_id="c", status="error_llm", correct=0, duration_s=1.0,
        token_usage=json.dumps({"input": 50, "output": 10, "reasoning": 5, "cached": 0}),
    ))

    summary = db.get_run_summary("test_run")
    assert summary["total"] == 3
    assert summary["correct"] == 1
    assert abs(summary["accuracy"] - 1 / 3) < 1e-6
    assert summary["by_status"]["success"] == 1
    assert summary["by_status"]["wrong_answer"] == 1
    assert summary["by_status"]["error_llm"] == 1
    assert abs(summary["avg_duration_s"] - 2.0) < 1e-6
    assert summary["total_tokens"]["input"] == 350
    assert summary["total_tokens"]["output"] == 140
    assert summary["total_tokens"]["reasoning"] == 65
    assert summary["total_tokens"]["cached"] == 30


def test_get_run_summary_empty(tmp_path):
    db = ResultDB(tmp_path / "results.db")
    summary = db.get_run_summary("nonexistent")
    assert summary["total"] == 0
    assert summary["correct"] == 0
    assert summary["accuracy"] == 0.0
