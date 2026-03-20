"""SQLite result database."""

import json
import sqlite3
from pathlib import Path

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS results (
    run_name        TEXT    NOT NULL,
    task_id         TEXT    NOT NULL,
    mode            TEXT    NOT NULL,
    endpoint_name   TEXT    NOT NULL,
    status          TEXT    NOT NULL,
    raw_response    TEXT,
    extracted_code  TEXT,
    test_passed     INTEGER DEFAULT 0,
    test_total      INTEGER DEFAULT 0,
    correct         INTEGER DEFAULT 0,
    token_usage     TEXT,
    tool_rounds     INTEGER DEFAULT 0,
    duration_s      REAL,
    error_message   TEXT,
    created_at      TEXT    DEFAULT (datetime('now')),
    PRIMARY KEY (run_name, task_id)
);
"""

_COLUMNS = [
    "run_name", "task_id", "mode", "endpoint_name", "status",
    "raw_response", "extracted_code", "test_passed", "test_total", "correct",
    "token_usage", "tool_rounds", "duration_s", "error_message",
]


class ResultDB:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(_CREATE_TABLE)
        self.conn.commit()

    def save_result(self, result: dict):
        placeholders = ", ".join(["?"] * len(_COLUMNS))
        cols = ", ".join(_COLUMNS)
        values = [result.get(c) for c in _COLUMNS]
        self.conn.execute(
            f"INSERT OR REPLACE INTO results ({cols}) VALUES ({placeholders})",
            values,
        )
        self.conn.commit()

    def get_completed_task_ids(self, run_name: str) -> set[str]:
        cursor = self.conn.execute(
            "SELECT task_id FROM results WHERE run_name = ?", (run_name,)
        )
        return {row[0] for row in cursor.fetchall()}

    def get_run_summary(self, run_name: str) -> dict:
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(
            "SELECT * FROM results WHERE run_name = ?", (run_name,)
        ).fetchall()
        self.conn.row_factory = None

        if not rows:
            return {
                "total": 0, "correct": 0, "accuracy": 0.0,
                "by_status": {}, "avg_duration_s": 0.0,
                "total_tokens": {"input": 0, "output": 0, "reasoning": 0, "cached": 0},
            }

        total = len(rows)
        correct = sum(1 for r in rows if r["correct"])
        by_status = {}
        for r in rows:
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1

        durations = [r["duration_s"] for r in rows if r["duration_s"] is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        total_tokens = {"input": 0, "output": 0, "reasoning": 0, "cached": 0}
        for r in rows:
            if r["token_usage"]:
                usage = json.loads(r["token_usage"])
                for k in total_tokens:
                    total_tokens[k] += usage.get(k, 0)

        return {
            "total": total,
            "correct": correct,
            "accuracy": correct / total,
            "by_status": by_status,
            "avg_duration_s": avg_duration,
            "total_tokens": total_tokens,
        }
