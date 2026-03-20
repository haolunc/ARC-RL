#!/bin/bash
#SBATCH --account=eecs545w26_class
#SBATCH --job-name=qwen35-35b-a3b
#SBATCH --partition=spgpu
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=8:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

module load gcc/13 cuda/12.8 python/3.12.1
source ~/vllm_from_source/bin/activate

SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/haolunca
export HF_HOME=${SCRATCH}/qwen35-deploy/hf_cache

mkdir -p logs

vllm serve Qwen/Qwen3.5-35B-A3B-GPTQ-Int4 \
    --port 8000 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1 \
    --max-model-len 131072 \
    --gpu-memory-utilization 0.90 \
    --kv-cache-dtype fp8 \
    --quantization gptq_marlin \
    --dtype bfloat16 \
    --max-num-batched-tokens 32768 \
    --enable-prefix-caching \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --trust-remote-code
