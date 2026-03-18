"""Thread-safety tests for ResultDB."""

import tempfile
import threading
from pathlib import Path

from arc.eval.db import ResultDB


def _make_db():
    """Create a ResultDB backed by a temporary file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    return ResultDB(Path(tmp.name))


def test_concurrent_insert_llm_call():
    db = _make_db()
    n_threads = 8
    n_inserts = 20
    barrier = threading.Barrier(n_threads)

    def worker(thread_id):
        barrier.wait()
        for i in range(n_inserts):
            db.insert_llm_call(
                "run1", f"task_{thread_id}_{i}", test_index=0, step=0,
                success=True,
            )

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    cur = db.conn.execute("SELECT COUNT(*) FROM llm_calls")
    assert cur.fetchone()[0] == n_threads * n_inserts
    db.close()


def test_concurrent_upsert_task():
    db = _make_db()
    n_threads = 8
    n_tasks = 10
    barrier = threading.Barrier(n_threads)

    def worker(thread_id):
        barrier.wait()
        for i in range(n_tasks):
            db.upsert_task(
                "run1", f"task_{i}", mode="direct",
                solved=(thread_id % 2 == 0),
                num_test_cases=2, test_cases_passed=1,
                total_time_seconds=1.0, final_code="pass",
            )

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Each task_id should appear exactly once due to UPSERT
    cur = db.conn.execute("SELECT COUNT(*) FROM tasks")
    assert cur.fetchone()[0] == n_tasks
    db.close()


def test_concurrent_mixed_operations():
    """Insert LLM calls and upsert tasks concurrently from different threads."""
    db = _make_db()
    n_threads = 4
    barrier = threading.Barrier(n_threads * 2)

    def llm_worker(thread_id):
        barrier.wait()
        for i in range(15):
            db.insert_llm_call(
                "run1", f"task_{thread_id}_{i}", test_index=0, step=0,
                success=True,
            )

    def task_worker(thread_id):
        barrier.wait()
        for i in range(10):
            db.upsert_task(
                "run1", f"task_{thread_id}_{i}", mode="sandbox_tools",
                solved=True,
                num_test_cases=1, test_cases_passed=1,
                total_time_seconds=0.5, final_code="pass",
            )

    threads = []
    for t in range(n_threads):
        threads.append(threading.Thread(target=llm_worker, args=(t,)))
        threads.append(threading.Thread(target=task_worker, args=(t,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    cur = db.conn.execute("SELECT COUNT(*) FROM llm_calls")
    assert cur.fetchone()[0] == n_threads * 15

    cur = db.conn.execute("SELECT COUNT(*) FROM tasks")
    assert cur.fetchone()[0] == n_threads * 10
    db.close()
