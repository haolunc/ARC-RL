"""SQLite logging for ARC evaluation pipeline."""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path


SCHEMA = """\
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

CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    test_index INTEGER NOT NULL,
    step INTEGER NOT NULL,

    -- Request
    input_messages TEXT,
    requested_model TEXT,
    temperature REAL,

    -- Response metadata
    response_id TEXT,
    actual_model TEXT,
    finish_reason TEXT,
    llm_response TEXT,
    thinking TEXT,

    -- Token usage
    input_tokens INTEGER,
    output_tokens INTEGER,
    cached_tokens INTEGER,

    -- Timing
    duration_seconds REAL,

    -- Status
    success INTEGER NOT NULL DEFAULT 1,
    error_type TEXT,
    error_msg TEXT,

    -- Simple-mode verification results (null in agentic mode)
    extracted_code TEXT,
    train_pass INTEGER,
    test_correct INTEGER,
    cell_accuracy REAL,

    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    llm_call_id INTEGER NOT NULL REFERENCES llm_calls(id),
    tool_call_index INTEGER NOT NULL,
    tool_call_id TEXT,
    tool_name TEXT NOT NULL,
    tool_arguments TEXT,
    tool_output TEXT,
    extracted_code TEXT,
    test_correct INTEGER,
    duration_seconds REAL,
    created_at TEXT NOT NULL
);
"""


_LLM_CALL_COLUMNS = (
    "run_id", "task_id", "test_index", "step",
    "input_messages", "requested_model", "temperature",
    "response_id", "actual_model", "finish_reason", "llm_response", "thinking",
    "input_tokens", "output_tokens", "cached_tokens",
    "duration_seconds", "success", "error_type", "error_msg",
    "extracted_code", "train_pass", "test_correct", "cell_accuracy",
    "created_at",
)

_LLM_CALL_SQL = (
    f"INSERT INTO llm_calls ({', '.join(_LLM_CALL_COLUMNS)}) "
    f"VALUES ({', '.join('?' for _ in _LLM_CALL_COLUMNS)})"
)


class ResultDB:
    """SQLite-backed result logger. Writes are committed immediately."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert_llm_call(self, run_id: str, task_id: str, test_index: int,
                        step: int, *,
                        llm_result=None,
                        input_messages: str | None = None,
                        thinking: str | None = None,
                        success: bool = True,
                        error_type: str | None = None,
                        error_msg: str | None = None,
                        extracted_code: str | None = None,
                        train_pass: bool | None = None,
                        test_correct: bool | None = None,
                        cell_accuracy: float | None = None) -> int:
        """Insert an LLM call record. Returns the row id.

        If llm_result (LLMResponse) is provided, its fields are extracted
        automatically for the response metadata columns.
        """
        if llm_result is not None:
            requested_model = llm_result.requested_model
            temperature = llm_result.temperature
            response_id = llm_result.response_id
            actual_model = llm_result.actual_model
            finish_reason = llm_result.finish_reason
            llm_response = llm_result.content
            input_tokens = llm_result.input_tokens
            output_tokens = llm_result.output_tokens
            cached_tokens = llm_result.cached_tokens
            duration_seconds = llm_result.duration_seconds
        else:
            requested_model = temperature = response_id = actual_model = None
            finish_reason = llm_response = None
            input_tokens = output_tokens = cached_tokens = duration_seconds = None

        values = (
            run_id, task_id, test_index, step,
            input_messages, requested_model, temperature,
            response_id, actual_model, finish_reason, llm_response, thinking,
            input_tokens, output_tokens, cached_tokens,
            duration_seconds, int(success) if success is not None else None,
            error_type, error_msg,
            extracted_code,
            int(train_pass) if train_pass is not None else None,
            int(test_correct) if test_correct is not None else None,
            cell_accuracy,
            datetime.now().isoformat(),
        )
        with self._lock:
            cur = self.conn.execute(_LLM_CALL_SQL, values)
            self.conn.commit()
            return cur.lastrowid

    def insert_tool_call(self, llm_call_id: int, tool_call_index: int, *,
                         tool_call_id: str | None = None,
                         tool_name: str,
                         tool_arguments: str | None = None,
                         tool_output: str | None = None,
                         extracted_code: str | None = None,
                         test_correct: bool | None = None,
                         duration_seconds: float | None = None) -> int:
        """Insert a tool call record. Returns the row id."""
        with self._lock:
            cur = self.conn.execute(
                "INSERT INTO tool_calls "
                "(llm_call_id, tool_call_index, tool_call_id, tool_name, "
                "tool_arguments, tool_output, extracted_code, test_correct, "
                "duration_seconds, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (llm_call_id, tool_call_index, tool_call_id, tool_name,
                 tool_arguments, tool_output, extracted_code,
                 int(test_correct) if test_correct is not None else None,
                 duration_seconds,
                 datetime.now().isoformat()),
            )
            self.conn.commit()
            return cur.lastrowid

    def upsert_task(self, run_id: str, task_id: str, solved: bool,
                    num_test_cases: int, test_cases_passed: int,
                    total_time_seconds: float, final_code: str | None):
        with self._lock:
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
        """Get task IDs already completed in this run."""
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

        # Token and timing aggregates from llm_calls
        token_cur = self.conn.execute(
            "SELECT SUM(input_tokens), SUM(output_tokens), SUM(cached_tokens), "
            "COUNT(*), SUM(duration_seconds) "
            "FROM llm_calls WHERE run_id = ? AND success = 1", (run_id,)
        )
        token_row = token_cur.fetchone()

        return {
            "tasks_evaluated": total,
            "tasks_solved": solved,
            "solve_rate": round(solved / total, 4) if total else 0,
            "total_test_cases": row[2] or 0,
            "test_cases_passed": row[3] or 0,
            "total_llm_calls": token_row[3] or 0,
            "total_input_tokens": token_row[0] or 0,
            "total_output_tokens": token_row[1] or 0,
            "total_cached_tokens": token_row[2] or 0,
            "total_llm_duration_seconds": round(token_row[4] or 0, 2),
        }

    def close(self):
        self.conn.close()
