import sqlite3
import sys
from pathlib import Path
from collections import Counter

def fetch_one(conn, query, params=()):
    cur = conn.execute(query, params)
    return cur.fetchone()

def fetch_all(conn, query, params=()):
    cur = conn.execute(query, params)
    return cur.fetchall()

def analyze_db(db_path: str):
    db_path = Path(db_path)
    if not db_path.exists():
        print(f"\n[ERROR] Missing DB: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))

    # Task-level summary
    total_tasks, solved_tasks, total_test_cases, passed_test_cases = fetch_one(
        conn,
        """
        SELECT COUNT(*),
               COALESCE(SUM(solved), 0),
               COALESCE(SUM(num_test_cases), 0),
               COALESCE(SUM(test_cases_passed), 0)
        FROM tasks
        """
    )

    avg_task_time, min_task_time, max_task_time = fetch_one(
        conn,
        """
        SELECT ROUND(AVG(total_time_seconds), 2),
               ROUND(MIN(total_time_seconds), 2),
               ROUND(MAX(total_time_seconds), 2)
        FROM tasks
        """
    )

    # Attempt-level summary
    total_attempts = fetch_one(conn, "SELECT COUNT(*) FROM attempts")[0]

    avg_prompt_tokens = fetch_one(
        conn,
        "SELECT ROUND(AVG(prompt_tokens), 2) FROM attempts WHERE prompt_tokens IS NOT NULL"
    )[0]

    avg_prompt_tokens_success = fetch_one(
        conn,
        """
        SELECT ROUND(AVG(prompt_tokens), 2)
        FROM attempts
        WHERE test_correct = 1 AND prompt_tokens IS NOT NULL
        """
    )[0]

    avg_prompt_tokens_fail = fetch_one(
        conn,
        """
        SELECT ROUND(AVG(prompt_tokens), 2)
        FROM attempts
        WHERE (test_correct = 0 OR train_pass = 0) AND prompt_tokens IS NOT NULL
        """
    )[0]

    # Error distribution
    error_rows = fetch_all(
        conn,
        """
        SELECT COALESCE(error_type, 'success') AS label, COUNT(*)
        FROM attempts
        GROUP BY COALESCE(error_type, 'success')
        ORDER BY COUNT(*) DESC
        """
    )
    error_counts = Counter({k: v for k, v in error_rows})

    # Retry statistics
    retry_rows = fetch_all(
        conn,
        """
        SELECT attempt, COUNT(*)
        FROM attempts
        GROUP BY attempt
        ORDER BY attempt
        """
    )

    # Success-by-attempt
    success_attempt_rows = fetch_all(
        conn,
        """
        SELECT attempt, COUNT(*)
        FROM attempts
        WHERE test_correct = 1
        GROUP BY attempt
        ORDER BY attempt
        """
    )

    # Most difficult tasks: max attempts, still unsolved
    hard_tasks = fetch_all(
        conn,
        """
        SELECT t.task_id,
               t.solved,
               t.total_time_seconds,
               COALESCE(MAX(a.attempt), 0) AS max_attempt,
               COALESCE(SUM(CASE WHEN a.error_type='train_fail' THEN 1 ELSE 0 END), 0) AS train_fail_count,
               COALESCE(SUM(CASE WHEN a.error_type='wrong_output' THEN 1 ELSE 0 END), 0) AS wrong_output_count
        FROM tasks t
        LEFT JOIN attempts a
          ON t.run_id = a.run_id AND t.task_id = a.task_id
        GROUP BY t.task_id, t.solved, t.total_time_seconds
        ORDER BY t.solved ASC, max_attempt DESC, t.total_time_seconds DESC
        LIMIT 10
        """
    )

    # Prompt token buckets
    bucket_rows = fetch_all(
        conn,
        """
        SELECT
          CASE
            WHEN prompt_tokens < 500 THEN '<500'
            WHEN prompt_tokens < 1000 THEN '500-999'
            WHEN prompt_tokens < 2000 THEN '1000-1999'
            WHEN prompt_tokens < 4000 THEN '2000-3999'
            ELSE '4000+'
          END AS bucket,
          COUNT(*) AS n,
          COALESCE(SUM(CASE WHEN test_correct = 1 THEN 1 ELSE 0 END), 0) AS success_n
        FROM attempts
        WHERE prompt_tokens IS NOT NULL
        GROUP BY bucket
        ORDER BY
          CASE bucket
            WHEN '<500' THEN 1
            WHEN '500-999' THEN 2
            WHEN '1000-1999' THEN 3
            WHEN '2000-3999' THEN 4
            ELSE 5
          END
        """
    )

    conn.close()

    print(f"\n=== Analysis for {db_path} ===")
    print(f"Tasks evaluated:      {total_tasks}")
    print(f"Tasks solved:         {solved_tasks}")
    print(f"Solve rate:           {solved_tasks / total_tasks:.2%}" if total_tasks else "Solve rate: N/A")
    print(f"Test cases passed:    {passed_test_cases}/{total_test_cases}")
    print(f"Total attempts:       {total_attempts}")
    print(f"Avg task time (s):    {avg_task_time}")
    print(f"Min/Max task time(s): {min_task_time}/{max_task_time}")
    print(f"Avg prompt tokens:    {avg_prompt_tokens}")
    print(f"Avg tokens (success): {avg_prompt_tokens_success}")
    print(f"Avg tokens (fail):    {avg_prompt_tokens_fail}")

    print("\nFailure / outcome distribution:")
    for k, v in error_rows:
        print(f"  {k:18s} {v}")

    print("\nAttempts used:")
    for attempt, count in retry_rows:
        print(f"  attempt {attempt}: {count}")

    print("\nSuccessful attempts by attempt number:")
    if success_attempt_rows:
        for attempt, count in success_attempt_rows:
            print(f"  attempt {attempt}: {count}")
    else:
        print("  none")

    print("\nPrompt token buckets:")
    for bucket, n, success_n in bucket_rows:
        rate = (success_n / n) if n else 0.0
        print(f"  {bucket:10s}  n={n:4d}  success={success_n:4d}  success_rate={rate:.2%}")

    print("\nHard / unsolved tasks (top 10):")
    for row in hard_tasks:
        task_id, solved, total_time, max_attempt, train_fail_count, wrong_output_count = row
        print(
            f"  {task_id} | solved={solved} | time={total_time}s | "
            f"max_attempt={max_attempt} | train_fail={train_fail_count} | wrong_output={wrong_output_count}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <db1> [<db2> ...]")
        sys.exit(1)

    for db in sys.argv[1:]:
        analyze_db(db)