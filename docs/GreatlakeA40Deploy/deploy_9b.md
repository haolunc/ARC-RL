# Deploy Qwen3.5-9B on Great Lakes

Follows the same workflow as [deploy_singularity.md](deploy_singularity.md) (image pull, model download, verify, SSH tunnel). This page only covers what differs for the 9B model.

## Hardware: NVIDIA A40

| Spec | Value |
|---|---|
| VRAM | 48 GB GDDR6 |
| Architecture | Ampere (Compute Capability 8.6) |
| BF16 / FP16 | Fully supported |
| FP8 | No native w8a8 (needs CC >= 8.9). KV cache FP8 (`--kv-cache-dtype fp8`) is supported |

**VRAM budget**: ~18 GiB weights + ~2-4 GiB overhead = ~22 GiB. Remaining ~26 GiB for KV cache — 128K+ context with fp8 KV cache.

## Download Model

Replace the model name in the download step:

```bash
huggingface-cli download Qwen/Qwen3.5-9B
```

## Deploy Script

Create `~/deploy_vllm_9b.sh`:

```bash
#!/bin/bash
#SBATCH --account=eecs545w26_class
#SBATCH --job-name=qwen35-9b
#SBATCH --partition=spgpu
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=8:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
SIF=${SCRATCH}/qwen35-deploy/vllm-nightly.sif
HF_CACHE=${SCRATCH}/qwen35-deploy/hf_cache

mkdir -p logs
module load singularity

echo "Node: $SLURMD_NODENAME"
echo "GPUs allocated: $CUDA_VISIBLE_DEVICES"
nvidia-smi

singularity exec --nv \
    --bind ${HF_CACHE}:/root/.cache/huggingface \
    ${SIF} \
    vllm serve Qwen/Qwen3.5-9B \
        --port 8000 \
        --host 0.0.0.0 \
        --tensor-parallel-size 1 \
        --max-model-len 131072 \
        --gpu-memory-utilization 0.90 \
        --kv-cache-dtype fp8 \
        --enable-prefix-caching \
        --reasoning-parser qwen3 \
        --enable-auto-tool-choice \
        --tool-call-parser qwen3_coder \
        --chat-template-content-format string \
        --trust-remote-code
```

**vs 35B-A3B**: No `--quantization`, `--dtype`, `--max-num-batched-tokens` needed.
## Notes

- 9B defaults to **thinking off**. The `--reasoning-parser qwen3` flag enables parsing thinking output. Per-request control: `"extra_body": {"chat_template_kwargs": {"enable_thinking": true/false}}`.
- Thinking mode consumes significant output tokens — disable for simple tasks.
