#!/usr/bin/env bash
# Run all ARC datasets in one-shot mode (no retry).
set -e

PYTHON="/opt/homebrew/Caskroom/miniforge/base/envs/eecs545/bin/python"
cd "$(dirname "$0")"

echo "=== One-shot evaluation: ARC1 training ==="
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc1 --split training \
    --max-retries 1 --run-name oneshot_arc1_training

echo ""
echo "=== One-shot evaluation: ARC1 evaluation ==="
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc1 --split evaluation \
    --max-retries 1 --run-name oneshot_arc1_evaluation

echo ""
echo "=== One-shot evaluation: ARC2 evaluation ==="
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc2 --split evaluation \
    --max-retries 1 --run-name oneshot_arc2_evaluation

echo ""
echo "=== All done! ==="
