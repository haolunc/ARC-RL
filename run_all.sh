#!/bin/bash
# Run all ARC evaluations
# Usage: ./run_all.sh

set -e

PYTHON=python
cd "$(dirname "$0")"

mkdir -p results

echo "=========================================="
echo " ARC-AGI Full Evaluation"
echo " Started: $(date)"
echo "=========================================="

# ARC-AGI-1 training
echo ""
echo ">>> ARC-AGI-1 Training"
$PYTHON -m arc_eval.run \
    --dataset arc1 --split training \
    --run-name arc1_training \
    2>&1 | tee -a results/arc1_training.log

# ARC-AGI-1 evaluation
echo ""
echo ">>> ARC-AGI-1 Evaluation"
$PYTHON -m arc_eval.run \
    --dataset arc1 --split evaluation \
    --run-name arc1_evaluation \
    2>&1 | tee -a results/arc1_evaluation.log

# ARC-AGI-2 training
echo ""
echo ">>> ARC-AGI-2 Training"
$PYTHON -m arc_eval.run \
    --dataset arc2 --split training \
    --run-name arc2_training \
    2>&1 | tee -a results/arc2_training.log

# ARC-AGI-2 evaluation
echo ""
echo ">>> ARC-AGI-2 Evaluation"
$PYTHON -m arc_eval.run \
    --dataset arc2 --split evaluation \
    --run-name arc2_evaluation \
    2>&1 | tee -a results/arc2_evaluation.log

echo ""
echo "=========================================="
echo " All evaluations complete!"
echo " Finished: $(date)"
echo "=========================================="