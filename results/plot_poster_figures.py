"""Generate publication-quality figures for ARC-RL poster."""

import argparse
import csv
import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ARC color palette
ARC_COLORS = {
    0: "#000000",  # black
    1: "#0074D9",  # blue
    2: "#FF4136",  # red
    3: "#2ECC40",  # green
    4: "#FFDC00",  # yellow
    5: "#AAAAAA",  # gray
    6: "#F012BE",  # magenta
    7: "#FF851B",  # orange
    8: "#7FDBCA",  # teal
    9: "#870C25",  # maroon
}


def load_task_from_json(task_file: Path) -> dict:
    """Load an ARC task from JSON."""
    with open(task_file) as f:
        return json.load(f)


def grid_to_image(grid: list[list[int]]) -> np.ndarray:
    """Convert grid of color codes to RGB image array."""
    height, width = len(grid), len(grid[0]) if grid else 0
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    for i in range(height):
        for j in range(width):
            color_code = grid[i][j]
            color_hex = ARC_COLORS.get(color_code, "#FFFFFF")
            # Convert hex to RGB
            color_hex = color_hex.lstrip('#')
            image[i, j] = tuple(int(color_hex[k:k+2], 16) for k in (0, 2, 4))
    
    return image


def plot_grid(ax, grid: list[list[int]], title: str = ""):
    """Plot a single grid on the given axes."""
    image = grid_to_image(grid)
    ax.imshow(image, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10, fontweight='bold')


def get_metrics_from_db(db_path: Path) -> dict:
    """Extract key metrics from results database."""
    if not db_path.exists():
        return {}
    
    con = sqlite3.connect(str(db_path))
    cursor = con.cursor()
    
    # Get solve rate
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE solved=1")
    solved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    solve_rate = (solved / total * 100) if total > 0 else 0
    
    # Get avg tokens
    cursor.execute("SELECT AVG(prompt_tokens) FROM attempts WHERE prompt_tokens IS NOT NULL")
    avg_tokens = cursor.fetchone()[0] or 0
    
    # Get outcome breakdown
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
    
    # Get token distribution per task
    cursor.execute("""
        SELECT task_id, AVG(prompt_tokens) as avg_tokens
        FROM attempts
        WHERE prompt_tokens IS NOT NULL
        GROUP BY task_id
    """)
    token_per_task = cursor.fetchall()
    
    con.close()
    
    return {
        'solve_rate': solve_rate,
        'solved': solved,
        'total': total,
        'avg_tokens': avg_tokens,
        'outcomes': outcomes,
        'token_per_task': token_per_task,
    }


def make_main_results_figure(train_metrics: dict, eval_metrics: dict, out_dir: Path) -> Path:
    """Figure A: Main Results Bar Chart.
    
    Shows:
    - Train solve rate vs Eval solve rate
    - Avg tokens per train task vs Eval task
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Solve rates
    datasets = ['Train', 'Eval']
    solve_rates = [train_metrics.get('solve_rate', 0), eval_metrics.get('solve_rate', 0)]
    colors_sr = ['#2E86AB', '#A23B72']
    bars1 = ax1.bar(datasets, solve_rates, color=colors_sr, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Solve Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Task Solve Rate Comparison', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars1, solve_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Avg tokens
    avg_tokens = [train_metrics.get('avg_tokens', 0), eval_metrics.get('avg_tokens', 0)]
    colors_tk = ['#2E86AB', '#A23B72']
    bars2 = ax2.bar(datasets, avg_tokens, color=colors_tk, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Average Tokens per Task', fontsize=12, fontweight='bold')
    ax2.set_title('Token Usage Comparison', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars2, avg_tokens):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    fig.suptitle('Figure A: Main Results Summary', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    
    out_path = out_dir / 'figureA_main_results.png'
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out_path


def make_outcome_breakdown_figure(train_metrics: dict, eval_metrics: dict, out_dir: Path) -> Path:
    """Figure B: Outcome Breakdown with stacked bars.
    
    Shows:
    - success
    - executable but wrong (wrong_output)
    - non-executable (test_exec_error)
    - API/system failure (api_error + train_fail)
    """
    # Normalize outcomes to standard categories
    def normalize_outcomes(outcomes_dict):
        return {
            'Success': outcomes_dict.get('success', 0),
            'Wrong Output': outcomes_dict.get('wrong_output', 0),
            'Non-Executable': outcomes_dict.get('non_executable', 0),
            'API/Train Fail': outcomes_dict.get('api_error', 0) + outcomes_dict.get('train_fail', 0),
        }
    
    train_outcomes = normalize_outcomes(train_metrics.get('outcomes', {}))
    eval_outcomes = normalize_outcomes(eval_metrics.get('outcomes', {}))
    
    # Calculate totals for percentages
    train_total = sum(train_outcomes.values())
    eval_total = sum(eval_outcomes.values())
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    datasets = ['Train\n(100 tasks)', 'Eval\n(50 tasks)']
    outcome_categories = ['Success', 'Wrong Output', 'Non-Executable', 'API/Train Fail']
    outcome_colors = ['#2ECC40', '#FF4136', '#FFDC00', '#AAAAAA']
    
    train_values = [train_outcomes[cat] for cat in outcome_categories]
    eval_values = [eval_outcomes[cat] for cat in outcome_categories]
    
    x = np.arange(len(datasets))
    width = 0.6
    
    bottom_train = 0
    bottom_eval = 0
    
    for i, (cat, color) in enumerate(zip(outcome_categories, outcome_colors)):
        train_val = train_outcomes[cat]
        eval_val = eval_outcomes[cat]
        
        # Create bars with clear separation
        bar1 = ax.bar(0, train_val, width, label=cat, 
                      bottom=bottom_train, color=color, edgecolor='black', linewidth=2)
        bar2 = ax.bar(1, eval_val, width,
                      bottom=bottom_eval, color=color, edgecolor='black', linewidth=2)
        
        # Add text labels with counts AND percentages
        if train_val > 0:
            pct = (train_val / train_total * 100)
            label_text = f'{int(train_val)}\n({pct:.0f}%)'
            y_pos = bottom_train + train_val / 2
            # Choose text color based on background
            text_color = 'white' if color != '#FFDC00' else 'black'
            ax.text(0, y_pos, label_text,
                   ha='center', va='center', fontweight='bold', fontsize=10, 
                   color=text_color, bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor=color, alpha=0.2, edgecolor='none'))
        
        if eval_val > 0:
            pct = (eval_val / eval_total * 100)
            label_text = f'{int(eval_val)}\n({pct:.0f}%)'
            y_pos = bottom_eval + eval_val / 2
            text_color = 'white' if color != '#FFDC00' else 'black'
            ax.text(1, y_pos, label_text,
                   ha='center', va='center', fontweight='bold', fontsize=10,
                   color=text_color, bbox=dict(boxstyle='round,pad=0.3',
                   facecolor=color, alpha=0.2, edgecolor='none'))
        
        bottom_train += train_val
        bottom_eval += eval_val
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(datasets, fontsize=13, fontweight='bold')
    ax.set_ylabel('Attempt Count', fontsize=13, fontweight='bold')
    ax.set_title('Figure B: Outcome Breakdown (Train vs Eval)', fontsize=14, fontweight='bold', pad=20)
    
    # Create custom legend with clear labels
    handles = [mpatches.Patch(facecolor=color, edgecolor='black', linewidth=2, label=cat) 
              for cat, color in zip(outcome_categories, outcome_colors)]
    ax.legend(handles=handles, loc='upper left', fontsize=11, frameon=True, 
             fancybox=True, shadow=True, title='Outcome Type', title_fontsize=12)
    
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Set reasonable y-limit
    max_y = max(bottom_train, bottom_eval) * 1.1
    ax.set_ylim(0, max_y)
    
    fig.tight_layout()
    out_path = out_dir / 'figureB_outcome_breakdown.png'
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out_path


def make_cost_vs_performance_figure(train_metrics: dict, eval_metrics: dict, out_dir: Path) -> Path:
    """Figure C: Cost vs Performance scatter plot.
    
    x-axis: Average tokens used per task
    y-axis: Solve rate (%)
    """
    fig, ax = plt.subplots(figsize=(9, 6))
    
    train_tokens = train_metrics.get('avg_tokens', 0)
    train_rate = train_metrics.get('solve_rate', 0)
    eval_tokens = eval_metrics.get('avg_tokens', 0)
    eval_rate = eval_metrics.get('solve_rate', 0)
    
    # Plot train and eval points
    ax.scatter(train_tokens, train_rate, s=400, color='#2E86AB', 
              edgecolors='black', linewidth=2, label='Train', zorder=3, marker='o')
    ax.scatter(eval_tokens, eval_rate, s=400, color='#A23B72',
              edgecolors='black', linewidth=2, label='Eval', zorder=3, marker='s')
    
    # Add labels
    ax.annotate(f'Train\n{train_rate:.1f}% @ {train_tokens:.0f}T',
               xy=(train_tokens, train_rate), xytext=(10, 10),
               textcoords='offset points', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#2E86AB', alpha=0.3))
    ax.annotate(f'Eval\n{eval_rate:.1f}% @ {eval_tokens:.0f}T',
               xy=(eval_tokens, eval_rate), xytext=(10, -20),
               textcoords='offset points', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#A23B72', alpha=0.3))
    
    ax.set_xlabel('Average Tokens per Task', fontsize=12, fontweight='bold')
    ax.set_ylabel('Solve Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Figure C: Cost vs Performance', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, frameon=True, loc='upper left')
    
    ax.set_ylim(-5, 105)
    
    fig.tight_layout()
    out_path = out_dir / 'figureC_cost_vs_performance.png'
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out_path


def get_example_tasks(
    db_path: Path, dataset_type: str = "arc2"
) -> tuple[list[str], list[bool]]:
    """Get example task IDs and their success status from database.
    
    Returns: (task_ids, success_flags)
    """
    if not db_path.exists():
        return [], []
    
    con = sqlite3.connect(str(db_path))
    cursor = con.cursor()
    
    cursor.execute("""
        SELECT task_id, solved
        FROM tasks
        WHERE solved IN (0, 1)
        ORDER BY RANDOM()
        LIMIT 10
    """)
    results = cursor.fetchall()
    con.close()
    
    task_ids = [r[0] for r in results]
    success_flags = [bool(r[1]) for r in results]
    
    return task_ids, success_flags


def load_arc_task(task_id: str, dataset_type: str = "arc2") -> dict | None:
    """Load an ARC task by ID."""
    # Try multiple possible locations
    paths = [
        Path(f"ARC-AGI-2/data/evaluation/training/{task_id}.json"),
        Path(f"ARC-AGI-2/data/training/{task_id}.json"),
        Path(f"ARC-AGI/data/training/{task_id}.json"),
        Path(f"ARC-AGI/data/evaluation/{task_id}.json"),
    ]
    
    for path in paths:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    
    return None


def make_example_tasks_figure(train_db: Path, eval_db: Path, out_dir: Path) -> Path:
    """Figure D: Example ARC Tasks showing successful and failed cases.
    
    Creates two subplots:
    - One example from training with success/failure
    - One example from evaluation with success/failure
    """
    train_task_ids, train_success = get_example_tasks(train_db, "arc2")
    eval_task_ids, eval_success = get_example_tasks(eval_db, "arc2")
    
    # Find one success and one failure from each
    train_success_id = next((t for t, s in zip(train_task_ids, train_success) if s), None)
    train_fail_id = next((t for t, s in zip(train_task_ids, train_success) if not s), None)
    eval_success_id = next((t for t, s in zip(eval_task_ids, eval_success) if s), None)
    eval_fail_id = next((t for t, s in zip(eval_task_ids, eval_success) if not s), None)
    
    fig = plt.figure(figsize=(14, 10))
    
    # Row 1: Training examples
    if train_success_id:
        task = load_arc_task(train_success_id, "arc2")
        if task:
            ax1 = plt.subplot(2, 4, 1)
            plot_grid(ax1, task['train'][0]['input'], 'Train Input')
            
            ax2 = plt.subplot(2, 4, 2)
            plot_grid(ax2, task['train'][0]['output'], 'Expected')
            
            ax3 = plt.subplot(2, 4, 3)
            if task.get('test'):
                plot_grid(ax3, task['test'][0]['input'], 'Test Input')
            else:
                ax3.text(0.5, 0.5, 'No test', ha='center', va='center')
                ax3.set_xticks([])
                ax3.set_yticks([])
            
            ax4 = plt.subplot(2, 4, 4)
            ax4.text(0.5, 0.5, '✓ Success\n(Training)', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='green',
                    bbox=dict(boxstyle='round,pad=1', facecolor='lightgreen', alpha=0.7))
            ax4.set_xticks([])
            ax4.set_yticks([])
    
    if train_fail_id:
        task = load_arc_task(train_fail_id, "arc2")
        if task:
            ax5 = plt.subplot(2, 4, 5)
            plot_grid(ax5, task['train'][0]['input'], 'Train Input')
            
            ax6 = plt.subplot(2, 4, 6)
            plot_grid(ax6, task['train'][0]['output'], 'Expected')
            
            ax7 = plt.subplot(2, 4, 7)
            if task.get('test'):
                plot_grid(ax7, task['test'][0]['input'], 'Test Input')
            else:
                ax7.text(0.5, 0.5, 'No test', ha='center', va='center')
                ax7.set_xticks([])
                ax7.set_yticks([])
            
            ax8 = plt.subplot(2, 4, 8)
            ax8.text(0.5, 0.5, '✗ Failure\n(Training)', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='red',
                    bbox=dict(boxstyle='round,pad=1', facecolor='lightcoral', alpha=0.7))
            ax8.set_xticks([])
            ax8.set_yticks([])
    
    fig.suptitle('Figure D: Example ARC Tasks - Train', fontsize=14, fontweight='bold')
    fig.tight_layout()
    
    out_path = out_dir / 'figureD_examples_train.png'
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # Make eval example figure
    fig = plt.figure(figsize=(14, 10))
    
    if eval_success_id:
        task = load_arc_task(eval_success_id, "arc2")
        if task:
            ax1 = plt.subplot(2, 4, 1)
            plot_grid(ax1, task['train'][0]['input'], 'Train Input')
            
            ax2 = plt.subplot(2, 4, 2)
            plot_grid(ax2, task['train'][0]['output'], 'Expected')
            
            ax3 = plt.subplot(2, 4, 3)
            if task.get('test'):
                plot_grid(ax3, task['test'][0]['input'], 'Test Input')
            else:
                ax3.text(0.5, 0.5, 'No test', ha='center', va='center')
                ax3.set_xticks([])
                ax3.set_yticks([])
            
            ax4 = plt.subplot(2, 4, 4)
            ax4.text(0.5, 0.5, '✓ Success\n(Evaluation)', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='green',
                    bbox=dict(boxstyle='round,pad=1', facecolor='lightgreen', alpha=0.7))
            ax4.set_xticks([])
            ax4.set_yticks([])
    
    if eval_fail_id:
        task = load_arc_task(eval_fail_id, "arc2")
        if task:
            ax5 = plt.subplot(2, 4, 5)
            plot_grid(ax5, task['train'][0]['input'], 'Train Input')
            
            ax6 = plt.subplot(2, 4, 6)
            plot_grid(ax6, task['train'][0]['output'], 'Expected')
            
            ax7 = plt.subplot(2, 4, 7)
            if task.get('test'):
                plot_grid(ax7, task['test'][0]['input'], 'Test Input')
            else:
                ax7.text(0.5, 0.5, 'No test', ha='center', va='center')
                ax7.set_xticks([])
                ax7.set_yticks([])
            
            ax8 = plt.subplot(2, 4, 8)
            ax8.text(0.5, 0.5, '✗ Failure\n(Evaluation)', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='red',
                    bbox=dict(boxstyle='round,pad=1', facecolor='lightcoral', alpha=0.7))
            ax8.set_xticks([])
            ax8.set_yticks([])
    
    fig.suptitle('Figure D: Example ARC Tasks - Eval', fontsize=14, fontweight='bold')
    fig.tight_layout()
    
    out_path_eval = out_dir / 'figureD_examples_eval.png'
    fig.savefig(out_path_eval, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate publication-quality poster figures")
    parser.add_argument("train_run_dir", type=str, help="Path to training results/<run_name>")
    parser.add_argument("eval_run_dir", type=str, help="Path to evaluation results/<run_name>")
    args = parser.parse_args()
    
    train_dir = Path(args.train_run_dir)
    eval_dir = Path(args.eval_run_dir)
    
    train_db = train_dir / "results.db"
    eval_db = eval_dir / "results.db"
    
    # Create output directory
    out_dir = train_dir / "poster"
    out_dir.mkdir(exist_ok=True)
    
    print("Generating Figure A: Main Results...")
    train_metrics = get_metrics_from_db(train_db)
    eval_metrics = get_metrics_from_db(eval_db)
    
    print(make_main_results_figure(train_metrics, eval_metrics, out_dir))
    
    print("Generating Figure B: Outcome Breakdown...")
    print(make_outcome_breakdown_figure(train_metrics, eval_metrics, out_dir))
    
    print("Generating Figure C: Cost vs Performance...")
    print(make_cost_vs_performance_figure(train_metrics, eval_metrics, out_dir))
    
    print("Generating Figure D: Example Tasks...")
    print(make_example_tasks_figure(train_db, eval_db, out_dir))
    
    print("\nAll figures generated to:", out_dir)


if __name__ == "__main__":
    main()
