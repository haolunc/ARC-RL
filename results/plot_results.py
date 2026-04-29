"""Generate PNG plots from poster analysis CSV files and results DB."""

import argparse
import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


def read_metrics(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["metric"]] = row["value"]
    return data


def read_outcomes(path: Path) -> tuple[list[str], list[int]]:
    labels: list[str] = []
    counts: list[int] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row["outcome"])
            counts.append(int(row["count"]))
    return labels, counts


def read_step_rewards(path: Path) -> tuple[list[int], list[float], list[float], list[int]]:
    steps: list[int] = []
    avg_rewards: list[float] = []
    max_rewards: list[float] = []
    train_pass_counts: list[int] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            steps.append(int(row["step"]))
            avg_rewards.append(float(row["avg_reward"]))
            max_rewards.append(float(row["max_reward"]))
            train_pass_counts.append(int(row["train_pass_count"]))
    return steps, avg_rewards, max_rewards, train_pass_counts


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


def db_query_all(db_path: Path, query: str) -> list[tuple]:
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def metrics_from_db(db_path: Path) -> dict[str, str]:
    rows = db_query_all(
        db_path,
        """
        SELECT COUNT(*) AS tasks_evaluated,
               COALESCE(SUM(CASE WHEN solved THEN 1 ELSE 0 END), 0) AS tasks_solved,
               COALESCE(SUM(num_test_cases), 0) AS total_test_cases,
               COALESCE(SUM(test_cases_passed), 0) AS test_cases_passed
        FROM tasks
        """,
    )
    tasks_evaluated, tasks_solved, total_test_cases, test_cases_passed = rows[0]
    return {
        "tasks_evaluated": str(tasks_evaluated),
        "tasks_solved": str(tasks_solved),
        "total_test_cases": str(total_test_cases),
        "test_cases_passed": str(test_cases_passed),
    }


def outcomes_from_db(db_path: Path) -> tuple[list[str], list[int]]:
    rows = db_query_all(
        db_path,
        """
        SELECT COALESCE(error_type, 'success') AS outcome, COUNT(*)
        FROM attempts
        GROUP BY COALESCE(error_type, 'success')
        ORDER BY COUNT(*) DESC
        """,
    )
    return [r[0] for r in rows], [int(r[1]) for r in rows]


def make_solve_rate_plot(metrics: dict[str, str], out_dir: Path) -> Path:
    tasks = int(metrics.get("tasks_evaluated", 0) or 0)
    solved = int(metrics.get("tasks_solved", 0) or 0)
    failed = max(tasks - solved, 0)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Solved", "Failed"], [solved, failed])
    ax.set_title("Task Outcomes")
    ax.set_ylabel("Count")

    out_path = out_dir / "plot_task_outcomes.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_outcomes_plot(labels: list[str], counts: list[int], out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, counts)
    ax.set_title("Attempt Outcome Distribution")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)

    out_path = out_dir / "plot_attempt_outcomes.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_success_by_step_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT attempt, COUNT(*)
        FROM attempts
        WHERE test_correct = 1
        GROUP BY attempt
        ORDER BY attempt
        """,
    )
    if not rows:
        return None

    steps = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([str(s) for s in steps], counts)
    ax.set_title("Solved Test Cases by Step")
    ax.set_xlabel("Step")
    ax.set_ylabel("Solved Count")

    out_path = out_dir / "plot_success_by_step.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_runtime_hist_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT total_time_seconds
        FROM tasks
        WHERE total_time_seconds IS NOT NULL
        """,
    )
    if not rows:
        return None

    values = [float(r[0]) for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(values, bins=min(12, max(4, len(values))), edgecolor="black")
    ax.set_title("Task Runtime Distribution")
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Task Count")

    out_path = out_dir / "plot_task_runtime_hist.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_tokens_vs_accuracy_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT prompt_tokens, cell_accuracy, test_correct
        FROM attempts
        WHERE prompt_tokens IS NOT NULL AND (test_correct = 1 OR test_correct = 0)
        """,
    )
    if not rows:
        return None

    x_success, y_success = [], []
    x_fail, y_fail = [], []
    for prompt_tokens, cell_accuracy, test_correct in rows:
        x = float(prompt_tokens)
        y = float(cell_accuracy) if cell_accuracy is not None else 0.0
        if int(test_correct) == 1:
            x_success.append(x)
            y_success.append(y)
        else:
            x_fail.append(x)
            y_fail.append(y)

    fig, ax = plt.subplots(figsize=(7, 4))
    if x_success:
        ax.scatter(x_success, y_success, alpha=0.7, label="correct")
    if x_fail:
        ax.scatter(x_fail, y_fail, alpha=0.7, label="wrong")
    ax.set_title("Prompt Tokens vs Cell Accuracy")
    ax.set_xlabel("Prompt Tokens")
    ax.set_ylabel("Cell Accuracy")
    ax.legend()

    out_path = out_dir / "plot_tokens_vs_accuracy.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_attempts_per_task_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT task_id, COUNT(*) AS attempts_per_task
        FROM attempts
        GROUP BY task_id
        ORDER BY attempts_per_task DESC, task_id
        """,
    )
    if not rows:
        return None

    counts = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = range(1, max(counts) + 2)
    ax.hist(counts, bins=bins, edgecolor="black", align="left")
    ax.set_title("Attempts per Task")
    ax.set_xlabel("Attempts")
    ax.set_ylabel("Task Count")
    ax.set_xticks(list(range(1, max(counts) + 1)))

    out_path = out_dir / "plot_attempts_per_task.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_task_timeline_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT rowid, solved, total_time_seconds
        FROM tasks
        ORDER BY rowid
        """,
    )
    if not rows:
        return None

    xs = [int(r[0]) for r in rows]
    ys = [1 if int(r[1]) == 1 else 0 for r in rows]
    times = [float(r[2]) if r[2] is not None else 0.0 for r in rows]

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.scatter(xs, ys, s=18, alpha=0.8)
    ax1.set_title("Task Timeline: Solved vs Failed")
    ax1.set_xlabel("Task Index")
    ax1.set_ylabel("Solved (1) / Failed (0)")
    ax1.set_ylim(-0.1, 1.1)

    ax2 = ax1.twinx()
    ax2.plot(xs, times, color="tab:orange", alpha=0.25, linewidth=1.5)
    ax2.set_ylabel("Task Runtime (sec)")

    out_path = out_dir / "plot_task_timeline.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_error_breakdown_plot(db_path: Path, out_dir: Path) -> Path | None:
    rows = db_query_all(
        db_path,
        """
        SELECT COALESCE(error_type, 'success') AS outcome, COUNT(*)
        FROM attempts
        GROUP BY COALESCE(error_type, 'success')
        ORDER BY COUNT(*) DESC
        """,
    )
    if not rows:
        return None

    labels = [r[0] for r in rows]
    counts = [int(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, counts, color="tab:purple")
    ax.set_title("Detailed Attempt Error Breakdown")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=35)

    out_path = out_dir / "plot_error_breakdown.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_dashboard_plot(db_path: Path, out_dir: Path) -> Path | None:
    task_rows = db_query_all(
        db_path,
        """
        SELECT solved, total_time_seconds
        FROM tasks
        ORDER BY rowid
        """,
    )
    attempt_rows = db_query_all(
        db_path,
        """
        SELECT COALESCE(error_type, 'success') AS outcome,
               prompt_tokens,
               cell_accuracy,
               test_correct,
               task_id
        FROM attempts
        """,
    )
    if not task_rows:
        return None

    solved_flags = [1 if int(r[0]) == 1 else 0 for r in task_rows]
    runtimes = [float(r[1]) if r[1] is not None else 0.0 for r in task_rows]

    cum_rate = []
    solved = 0
    for i, flag in enumerate(solved_flags, 1):
        solved += flag
        cum_rate.append(100.0 * solved / i)

    outcomes = Counter(r[0] for r in attempt_rows)

    x_success, y_success = [], []
    x_fail, y_fail = [], []
    for outcome, prompt_tokens, cell_accuracy, test_correct, _task_id in attempt_rows:
        if prompt_tokens is None or test_correct is None:
            continue
        x = float(prompt_tokens)
        y = float(cell_accuracy) if cell_accuracy is not None else 0.0
        if int(test_correct) == 1:
            x_success.append(x)
            y_success.append(y)
        elif int(test_correct) == 0:
            x_fail.append(x)
            y_fail.append(y)

    task_attempt_counts = Counter(r[4] for r in attempt_rows)
    attempts_per_task = list(task_attempt_counts.values())

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    ax = axes[0, 0]
    ax.plot(range(1, len(cum_rate) + 1), cum_rate, linewidth=2)
    ax.set_title("Cumulative Solve Rate")
    ax.set_xlabel("Task index")
    ax.set_ylabel("Solve rate (%)")
    ax.set_ylim(0, max(100, max(cum_rate) + 5))
    ax.grid(True, alpha=0.25)

    ax = axes[0, 1]
    labels = list(outcomes.keys())
    counts = list(outcomes.values())
    ax.bar(labels, counts, color="tab:orange")
    ax.set_title("Attempt Outcomes")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=30)

    ax = axes[0, 2]
    ax.hist(runtimes, bins=min(12, max(4, len(runtimes) // 5)), edgecolor="black")
    ax.set_title("Task Runtime Distribution")
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Tasks")

    ax = axes[1, 0]
    if attempts_per_task:
        ax.hist(attempts_per_task, bins=range(1, max(attempts_per_task) + 2), edgecolor="black", align="left")
    ax.set_title("Attempts per Task")
    ax.set_xlabel("Attempts")
    ax.set_ylabel("Tasks")

    ax = axes[1, 1]
    if x_success:
        ax.scatter(x_success, y_success, alpha=0.7, label="correct")
    if x_fail:
        ax.scatter(x_fail, y_fail, alpha=0.7, label="wrong")
    ax.set_title("Prompt Tokens vs Cell Accuracy")
    ax.set_xlabel("Prompt Tokens")
    ax.set_ylabel("Cell Accuracy")
    if x_success or x_fail:
        ax.legend()

    ax = axes[1, 2]
    ax.scatter(range(1, len(solved_flags) + 1), solved_flags, s=16, alpha=0.85)
    ax.set_title("Solved Tasks Over Time")
    ax.set_xlabel("Task index")
    ax.set_ylabel("Solved (0/1)")
    ax.set_ylim(-0.1, 1.1)

    fig.suptitle("ARC-AGI Evaluation Dashboard", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = out_dir / "plot_dashboard.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def make_reward_hist_plot(samples_path: Path, out_dir: Path) -> Path | None:
    rows = load_jsonl(samples_path)
    values = [float(r["reward"]) for r in rows if isinstance(r.get("reward"), (int, float))]
    if not values:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(values, bins=min(20, max(6, len(values) // 2)), edgecolor="black")
    ax.set_title("GPRO Reward Distribution")
    ax.set_xlabel("Reward")
    ax.set_ylabel("Sample Count")

    out_path = out_dir / "plot_reward_histogram.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def make_step_reward_plot(
    steps: list[int],
    avg_rewards: list[float],
    max_rewards: list[float],
    train_pass_counts: list[int],
    out_dir: Path,
) -> Path | None:
    if not steps:
        return None

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(steps, avg_rewards, marker="o", label="avg_reward")
    ax1.plot(steps, max_rewards, marker="o", label="max_reward")
    ax1.set_xlabel("GPRO Step")
    ax1.set_ylabel("Reward")
    ax1.set_title("Reward by GPRO Step")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(steps, train_pass_counts, marker="s", linestyle="--", label="train_pass_count")
    ax2.set_ylabel("Train Pass Count")

    out_path = out_dir / "plot_step_rewards.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate plots from poster CSV outputs")
    parser.add_argument("run_dir", type=str, help="Path to results/<run_name>")
    parser.add_argument(
        "--poster-dir",
        type=str,
        default=None,
        help="Poster directory (default: <run_dir>/poster)",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    poster_dir = Path(args.poster_dir) if args.poster_dir else run_dir / "poster"
    db_path = run_dir / "results.db"
    samples_path = run_dir / "gpro_samples.jsonl"

    metrics_csv = poster_dir / "poster_metrics.csv"
    outcomes_csv = poster_dir / "poster_outcomes.csv"
    step_csv = poster_dir / "poster_step_rewards.csv"

    poster_dir.mkdir(parents=True, exist_ok=True)

    if metrics_csv.exists():
        metrics = read_metrics(metrics_csv)
    else:
        metrics = metrics_from_db(db_path)

    if outcomes_csv.exists():
        labels, counts = read_outcomes(outcomes_csv)
    else:
        labels, counts = outcomes_from_db(db_path)

    if step_csv.exists():
        steps, avg_rewards, max_rewards, train_pass_counts = read_step_rewards(step_csv)
    else:
        steps, avg_rewards, max_rewards, train_pass_counts = [], [], [], []

    print(make_solve_rate_plot(metrics, poster_dir))
    print(make_outcomes_plot(labels, counts, poster_dir))
    step_plot = make_step_reward_plot(steps, avg_rewards, max_rewards, train_pass_counts, poster_dir)
    if step_plot is not None:
        print(step_plot)

    success_plot = make_success_by_step_plot(db_path, poster_dir)
    if success_plot is not None:
        print(success_plot)

    runtime_plot = make_runtime_hist_plot(db_path, poster_dir)
    if runtime_plot is not None:
        print(runtime_plot)

    token_plot = make_tokens_vs_accuracy_plot(db_path, poster_dir)
    if token_plot is not None:
        print(token_plot)

    attempts_plot = make_attempts_per_task_plot(db_path, poster_dir)
    if attempts_plot is not None:
        print(attempts_plot)

    timeline_plot = make_task_timeline_plot(db_path, poster_dir)
    if timeline_plot is not None:
        print(timeline_plot)

    error_plot = make_error_breakdown_plot(db_path, poster_dir)
    if error_plot is not None:
        print(error_plot)

    dashboard_plot = make_dashboard_plot(db_path, poster_dir)
    if dashboard_plot is not None:
        print(dashboard_plot)

    reward_hist = make_reward_hist_plot(samples_path, poster_dir)
    if reward_hist is not None:
        print(reward_hist)


if __name__ == "__main__":
    main()