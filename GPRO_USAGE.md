# Qwen3.5 + GPRO ARC Pipeline

This repository now includes a GPRO-style ARC solver:

- Runner: `python -m arc_eval.gpro`
- Convenience script: `./run_gpro.sh`
- Poster analysis: `python results/poster_analysis.py results/<run_name>`

## 1) Setup

Set your API key:

```bash
export ARC_API_KEY="<your_key>"
```

### Official Qwen API setup (recommended)

1. Create an account on Qwen/Alibaba Cloud Model Studio (DashScope).
2. Enable billing / purchase credits in the console.
3. Create an API key.
4. Set the endpoint + key in your shell:

```bash
# International endpoint (OpenAI-compatible)
export ARC_API_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# If your account is on mainland China, use this instead:
# export ARC_API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

export ARC_API_KEY="<dashscope_api_key>"
export ARC_MODEL="Qwen/Qwen3.5-32B-Instruct"
```

Optional model override (repo default is now qwen3.5-plus):

```bash
export ARC_MODEL="qwen3.5-plus"
```

## 2) Quick Smoke Run

```bash
RUN_NAME=gpro_smoke \
DATASET=arc1 \
SPLIT=training \
MAX_TASKS=5 \
GROUP_SIZE=3 \
GPRO_STEPS=2 \
./run_gpro.sh
```

## 3) Full Command (direct module)

```bash
python -m arc_eval.gpro \
  --dataset arc1 \
  --split training \
  --run-name gpro_qwen35_arc1_train \
  --model Qwen/Qwen3.5-32B-Instruct \
  --group-size 4 \
  --gpro-steps 3 \
  --temperature 0.7 \
  --timeout 120
```

## 4) Outputs

Under `results/<run_name>/`:

- `results.db`: task/attempt logs
- `gpro_samples.jsonl`: all group samples with rewards
- `summary.json`: run configuration + aggregate summary
- `poster/` (after analysis):
  - `poster_report.md`
  - `poster_metrics.csv`
  - `poster_outcomes.csv`
  - `poster_step_rewards.csv`

## 5) Poster-ready figures to build from CSVs

- Solve rate bar chart (`poster_metrics.csv`)
- Outcome pie/bar (`poster_outcomes.csv`)
- Reward progression across GPRO steps (`poster_step_rewards.csv`)

## 6) Quick summary command

```bash
python -m arc_eval.report results/<run_name>
```

## 7) Generate result plots

```bash
python results/plot_results.py results/<run_name>
```

This writes PNG files under `results/<run_name>/poster/`:

- `plot_task_outcomes.png`
- `plot_attempt_outcomes.png`
- `plot_step_rewards.png` (when step data exists)
- `plot_success_by_step.png` (successes at step 1/2/3...)
- `plot_task_runtime_hist.png`
- `plot_tokens_vs_accuracy.png`
- `plot_reward_histogram.png`

## 8) Recommended larger runs

Fast baseline (20 tasks):

```bash
RUN_NAME=run20_fast \
MAX_TASKS=20 \
GROUP_SIZE=1 \
GPRO_STEPS=1 \
ARC_MODEL=qwen3.6-35b-a3b \
./run_gpro.sh
```

Balanced (50 tasks):

```bash
RUN_NAME=run50_balanced \
MAX_TASKS=50 \
GROUP_SIZE=2 \
GPRO_STEPS=2 \
TEMPERATURE=0.7 \
ARC_MODEL=qwen3.6-35b-a3b \
./run_gpro.sh
```

Bigger benchmark (100 tasks):

```bash
RUN_NAME=run100_benchmark \
MAX_TASKS=100 \
GROUP_SIZE=2 \
GPRO_STEPS=2 \
TEMPERATURE=0.7 \
ARC_MODEL=qwen3.6-35b-a3b \
./run_gpro.sh
```

After each run:

```bash
python -m arc_eval.report results/<run_name>
python results/poster_analysis.py results/<run_name>
python results/plot_results.py results/<run_name>
```
