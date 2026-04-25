#!/usr/bin/env bash
# Run the no-GPRO baseline ablation with the same result layout as GPRO runs.

set -euo pipefail

PYTHON=${PYTHON:-python}
cd "$(dirname "$0")"

export PYTHONUNBUFFERED=1

RUN_NAME=${RUN_NAME:-ablation_no_gpro_$(date +%Y%m%d_%H%M%S)}
DATASET=${DATASET:-arc1}
SPLIT=${SPLIT:-training}
MODEL=${MODEL:-${ARC_MODEL:-qwen3.6-35b-a3b}}
MAX_RETRIES=${MAX_RETRIES:-1}
TEMPERATURE=${TEMPERATURE:-0.7}
TIMEOUT=${TIMEOUT:-120}
MAX_TOKENS=${MAX_TOKENS:-400}
MAX_TASKS=${MAX_TASKS:-}

mkdir -p results

CMD=(
  "$PYTHON" -m arc_eval.run
  --dataset "$DATASET"
  --split "$SPLIT"
  --run-name "$RUN_NAME"
  --model "$MODEL"
  --max-retries "$MAX_RETRIES"
  --temperature "$TEMPERATURE"
  --timeout "$TIMEOUT"
  --max-tokens "$MAX_TOKENS"
)

if [[ -n "$MAX_TASKS" ]]; then
  CMD+=(--max-tasks "$MAX_TASKS")
fi

echo "=== ARC No-GPRO Ablation ==="
echo "Run name:     $RUN_NAME"
echo "Dataset:      $DATASET/$SPLIT"
echo "Model:        $MODEL"
echo "Max retries:  $MAX_RETRIES"
echo "Temperature:  $TEMPERATURE"
echo "Timeout:      ${TIMEOUT}s"
echo "Max tokens:   $MAX_TOKENS"

if "${CMD[@]}" 2>&1 | tee -a "results/${RUN_NAME}.log"; then
  echo ""
  echo "=== Building analysis files ==="
  "$PYTHON" results/poster_analysis.py "results/${RUN_NAME}" \
    2>&1 | tee -a "results/${RUN_NAME}.log"

  echo ""
  echo "=== Building plots ==="
  "$PYTHON" results/plot_results.py "results/${RUN_NAME}" \
    2>&1 | tee -a "results/${RUN_NAME}.log"

  echo ""
  echo "Done. See results/${RUN_NAME}/poster"
else
  echo ""
  echo "Run failed before results DB generation. Skipping analysis."
  exit 1
fi
