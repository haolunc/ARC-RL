"""SQLite logging for ARC evaluation pipeline."""

import sqlite3
from datetime import datetime
from pathlib import Path


SCHEMA = """\
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    split TEXT NOT NULL,
    max_retries INTEGER NOT NULL,
    timeout INTEGER NOT NULL,
    temperature REAL NOT NULL,
    started_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    solved INTEGER NOT NULL DEFAULT 0,
    num_test_cases INTEGER,
    test_cases_passed INTEGER DEFAULT 0,
    total_time_seconds REAL,
    final_code TEXT,
    completed_at TEXT,
    UNIQUE(run_id, task_id)
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    test_index INTEGER NOT NULL,
    attempt INTEGER NOT NULL,
    llm_response TEXT,
    extracted_code TEXT,
    train_pass INTEGER,
    test_correct INTEGER,
    cell_accuracy REAL,
    error_type TEXT,
    error_msg TEXT,
    created_at TEXT NOT NULL
);
"""


class ResultDB:
    """SQLite-backed result logger. Writes are committed immediately."""

    def __init__(self, db_path: str | Path):
        path = Path(db_path)

        # Ensure the directory for the database exists
        path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(path)

        # Create SQLite connection
        self.conn = sqlite3.connect(self.db_path, timeout=30)

        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert_run(self, run_id: str, dataset: str, split: str,
                   max_retries: int, timeout: int, temperature: float):
        self.conn.execute(
            "INSERT OR IGNORE INTO runs VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, dataset, split, max_retries, timeout, temperature,
             datetime.now().isoformat()),
        )
        self.conn.commit()

    def insert_attempt(self, run_id: str, task_id: str, test_index: int,
                       attempt: int, llm_response: str | None,
                       extracted_code: str | None, train_pass: bool | None,
                       test_correct: bool | None, cell_accuracy: float | None,
                       error_type: str | None, error_msg: str | None):
        self.conn.execute(
            "INSERT INTO attempts "
            "(run_id, task_id, test_index, attempt, llm_response, extracted_code, "
            "train_pass, test_correct, cell_accuracy, error_type, error_msg, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (run_id, task_id, test_index, attempt, llm_response, extracted_code,
             int(train_pass) if train_pass is not None else None,
             int(test_correct) if test_correct is not None else None,
             cell_accuracy, error_type, error_msg,
             datetime.now().isoformat()),
        )
        self.conn.commit()

    def upsert_task(self, run_id: str, task_id: str, solved: bool,
                    num_test_cases: int, test_cases_passed: int,
                    total_time_seconds: float, final_code: str | None):
        self.conn.execute(
            "INSERT INTO tasks "
            "(run_id, task_id, solved, num_test_cases, test_cases_passed, "
            "total_time_seconds, final_code, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(run_id, task_id) DO UPDATE SET "
            "solved=excluded.solved, num_test_cases=excluded.num_test_cases, "
            "test_cases_passed=excluded.test_cases_passed, "
            "total_time_seconds=excluded.total_time_seconds, "
            "final_code=excluded.final_code, completed_at=excluded.completed_at",
            (run_id, task_id, int(solved), num_test_cases, test_cases_passed,
             total_time_seconds, final_code, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_completed_task_ids(self, run_id: str) -> set[str]:
        """Get task IDs already completed in this run (for resuming)."""
        cur = self.conn.execute(
            "SELECT task_id FROM tasks WHERE run_id = ?", (run_id,)
        )
        return {row[0] for row in cur.fetchall()}

    def get_summary(self, run_id: str) -> dict:
        cur = self.conn.execute(
            "SELECT COUNT(*), SUM(solved), SUM(num_test_cases), SUM(test_cases_passed) "
            "FROM tasks WHERE run_id = ?", (run_id,)
        )
        row = cur.fetchone()
        total = row[0] or 0
        solved = row[1] or 0
        return {
            "tasks_evaluated": total,
            "tasks_solved": solved,
            "solve_rate": round(solved / total, 4) if total else 0,
            "total_test_cases": row[2] or 0,
            "test_cases_passed": row[3] or 0,
        }

    def close(self):
        self.conn.close()
