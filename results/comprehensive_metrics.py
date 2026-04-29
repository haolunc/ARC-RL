"""Generate comprehensive metrics table for train vs eval results."""

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime


def get_comprehensive_metrics(db_path: Path) -> dict:
    """Extract all metrics from results database."""
    if not db_path.exists():
        return {}
    
    con = sqlite3.connect(str(db_path))
    cursor = con.cursor()
    
    # Task-level metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN solved=1 THEN 1 ELSE 0 END) as solved_tasks,
            SUM(test_cases_passed) as total_test_cases_passed,
            SUM(num_test_cases) as total_test_cases,
            AVG(total_time_seconds) as avg_task_time,
            SUM(total_time_seconds) as total_time_seconds
        FROM tasks
    """)
    task_row = cursor.fetchone()
    total_tasks, solved_tasks, test_cases_passed, total_test_cases, avg_task_time, total_time = task_row
    
    solve_rate = (solved_tasks / total_tasks * 100) if total_tasks > 0 else 0
    test_case_rate = (test_cases_passed / total_test_cases * 100) if total_test_cases else 0
    
    # Attempt-level metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_attempts,
            SUM(CASE WHEN test_correct=1 THEN 1 ELSE 0 END) as correct_attempts,
            SUM(CASE WHEN test_correct=0 THEN 1 ELSE 0 END) as wrong_attempts,
            AVG(prompt_tokens) as avg_prompt_tokens,
            SUM(prompt_tokens) as total_prompt_tokens,
            MIN(prompt_tokens) as min_prompt_tokens,
            MAX(prompt_tokens) as max_prompt_tokens,
            AVG(CASE WHEN prompt_tokens IS NOT NULL THEN prompt_tokens ELSE NULL END) as mean_tokens
        FROM attempts
    """)
    attempt_row = cursor.fetchone()
    (total_attempts, correct_attempts, wrong_attempts, 
     avg_prompt_tokens, total_prompt_tokens, min_tokens, max_tokens, mean_tokens) = attempt_row
    
    correct_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Error breakdown
    cursor.execute("""
        SELECT 
            CASE 
                WHEN error_type IS NULL THEN 'success'
                WHEN error_type = 'train_fail' THEN 'train_fail'
                WHEN error_type = 'test_exec_error' THEN 'non_executable'
                WHEN error_type = 'wrong_output' THEN 'wrong_output'
                WHEN error_type = 'api_error' THEN 'api_error'
                ELSE error_type
            END as outcome,
            COUNT(*) as count
        FROM attempts
        GROUP BY outcome
    """)
    outcomes = dict(cursor.fetchall())
    
    # Average metrics per task
    cursor.execute("""
        SELECT 
            AVG(attempts_per_task) as avg_attempts_per_task,
            MAX(attempts_per_task) as max_attempts_per_task
        FROM (
            SELECT task_id, COUNT(*) as attempts_per_task
            FROM attempts
            GROUP BY task_id
        )
    """)
    attempts_row = cursor.fetchone()
    avg_attempts_per_task, max_attempts_per_task = attempts_row
    
    # Cell accuracy stats
    cursor.execute("""
        SELECT 
            AVG(cell_accuracy) as avg_cell_accuracy,
            COUNT(CASE WHEN cell_accuracy >= 0.5 THEN 1 ELSE NULL END) as attempts_50pct,
            COUNT(CASE WHEN cell_accuracy = 1.0 THEN 1 ELSE NULL END) as attempts_perfect
        FROM attempts
        WHERE cell_accuracy IS NOT NULL
    """)
    accuracy_row = cursor.fetchone()
    avg_cell_accuracy, attempts_50pct, attempts_perfect = accuracy_row
    
    con.close()
    
    return {
        'total_tasks': total_tasks or 0,
        'solved_tasks': solved_tasks or 0,
        'solve_rate': solve_rate,
        'total_test_cases': total_test_cases or 0,
        'test_cases_passed': test_cases_passed or 0,
        'test_case_rate': test_case_rate,
        'avg_task_time': avg_task_time or 0,
        'total_time': total_time or 0,
        'total_attempts': total_attempts or 0,
        'correct_attempts': correct_attempts or 0,
        'wrong_attempts': wrong_attempts or 0,
        'correct_rate': correct_rate,
        'avg_prompt_tokens': avg_prompt_tokens or 0,
        'total_prompt_tokens': total_prompt_tokens or 0,
        'min_tokens': min_tokens or 0,
        'max_tokens': max_tokens or 0,
        'avg_attempts_per_task': avg_attempts_per_task or 0,
        'max_attempts_per_task': max_attempts_per_task or 0,
        'avg_cell_accuracy': avg_cell_accuracy or 0,
        'attempts_50pct': attempts_50pct or 0,
        'attempts_perfect': attempts_perfect or 0,
        'outcomes': outcomes,
    }


def format_metrics_table(train_metrics: dict, eval_metrics: dict) -> str:
    """Generate markdown table comparing train and eval metrics."""
    
    table = """# Comprehensive Metrics: Training vs Evaluation

## Summary Table

| Metric | Train | Eval | Difference |
|--------|-------|------|------------|
"""
    
    # Task-level metrics
    table += f"| **Total Tasks Evaluated** | {train_metrics['total_tasks']} | {eval_metrics['total_tasks']} | - |\n"
    table += f"| **Tasks Solved** | {train_metrics['solved_tasks']} | {eval_metrics['solved_tasks']} | {eval_metrics['solved_tasks'] - train_metrics['solved_tasks']} |\n"
    table += f"| **Solve Rate (%)** | {train_metrics['solve_rate']:.2f}% | {eval_metrics['solve_rate']:.2f}% | {eval_metrics['solve_rate'] - train_metrics['solve_rate']:.2f}pp |\n"
    table += "| | | | |\n"
    
    # Test case metrics
    table += f"| **Total Test Cases** | {train_metrics['total_test_cases']} | {eval_metrics['total_test_cases']} | - |\n"
    table += f"| **Test Cases Passed** | {train_metrics['test_cases_passed']} | {eval_metrics['test_cases_passed']} | - |\n"
    table += f"| **Test Case Pass Rate (%)** | {train_metrics['test_case_rate']:.2f}% | {eval_metrics['test_case_rate']:.2f}% | {eval_metrics['test_case_rate'] - train_metrics['test_case_rate']:.2f}pp |\n"
    table += "| | | | |\n"
    
    # Attempt metrics
    table += f"| **Total Attempts** | {train_metrics['total_attempts']} | {eval_metrics['total_attempts']} | - |\n"
    table += f"| **Correct Attempts** | {train_metrics['correct_attempts']} | {eval_metrics['correct_attempts']} | - |\n"
    table += f"| **Attempt Success Rate (%)** | {train_metrics['correct_rate']:.2f}% | {eval_metrics['correct_rate']:.2f}% | {eval_metrics['correct_rate'] - train_metrics['correct_rate']:.2f}pp |\n"
    table += f"| **Avg Attempts per Task** | {train_metrics['avg_attempts_per_task']:.2f} | {eval_metrics['avg_attempts_per_task']:.2f} | {eval_metrics['avg_attempts_per_task'] - train_metrics['avg_attempts_per_task']:.2f} |\n"
    table += f"| **Max Attempts per Task** | {train_metrics['max_attempts_per_task']:.0f} | {eval_metrics['max_attempts_per_task']:.0f} | - |\n"
    table += "| | | | |\n"
    
    # Token metrics
    table += f"| **Total Tokens Used** | {train_metrics['total_prompt_tokens']:,.0f} | {eval_metrics['total_prompt_tokens']:,.0f} | {eval_metrics['total_prompt_tokens'] - train_metrics['total_prompt_tokens']:,.0f} |\n"
    table += f"| **Avg Tokens per Attempt** | {train_metrics['avg_prompt_tokens']:.2f} | {eval_metrics['avg_prompt_tokens']:.2f} | {eval_metrics['avg_prompt_tokens'] - train_metrics['avg_prompt_tokens']:.2f} |\n"
    table += f"| **Min Tokens per Attempt** | {train_metrics['min_tokens']:.0f} | {eval_metrics['min_tokens']:.0f} | - |\n"
    table += f"| **Max Tokens per Attempt** | {train_metrics['max_tokens']:.0f} | {eval_metrics['max_tokens']:.0f} | - |\n"
    table += f"| **Avg Tokens per Solved Task** | {train_metrics['total_prompt_tokens'] / max(train_metrics['solved_tasks'], 1):.2f} | {eval_metrics['total_prompt_tokens'] / max(eval_metrics['solved_tasks'], 1):.2f} | - |\n"
    table += "| | | | |\n"
    
    # Cell accuracy metrics
    table += f"| **Avg Cell Accuracy** | {train_metrics['avg_cell_accuracy']:.4f} | {eval_metrics['avg_cell_accuracy']:.4f} | {eval_metrics['avg_cell_accuracy'] - train_metrics['avg_cell_accuracy']:.4f} |\n"
    table += f"| **Attempts ≥50% Accurate** | {train_metrics['attempts_50pct']} | {eval_metrics['attempts_50pct']} | - |\n"
    table += f"| **Perfect Accuracy Attempts** | {train_metrics['attempts_perfect']} | {eval_metrics['attempts_perfect']} | - |\n"
    table += "| | | | |\n"
    
    # Runtime metrics
    table += f"| **Avg Time per Task (sec)** | {train_metrics['avg_task_time']:.2f} | {eval_metrics['avg_task_time']:.2f} | - |\n"
    table += f"| **Total Runtime (sec)** | {train_metrics['total_time']:.2f} | {eval_metrics['total_time']:.2f} | - |\n"
    
    # Error breakdown
    table += "\n## Outcome Breakdown\n\n"
    table += "| Outcome Category | Train | Eval |\n"
    table += "|---|---|---|\n"
    
    all_outcomes = set(train_metrics['outcomes'].keys()) | set(eval_metrics['outcomes'].keys())
    for outcome in sorted(all_outcomes):
        train_count = train_metrics['outcomes'].get(outcome, 0)
        eval_count = eval_metrics['outcomes'].get(outcome, 0)
        train_pct = (train_count / train_metrics['total_attempts'] * 100) if train_metrics['total_attempts'] else 0
        eval_pct = (eval_count / eval_metrics['total_attempts'] * 100) if eval_metrics['total_attempts'] else 0
        table += f"| {outcome} | {train_count} ({train_pct:.1f}%) | {eval_count} ({eval_pct:.1f}%) |\n"
    
    # Key insights
    table += "\n## Key Insights\n\n"
    
    generalization_gap = train_metrics['solve_rate'] - eval_metrics['solve_rate']
    table += f"- **Generalization Gap**: {generalization_gap:.2f} percentage points (Train {train_metrics['solve_rate']:.1f}% vs Eval {eval_metrics['solve_rate']:.1f}%)\n"
    
    token_diff = eval_metrics['avg_prompt_tokens'] - train_metrics['avg_prompt_tokens']
    table += f"- **Token Cost**: Eval requires {token_diff:.0f} MORE tokens per attempt (+{token_diff/train_metrics['avg_prompt_tokens']*100:.1f}%)\n"
    
    table += f"- **Inference Efficiency**: Train solves tasks with {train_metrics['total_prompt_tokens']/max(train_metrics['solved_tasks'], 1):.0f} avg tokens/solved task\n"
    table += f"- **Inference Efficiency**: Eval solves tasks with {eval_metrics['total_prompt_tokens']/max(eval_metrics['solved_tasks'], 1):.0f} avg tokens/solved task\n"
    
    table += f"- **Error Profile**: Eval has {train_metrics['outcomes'].get('api_error', 0)} API errors vs Train's {train_metrics['outcomes'].get('api_error', 0)}\n"
    table += f"- **Pattern Recognition**: Eval ~{eval_metrics['correct_rate']:.1f}% attempt success vs Train's {train_metrics['correct_rate']:.1f}%\n"
    
    return table


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive metrics table")
    parser.add_argument("train_run_dir", type=str, help="Path to training results/<run_name>")
    parser.add_argument("eval_run_dir", type=str, help="Path to evaluation results/<run_name>")
    parser.add_argument("--output", type=str, default=None, help="Output file (optional)")
    args = parser.parse_args()
    
    train_db = Path(args.train_run_dir) / "results.db"
    eval_db = Path(args.eval_run_dir) / "results.db"
    
    print("Extracting training metrics...")
    train_metrics = get_comprehensive_metrics(train_db)
    
    print("Extracting eval metrics...")
    eval_metrics = get_comprehensive_metrics(eval_db)
    
    table = format_metrics_table(train_metrics, eval_metrics)
    
    print("\n" + table)
    
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(table)
        print(f"\nTable saved to: {out_path}")


if __name__ == "__main__":
    main()
