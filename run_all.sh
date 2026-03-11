#!/bin/bash
# Run all ARC evaluations with caffeinate (prevents macOS sleep)
# Usage: ./run_all.sh

set -e

PYTHON="/opt/homebrew/Caskroom/miniforge/base/envs/eecs545/bin/python"
cd "$(dirname "$0")"

echo "=========================================="
echo " ARC-AGI Full Evaluation"
echo " Started: $(date)"
echo "=========================================="

# ARC-AGI-1 training (400 tasks)
echo ""
echo ">>> ARC-AGI-1 Training (400 tasks)"
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc1 --split training \
    --run-name arc1_training \
    2>&1 | tee -a results/arc1_training.log

# ARC-AGI-1 evaluation (400 tasks)
echo ""
echo ">>> ARC-AGI-1 Evaluation (400 tasks)"
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc1 --split evaluation \
    --run-name arc1_evaluation \
    2>&1 | tee -a results/arc1_evaluation.log

# ARC-AGI-2 training (1000 tasks)
echo ""
echo ">>> ARC-AGI-2 Training (1000 tasks)"
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc2 --split training \
    --run-name arc2_training \
    2>&1 | tee -a results/arc2_training.log

# ARC-AGI-2 evaluation (120 tasks)
echo ""
echo ">>> ARC-AGI-2 Evaluation (120 tasks)"
caffeinate -dims $PYTHON -m arc_eval.run \
    --dataset arc2 --split evaluation \
    --run-name arc2_evaluation \
    2>&1 | tee -a results/arc2_evaluation.log

echo ""
echo "=========================================="
echo " All evaluations complete!"
echo " Finished: $(date)"
echo "=========================================="
