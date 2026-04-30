#!/usr/bin/env bash
#SBATCH --job-name=arc_cases_25_100
#SBATCH --account=eecs545w26_class
#SBATCH --partition=gpu
#SBATCH --output=slurm_logs/%x_%j.out
#SBATCH --error=slurm_logs/%x_%j.err
#SBATCH --time=08:00:00
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail

REPO_DIR="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO_DIR"
mkdir -p slurm_logs results

export PYTHONUNBUFFERED=1

# Keep API secrets outside this file. Set ARC_API_KEY before sbatch, or pass it
# with sbatch --export=ALL,ARC_API_KEY=...
: "${ARC_API_KEY:?Please set ARC_API_KEY before submitting this job.}"

export ARC_API_BASE_URL="${ARC_API_BASE_URL:-https://dashscope-us.aliyuncs.com/compatible-mode/v1}"
export ARC_MODEL="${ARC_MODEL:-qwen3.6-35b-a3b}"

RUN_NAME="${RUN_NAME:-arc_cases_25_100_$(date +%Y%m%d_%H%M%S)}"
DATASET="${DATASET:-arc1}"
SPLIT="${SPLIT:-evaluation}"
TASK_START="${TASK_START:-227}"
TASK_END="${TASK_END:-300}"
GROUP_SIZE="${GROUP_SIZE:-4}"
GPRO_STEPS="${GPRO_STEPS:-3}"
TEMPERATURE="${TEMPERATURE:-0.7}"
TIMEOUT="${TIMEOUT:-120}"
MAX_API_RETRIES="${MAX_API_RETRIES:-1}"
MAX_TOKENS="${MAX_TOKENS:-400}"
LOG_SAMPLE_TEXT="${LOG_SAMPLE_TEXT:-0}"

echo "=== Submitting ARC cases ${TASK_START}-${TASK_END} ==="
echo "Started:      $(date)"
echo "Host:         $(hostname)"
echo "Workdir:      $(pwd)"
echo "Run name:     ${RUN_NAME}"
echo "Dataset:      ${DATASET}/${SPLIT}"
echo "Model:        ${ARC_MODEL}"
echo "Group size:   ${GROUP_SIZE}"
echo "GPRO steps:   ${GPRO_STEPS}"
echo "Temperature:  ${TEMPERATURE}"
echo "Timeout:      ${TIMEOUT}s"
echo "Max tokens:   ${MAX_TOKENS}"

RUN_NAME="${RUN_NAME}" \
DATASET="${DATASET}" \
SPLIT="${SPLIT}" \
TASK_START="${TASK_START}" \
TASK_END="${TASK_END}" \
GROUP_SIZE="${GROUP_SIZE}" \
GPRO_STEPS="${GPRO_STEPS}" \
TEMPERATURE="${TEMPERATURE}" \
TIMEOUT="${TIMEOUT}" \
MAX_API_RETRIES="${MAX_API_RETRIES}" \
MAX_TOKENS="${MAX_TOKENS}" \
LOG_SAMPLE_TEXT="${LOG_SAMPLE_TEXT}" \
./run_gpro.sh

echo "Finished:     $(date)"
