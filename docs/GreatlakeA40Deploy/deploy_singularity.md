# Deploy vLLM on Great Lakes with Singularity

This guide covers deploying Qwen3.5-35B-A3B-GPTQ-Int4 on Great Lakes HPC using a pre-built Singularity container.

## Prerequisites

- Great Lakes account with `eecs545w26_class` allocation
- Access to `spgpu` partition (A40 GPUs)

## Step 1: Pull the vLLM Singularity Image

Submit a job to pull the official vLLM Docker image as a Singularity `.sif` file. This takes a while (~30 min+), so we use an sbatch script.

Create `~/pull_vllm_sif.sh`:

```bash
#!/bin/bash
#SBATCH --account=eecs545w26_class
#SBATCH --job-name=pull-vllm-sif
#SBATCH --partition=standard
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=4:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

mkdir -p logs

module load singularity

SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
mkdir -p ${SCRATCH}/qwen35-deploy

singularity pull ${SCRATCH}/qwen35-deploy/vllm-nightly.sif docker://vllm/vllm-openai:latest
```

Submit:

```bash
sbatch ~/pull_vllm_sif.sh
```

> The image is ~6GB+. `standard` partition does not need GPU, but the download and conversion takes time, so `--time` is set to 4 hours.

## Step 2: Download the Model

Make sure the model is cached locally before serving. You can do this inside an interactive session or a batch job:

```bash
srun --account=eecs545w26_class --partition=standard --mem=16G --cpus-per-task=2 --time=02:00:00 --pty bash

module load singularity

SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
export HF_HOME=${SCRATCH}/qwen35-deploy/hf_cache

singularity exec ${SCRATCH}/qwen35-deploy/vllm-nightly.sif \
    huggingface-cli download Qwen/Qwen3.5-35B-A3B-GPTQ-Int4
```

## Step 3: Deploy vLLM Service

Create `~/deploy_vllm.sh`:

```bash
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

# Paths
SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
SIF=${SCRATCH}/qwen35-deploy/vllm-nightly.sif
HF_CACHE=${SCRATCH}/qwen35-deploy/hf_cache

# Create log directory
mkdir -p logs

module load singularity

echo "Node: $SLURMD_NODENAME"
echo "GPUs allocated: $CUDA_VISIBLE_DEVICES"
nvidia-smi

# Launch vLLM inside Singularity container
singularity exec --nv \
    --bind ${HF_CACHE}:/root/.cache/huggingface \
    ${SIF} \
    vllm serve Qwen/Qwen3.5-35B-A3B-GPTQ-Int4 \
        --port 8000 \
        --host 0.0.0.0 \
        --tensor-parallel-size 1 \
        --max-model-len 131072 \
        --gpu-memory-utilization 0.90 \
        --kv-cache-dtype fp8 \
        --quantization gptq_marlin \
        --dtype bfloat16 \
        --max-num-batched-tokens 16384 \
        --enable-prefix-caching \
        --reasoning-parser qwen3 \
        --enable-auto-tool-choice \
        --tool-call-parser hermes \
        --trust-remote-code
```

Submit:

```bash
sbatch ~/deploy_vllm.sh
```

## Step 4: Verify the Service

Check job status:

```bash
squeue -u $USER
```

Once running, find the node name from the output (e.g. `gl1520`), then test:

```bash
# Check model is loaded
curl -s http://<node>:8000/v1/models | python3 -m json.tool

# Test chat completion
curl -s http://<node>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'

# Test tool calling
curl -s http://<node>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4",
    "messages": [{"role": "user", "content": "What is the weather in SF?"}],
    "tools": [{"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}],
    "max_tokens": 200
  }'
```

## Notes

- **GPU memory**: Model weights use ~21 GiB on A40 (46 GiB total). With `gpu-memory-utilization=0.90`, ~17 GiB is available for KV cache.
- **KV cache**: ~390K tokens with fp8 KV cache. At `max-model-len=131072` (128K), supports ~24 concurrent requests with `--max-num-batched-tokens 16384`, achieving ~600 tokens/s generation throughput.
- **Startup time**: ~6 minutes (weight download from HF cache + GPU loading + CUDA graph compilation).
- **GPU quota**: Only one GPU job per account can run at a time (`AssocGrpGRES`). Cancel other GPU jobs before deploying.
- **Logs**: Check `~/logs/qwen35-35b-a3b_<jobid>.out` and `.err` for startup progress.
- **Service endpoint**: `http://<node>:8000/v1/` — OpenAI-compatible API. Use the node name from `squeue` output.
