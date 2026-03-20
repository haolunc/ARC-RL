"""SQLite result database."""

import sqlite3
from pathlib import Path


class ResultDB:
    def __init__(self, db_path: Path):
        """Open or create SQLite database, auto-create tables."""
        raise NotImplementedError

    def save_result(self, result: dict):
        """INSERT OR REPLACE a result record."""
        raise NotImplementedError

    def get_completed_task_ids(self, run_name: str) -> set[str]:
        """Return set of completed task_ids for a run (for resume dedup)."""
        raise NotImplementedError

    def get_run_summary(self, run_name: str) -> dict:
        """Return run summary: total, correct, accuracy, by_status, etc."""
        raise NotImplementedError
