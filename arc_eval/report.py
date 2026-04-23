"""Summarize ARC run results from the SQLite database."""

import argparse
import sqlite3
from pathlib import Path


def summarize(db_path: Path) -> dict:
    conn = sqlite3.connect(str(db_path))

    total_tasks, solved_tasks, total_test_cases, passed_test_cases = conn.execute(
        """
        SELECT COUNT(*),
               COALESCE(SUM(solved), 0),
               COALESCE(SUM(num_test_cases), 0),
               COALESCE(SUM(test_cases_passed), 0)
        FROM tasks
        """
    ).fetchone()

    total_attempts = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    conn.close()

    return {
        "tasks_evaluated": total_tasks or 0,
        "tasks_solved": solved_tasks or 0,
        "solve_rate": (solved_tasks / total_tasks) if total_tasks else 0.0,
        "test_cases_passed": passed_test_cases or 0,
        "total_test_cases": total_test_cases or 0,
        "total_attempts": total_attempts or 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Print a compact ARC run summary")
    parser.add_argument("run_dir", type=str, help="Path to results/<run_name>")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    db_path = run_dir / "results.db"

    if not db_path.exists():
        raise FileNotFoundError(f"Missing DB: {db_path}")

    s = summarize(db_path)
    print(f"Run dir:           {run_dir}")
    print(f"Tasks evaluated:   {s['tasks_evaluated']}")
    print(f"Tasks solved:      {s['tasks_solved']}")
    print(f"Solve rate:        {s['solve_rate']:.1%}")
    print(f"Test cases passed: {s['test_cases_passed']}/{s['total_test_cases']}")
    print(f"Total attempts:    {s['total_attempts']}")


if __name__ == "__main__":
    main()