#!/usr/bin/env bash
# Run ARC with Qwen3.5 + GPRO-style group sampling.

set -euo pipefail

PYTHON=${PYTHON:-python}
cd "$(dirname "$0")"

export PYTHONUNBUFFERED=1

RUN_NAME=${RUN_NAME:-gpro_qwen35_$(date +%Y%m%d_%H%M%S)}
DATASET=${DATASET:-arc1}
SPLIT=${SPLIT:-training}
MODEL=${MODEL:-${ARC_MODEL:-qwen3.5-plus}}
GROUP_SIZE=${GROUP_SIZE:-4}
GPRO_STEPS=${GPRO_STEPS:-3}
TEMPERATURE=${TEMPERATURE:-0.7}
TIMEOUT=${TIMEOUT:-120}
MAX_API_RETRIES=${MAX_API_RETRIES:-2}
MAX_TOKENS=${MAX_TOKENS:-400}
TASK_START=${TASK_START:-}
TASK_END=${TASK_END:-}
MAX_TASKS=${MAX_TASKS:-}
LOG_SAMPLE_TEXT=${LOG_SAMPLE_TEXT:-0}

mkdir -p results

CMD=(
  "$PYTHON" -m arc_eval.gpro
  --dataset "$DATASET"
  --split "$SPLIT"
  --run-name "$RUN_NAME"
  --model "$MODEL"
  --group-size "$GROUP_SIZE"
  --gpro-steps "$GPRO_STEPS"
  --temperature "$TEMPERATURE"
  --timeout "$TIMEOUT"
  --max-api-retries "$MAX_API_RETRIES"
  --max-tokens "$MAX_TOKENS"
)

if [[ -n "$MAX_TASKS" ]]; then
  CMD+=(--max-tasks "$MAX_TASKS")
fi

if [[ -n "$TASK_START" ]]; then
  CMD+=(--task-start "$TASK_START")
fi

if [[ -n "$TASK_END" ]]; then
  CMD+=(--task-end "$TASK_END")
fi

if [[ "$LOG_SAMPLE_TEXT" == "1" ]]; then
  CMD+=(--log-sample-text)
fi

echo "=== ARC GPRO Run ==="
echo "Run name:     $RUN_NAME"
echo "Dataset:      $DATASET/$SPLIT"
echo "Model:        $MODEL"
echo "Group size:   $GROUP_SIZE"
echo "GPRO steps:   $GPRO_STEPS"
echo "Temperature:  $TEMPERATURE"
echo "Timeout:      ${TIMEOUT}s"
echo "API retries:  $MAX_API_RETRIES"
echo "Max tokens:   $MAX_TOKENS"
echo "Task start:   ${TASK_START:-1}"
echo "Task end:     ${TASK_END:-all}"
echo "Log text:     $LOG_SAMPLE_TEXT"

if "${CMD[@]}" 2>&1 | tee -a "results/${RUN_NAME}.log"; then
  echo ""
  echo "=== Building poster analysis files ==="
  "$PYTHON" results/poster_analysis.py "results/${RUN_NAME}" \
    2>&1 | tee -a "results/${RUN_NAME}.log"

  echo ""
  echo "Done. See results/${RUN_NAME}/poster"
else
  echo ""
  echo "Run failed before results DB generation. Skipping poster analysis."
  exit 1
fi
