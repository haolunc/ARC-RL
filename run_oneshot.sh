#!/usr/bin/env bash
# Run ARC datasets in one-shot mode (no retry).
set -e

PYTHON=python
cd "$(dirname "$0")"

mkdir -p results

echo "=== One-shot evaluation: ARC1 training ==="
$PYTHON -m arc_eval.run \
    --dataset arc1 --split training \
    --max-retries 1 --run-name oneshot_arc1_training \
    2>&1 | tee -a results/oneshot_arc1_training.log

echo ""
echo "=== One-shot evaluation: ARC1 evaluation ==="
$PYTHON -m arc_eval.run \
    --dataset arc1 --split evaluation \
    --max-retries 1 --run-name oneshot_arc1_evaluation \
    2>&1 | tee -a results/oneshot_arc1_evaluation.log

echo ""
echo "=== One-shot evaluation: ARC2 evaluation ==="
$PYTHON -m arc_eval.run \
    --dataset arc2 --split evaluation \
    --max-retries 1 --run-name oneshot_arc2_evaluation \
    2>&1 | tee -a results/oneshot_arc2_evaluation.log

echo ""
echo "=== All done! ==="