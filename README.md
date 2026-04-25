# ARC-RL

This repository contains an ARC-AGI evaluation pipeline centered on `arc_eval`.
The current code evaluates LLM-generated Python programs on ARC tasks, logs each
attempt to SQLite, and includes a GPRO-style grouped sampling loop for
per-task refinement.

## Current Code Path

- `arc_eval/run.py`: baseline ARC evaluator with retry feedback on training examples.
- `arc_eval/gpro.py`: GPRO-style evaluator that samples multiple candidate programs,
  scores them on training examples, and retries from the best candidate.
- `arc_eval/prompt.py`: prompt construction and retry feedback.
- `arc_eval/evaluate.py`: grid comparison and training-example verification.
- `arc_eval/safe_exec.py`: subprocess-based execution sandbox for generated code.
- `arc_eval/db.py`: SQLite result logging.
- `arc_eval/export_grpo_data.py`: export logged rollouts for later GRPO/SFT work.
- `results/poster_analysis.py`: CSV and Markdown summaries for a run.
- `results/plot_results.py`: plot generation from run artifacts.

## Setup

From the repository root:

```bash
cd /Users/danqihu/umich/eecs545/ARC-RL
python -m pip install -r requirements.txt
```

Set the model API configuration:

```bash
export ARC_API_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
export ARC_API_KEY="<your_dashscope_api_key>"
export ARC_MODEL="qwen3.6-35b-a3b"
```

For mainland China DashScope accounts, use:

```bash
export ARC_API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

## Quick Smoke Run

```bash
RUN_NAME=gpro_smoke \
DATASET=arc1 \
SPLIT=training \
MAX_TASKS=5 \
GROUP_SIZE=2 \
GPRO_STEPS=2 \
TEMPERATURE=0.7 \
./run_gpro.sh
```

This writes artifacts under:

```text
results/gpro_smoke/
```

Key files:

- `results.db`: SQLite database of tasks and attempts.
- `gpro_samples.jsonl`: every sampled candidate and reward.
- `summary.json`: aggregate run summary.
- `poster/`: generated CSV summaries and plots.

## No-GPRO Ablation

Use this when you want the control condition without grouped sampling:

```bash
RUN_NAME=ablation_arc1_20 \
DATASET=arc1 \
SPLIT=training \
MAX_TASKS=20 \
MAX_RETRIES=1 \
TEMPERATURE=0.7 \
ARC_MODEL=qwen3.6-35b-a3b \
./run_ablation.sh
```

This uses `arc_eval.run`, not `arc_eval.gpro`. It now accepts the same model
configuration and writes `summary.json`, `results.db`, logs, poster CSVs, and
plots under `results/<run_name>/`.

For the cleanest ablation, compare:

- No GPRO: `run_ablation.sh` with `MAX_RETRIES=1`.
- Single-sample GPRO-style path: `run_gpro.sh` with `GROUP_SIZE=1` and `GPRO_STEPS=1`.
- Full GPRO inference: `run_gpro.sh` with larger `GROUP_SIZE` and `GPRO_STEPS`.

## GRPO Rollout Collection

The current repository does not yet perform true online GRPO weight updates.
It can now collect prompt/response/reward rollouts needed for later GRPO or SFT:

```bash
RUN_NAME=grpo_rollout_arc1_20 \
DATASET=arc1 \
SPLIT=training \
MAX_TASKS=20 \
GROUP_SIZE=4 \
GPRO_STEPS=3 \
TEMPERATURE=0.8 \
LOG_SAMPLE_TEXT=1 \
./run_gpro.sh
```

Then export training data:

```bash
python -m arc_eval.export_grpo_data results/grpo_rollout_arc1_20
```

See `GRPO_TRAINING.md` for the recommended separation between no-GPRO
ablation, GPRO inference, and an eventual GRPO-trained checkpoint.

## Direct Commands

Run GPRO directly:

```bash
python -m arc_eval.gpro \
  --dataset arc1 \
  --split training \
  --run-name gpro_arc1_train_20 \
  --model qwen3.6-35b-a3b \
  --max-tasks 20 \
  --group-size 4 \
  --gpro-steps 5 \
  --temperature 0.8 \
  --timeout 120
```

Run the baseline evaluator:

```bash
python -m arc_eval.run \
  --dataset arc1 \
  --split training \
  --run-name baseline_arc1_train_20 \
  --max-tasks 20 \
  --max-retries 2 \
  --temperature 0.0 \
  --timeout 120
```

Summarize an existing run:

```bash
python -m arc_eval.report results/<run_name>
python results/poster_analysis.py results/<run_name>
python results/plot_results.py results/<run_name>
```

## Existing Result Anchors

Recorded runs currently show:

- `results/test_qwen36_35b_20`: `arc1/training`, 20 tasks, group size 1,
  1 step, 10/20 solved.
- `results/mid_qwen36`: `arc1/training`, 20 tasks, group size 4,
  5 steps, 15/20 solved.
- `results/arc2_train_100`: `arc2/training`, 100 tasks, group size 2,
  2 steps, 48/100 solved.

These are useful baselines for the next experiments.

## Recommended Next Work

1. Reproduce the existing anchors with fixed run names and logs.
2. Add task-level failure analysis: separate extraction failures, train failures,
   test execution failures, and wrong outputs.
3. Improve the reward used in `arc_eval/gpro.py`; the current reward is mostly
   training pass/fail plus cell accuracy, so it is still sparse.
4. Add a reranker/verifier pass over all candidates instead of immediately using
   only the max training reward candidate.
5. Convert successful and failed candidate traces into data for later policy
   tuning or RL-style preference optimization.
