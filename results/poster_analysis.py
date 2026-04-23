"""Poster-oriented analysis for ARC GPRO run artifacts."""

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sql_one(conn: sqlite3.Connection, query: str, params=()):
    cur = conn.execute(query, params)
    return cur.fetchone()


def sql_all(conn: sqlite3.Connection, query: str, params=()):
    cur = conn.execute(query, params)
    return cur.fetchall()


def analyze_run(run_dir: Path, out_dir: Path):
    db_path = run_dir / "results.db"
    samples_path = run_dir / "gpro_samples.jsonl"
    summary_path = run_dir / "summary.json"

    if not db_path.exists():
        raise FileNotFoundError(f"Missing results DB: {db_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    samples = load_jsonl(samples_path)

    conn = sqlite3.connect(str(db_path))

    total_tasks, solved_tasks, total_test_cases, passed_test_cases = sql_one(
        conn,
        """
        SELECT COUNT(*),
               COALESCE(SUM(solved), 0),
               COALESCE(SUM(num_test_cases), 0),
               COALESCE(SUM(test_cases_passed), 0)
        FROM tasks
        """,
    )

    avg_task_time, p50_task_time, max_task_time = sql_one(
        conn,
        """
        SELECT ROUND(AVG(total_time_seconds), 2),
               ROUND((SELECT total_time_seconds FROM tasks ORDER BY total_time_seconds
                      LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM tasks)), 2),
               ROUND(MAX(total_time_seconds), 2)
        FROM tasks
        """,
    )

    total_attempts = sql_one(conn, "SELECT COUNT(*) FROM attempts")[0]
    outcome_rows = sql_all(
        conn,
        """
        SELECT COALESCE(error_type, 'success') AS outcome, COUNT(*)
        FROM attempts
        GROUP BY COALESCE(error_type, 'success')
        ORDER BY COUNT(*) DESC
        """,
    )

    conn.close()

    rewards = [r.get("reward") for r in samples if isinstance(r.get("reward"), (int, float))]
    avg_reward = (sum(rewards) / len(rewards)) if rewards else None

    by_step = defaultdict(list)
    train_pass_by_step = Counter()
    for row in samples:
        step = row.get("step")
        reward = row.get("reward")
        if isinstance(step, int) and isinstance(reward, (int, float)):
            by_step[step].append(reward)
            if row.get("train_pass"):
                train_pass_by_step[step] += 1

    step_reward_rows: list[tuple[int, int, float, float, int]] = []
    for step in sorted(by_step):
        vals = by_step[step]
        step_reward_rows.append(
            (
                step,
                len(vals),
                round(sum(vals) / len(vals), 4),
                round(max(vals), 4),
                train_pass_by_step[step],
            )
        )

    metrics_csv = out_dir / "poster_metrics.csv"
    with open(metrics_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["tasks_evaluated", total_tasks])
        writer.writerow(["tasks_solved", solved_tasks])
        writer.writerow(["solve_rate", round((solved_tasks / total_tasks), 4) if total_tasks else 0.0])
        writer.writerow(["test_cases_passed", passed_test_cases])
        writer.writerow(["total_test_cases", total_test_cases])
        writer.writerow(["total_attempts", total_attempts])
        writer.writerow(["avg_task_time_seconds", avg_task_time])
        writer.writerow(["p50_task_time_seconds", p50_task_time])
        writer.writerow(["max_task_time_seconds", max_task_time])
        writer.writerow(["num_gpro_samples", len(samples)])
        writer.writerow(["avg_gpro_reward", round(avg_reward, 4) if avg_reward is not None else ""])

    outcomes_csv = out_dir / "poster_outcomes.csv"
    with open(outcomes_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["outcome", "count"])
        writer.writerows(outcome_rows)

    step_csv = out_dir / "poster_step_rewards.csv"
    with open(step_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "num_samples", "avg_reward", "max_reward", "train_pass_count"])
        writer.writerows(step_reward_rows)

    run_meta = {}
    if summary_path.exists():
        with open(summary_path, encoding="utf-8") as f:
            run_meta = json.load(f)

    md_path = out_dir / "poster_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# ARC GPRO Poster Summary\n\n")
        f.write(f"- Run directory: `{run_dir}`\n")
        if run_meta:
            f.write(f"- Model: `{run_meta.get('model', 'unknown')}`\n")
            f.write(f"- Dataset: `{run_meta.get('dataset', 'unknown')}` / `{run_meta.get('split', 'unknown')}`\n")
            f.write(f"- Group size: `{run_meta.get('group_size', 'unknown')}`\n")
            f.write(f"- GPRO steps: `{run_meta.get('gpro_steps', 'unknown')}`\n")
            f.write(f"- Temperature: `{run_meta.get('temperature', 'unknown')}`\n")

        solve_rate = (solved_tasks / total_tasks) if total_tasks else 0.0
        f.write("\n## Core Metrics\n")
        f.write(f"- Tasks solved: **{solved_tasks}/{total_tasks} ({solve_rate:.1%})**\n")
        f.write(
            f"- Test cases passed: **{passed_test_cases}/{total_test_cases}**\n"
        )
        f.write(f"- Total attempts logged: **{total_attempts}**\n")
        f.write(f"- Avg task time: **{avg_task_time}s** (p50={p50_task_time}s, max={max_task_time}s)\n")
        f.write(f"- GPRO sample count: **{len(samples)}**\n")
        if avg_reward is not None:
            f.write(f"- Avg GPRO reward: **{avg_reward:.4f}**\n")

        f.write("\n## Attempt Outcomes\n")
        for k, v in outcome_rows:
            f.write(f"- {k}: {v}\n")

        if step_reward_rows:
            f.write("\n## Reward by GPRO Step\n")
            for step, n, avg_r, max_r, pass_n in step_reward_rows:
                f.write(
                    f"- Step {step}: n={n}, avg_reward={avg_r}, max_reward={max_r}, train_pass={pass_n}\n"
                )

        f.write("\n## Output Files\n")
        f.write(f"- `{metrics_csv.name}`\n")
        f.write(f"- `{outcomes_csv.name}`\n")
        f.write(f"- `{step_csv.name}`\n")

    print(f"Poster report: {md_path}")
    print(f"Metrics CSV:   {metrics_csv}")
    print(f"Outcomes CSV:  {outcomes_csv}")
    print(f"Step CSV:      {step_csv}")


def main():
    parser = argparse.ArgumentParser(description="Build poster analysis files for a GPRO run")
    parser.add_argument("run_dir", type=str, help="Path to results/<run_name>")
    parser.add_argument(
        "--out-dir",
        type=str,
        default=None,
        help="Output dir (default: <run_dir>/poster)",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir) if args.out_dir else run_dir / "poster"
    analyze_run(run_dir, out_dir)


if __name__ == "__main__":
    main()