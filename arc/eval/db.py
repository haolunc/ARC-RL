"""SQLite result database."""

import json
import sqlite3
from pathlib import Path

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS results (
    task_id         TEXT    PRIMARY KEY,
    status          TEXT    NOT NULL,
    test_passed     INTEGER DEFAULT 0,
    test_total      INTEGER DEFAULT 0,
    correct         INTEGER DEFAULT 0,
    token_usage     TEXT,
    tool_rounds     INTEGER DEFAULT 0,
    duration_s      REAL,
    test_details    TEXT,
    error_message   TEXT,
    created_at      TEXT    DEFAULT (datetime('now'))
);
"""

_COLUMNS = [
    "task_id", "status", "test_passed", "test_total", "correct",
    "token_usage", "tool_rounds", "duration_s", "test_details", "error_message",
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

    def get_completed_task_ids(self) -> set[str]:
        cursor = self.conn.execute("SELECT task_id FROM results")
        return {row[0] for row in cursor.fetchall()}

    def get_run_summary(self) -> dict:
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute("SELECT * FROM results").fetchall()
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


_CREATE_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    task_id         TEXT    PRIMARY KEY,
    text            TEXT,
    extracted_code  TEXT,
    raw_responses   TEXT,
    created_at      TEXT    DEFAULT (datetime('now'))
);
"""


class LogDB:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(_CREATE_LOG_TABLE)
        self.conn.commit()

    def save_log(self, task_id: str, text: str | None, extracted_code: str | None,
                 raw_responses: list[dict] | None):
        self.conn.execute(
            "INSERT OR REPLACE INTO logs (task_id, text, extracted_code, raw_responses)"
            " VALUES (?, ?, ?, ?)",
            (task_id, text, extracted_code, json.dumps(raw_responses) if raw_responses else None),
        )
        self.conn.commit()
