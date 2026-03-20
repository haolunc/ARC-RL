# Deploy vLLM on Great Lakes (Build from Source)

This guide covers building vLLM from source and deploying Qwen3.5-35B-A3B-GPTQ-Int4 on Great Lakes HPC using a uv venv (no Singularity).

> For the Singularity-based deployment, see [deploy_singularity.md](deploy_singularity.md).

## Prerequisites

- Great Lakes account with `eecs545w26_class` allocation
- Access to `spgpu` partition (A40 GPUs)

## Step 1: Install uv

On the login node, download the latest `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This installs `uv` to `~/.local/bin/`. Make sure it's in your `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
```

## Step 2: Clone vLLM Source

```bash
cd ~
git clone https://github.com/vllm-project/vllm.git
cd vllm
```

## Step 3: Build vLLM from Source

Building vLLM compiles CUDA kernels, which requires a GPU node. Create `~/build_vllm.sh`:

```bash
#!/bin/bash
#SBATCH --account=eecs545w26_class
#SBATCH --job-name=build_vllm
#SBATCH --partition=spgpu
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --time=02:00:00

module load gcc/13 cuda/12.8 python/3.12.1

# Create venv (must use module python for dev headers)
if [ ! -f ~/vllm_from_source/pyvenv.cfg ]; then
    uv venv ~/vllm_from_source --python $(which python3)
fi
source ~/vllm_from_source/bin/activate

# Install torch first (needed for build)
uv pip install torch --index-url https://download.pytorch.org/whl/cu128

cd ~/vllm
python use_existing_torch.py
uv pip install -r requirements/build.txt

# Use more parallel compile jobs
export MAX_JOBS=8
uv pip install --no-build-isolation -e .
```

Submit:

```bash
mkdir -p ~/logs
sbatch ~/build_vllm.sh
```

> **Important**: Must use `module load python/3.12.1` (not the system Python) because the module Python includes development headers (`Python.h`) required by CMake. The system Python at `/usr/bin/python3.12` does not have `-dev` headers installed.

> **Build time**: ~55 minutes with 8 CPUs on an A40 node. The build compiles CUDA kernels for flashinfer, attention backends, etc. Set `--time` to at least 2 hours.

Monitor progress:

```bash
# Check job status
sacct -j <jobid> --format=JobID,State,Elapsed -n

# Watch build logs
tail -f ~/logs/build_vllm_<jobid>.err
```

## Step 4: Download the Model

Install huggingface tools and download the model to scratch:

```bash
# Get an interactive session (no GPU needed)
srun --account=eecs545w26_class --partition=standard --mem=16G --cpus-per-task=2 --time=02:00:00 --pty bash

module load python/3.12.1
source ~/vllm_from_source/bin/activate

# Install HF tools
uv pip install huggingface_hub hf_transfer

# Set cache to scratch (home has limited space)
SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
export HF_HOME=${SCRATCH}/qwen35-deploy/hf_cache
export HF_HUB_ENABLE_HF_TRANSFER=1  # faster downloads

# Download model
huggingface-cli download Qwen/Qwen3.5-35B-A3B-GPTQ-Int4
```

## Step 5: Deploy vLLM Service

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

module load gcc/13 cuda/12.8 python/3.12.1
source ~/vllm_from_source/bin/activate

SCRATCH=/scratch/eecs545w26_class_root/eecs545w26_class/<username>
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

> **Startup time**: ~20-25 minutes total (model weight loading ~16 min, torch.compile ~30s, CUDA graph capture ~10s).

## Step 6: SSH Tunneling

The vLLM service runs on an internal compute node (e.g. `gl1529`). To access it from your local machine, set up an SSH tunnel.

First, find the node name:

```bash
# On Great Lakes
squeue -u $USER
# Or check the log
grep "Node:" ~/logs/qwen35-35b-a3b_<jobid>.out
```

Then on your **local machine**, create a tunnel:

```bash
# Replace <node> with the actual node name (e.g. gl1529)
ssh -L 8000:<node>:8000 <username>@greatlakes.arc-ts.umich.edu
```

Now you can access the API at `http://localhost:8000` from your local machine.

For a persistent tunnel in the background:

```bash
ssh -fNL 8000:<node>:8000 <username>@greatlakes.arc-ts.umich.edu
```

## Step 7: Verify the Service

Test from either the login node (`curl http://<node>:8000/...`) or your local machine after tunneling (`curl http://localhost:8000/...`):

```bash
# Check model is loaded
curl -s http://localhost:8000/v1/models | python3 -m json.tool

# Test reasoning
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4",
    "messages": [{"role": "user", "content": "What is 25 * 37? Think step by step."}],
    "max_tokens": 1024
  }'

# Test tool calling
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4",
    "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City name"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
          },
          "required": ["location"]
        }
      }
    }],
    "max_tokens": 512
  }'
```

Expected behavior:
- **Reasoning**: Response has `reasoning` field with chain-of-thought, `content` field with final answer
- **Tool call**: Response has `tool_calls` array with function name and arguments, `finish_reason` is `"tool_calls"`

## Notes

- **Why build from source?** The nightly wheel may not support the latest models (e.g. Qwen3.5). Building from the latest `main` branch ensures all model architectures are available.
- **GPU memory**: Model weights use ~21 GiB on A40 (46 GiB total). With `gpu-memory-utilization=0.90` and fp8 KV cache, ~390K tokens of KV cache are available. With `--max-num-batched-tokens 16384`, supports ~24 concurrent requests and ~600 tokens/s generation throughput.
- **GPU quota**: Only one GPU job per account can run at a time (`AssocGrpGRES`). Cancel other GPU jobs before deploying.
- **Logs**: Check `~/logs/qwen35-35b-a3b_<jobid>.out` and `.err` for startup progress.