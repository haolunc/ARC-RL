


ssh haolunca@greatlakes.arc-ts.umich.edu


/scratch/eecs545w26_class_root/eecs545w26_class/haolunca



```bash

# 加载 uv 和 CUDA
module load uv/0.5.1
module load cuda/12.6   # 确保 CUDA >= 12.1

# 创建 venv（uv 会自动下载 Python 3.11）
uv venv --python 3.11 .venv
source .venv/bin/activate
```

### Step 2：安装 vLLM

**重要：Qwen3.5 需要 vLLM nightly 版本（截至 2026-03）。**

```bash
# 安装最新 nightly（推荐）+ huggingface 工具
uv pip install vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
uv pip install huggingface_hub hf_transfer
```

### Step 3：下载模型

根据你选择的方案，下载对应模型。建议下载到集群的共享存储或 scratch 目录：

```bash
export HF_HOME=/scratch/eecs545w26_class_root/eecs545w26_class/haolunca/qwen35-deploy/hf_cache  # 或集群推荐的缓存路径
export HF_HUB_ENABLE_HF_TRANSFER=1  # 加速下载

# === 方案 A：35B-A3B GPTQ-Int4 ===
hf download Qwen/Qwen3.5-35B-A3B-GPTQ-Int4

# === 方案 B：9B BF16（全精度）===
hf download Qwen/Qwen3.5-9B

# === 方案 C：9B FP8 ===
# 官方 FP8 checkpoint（如果有的话），或使用 BF16 + vLLM 在线量化
huggingface-cli download Qwen/Qwen3.5-9B

# === 方案 D：4B BF16 ===
huggingface-cli download Qwen/Qwen3.5-4B
```

> **提示：** 如果集群无法直接访问 HuggingFace，可以：
> 1. 设置 `export VLLM_USE_MODELSCOPE=true` 从 ModelScope 下载
> 2. 在有网络的节点上先下载，再拷贝到集群
> 3. 使用 `huggingface-cli download --local-dir /path/to/model` 指定本地路径

### Step 4：编写 SLURM 脚本

以下提供两个最推荐方案的 SLURM 脚本。

#### 方案 A 的 SLURM 脚本（35B-A3B GPTQ-Int4）

```bash
#!/bin/bash
#SBATCH --account=eecs545w26_class
#SBATCH --job-name=qwen35-35b-a3b
#SBATCH --partition=spgpu          # 改成你集群的 GPU 分区名
#SBATCH --gres=gpu:a40:1         # 申请 1 张 A40
#SBATCH --cpus-per-task=4        # vLLM 需要多核做 tokenization
#SBATCH --mem=48G                # 系统内存，模型加载时需要
#SBATCH --time=8:00:00          # 根据需要调整
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# 加载环境
module load uv/0.5.1
module load cuda/12.6
source /scratch/eecs545w26_class_root/eecs545w26_class/haolunca/qwen35-deploy/.venv/bin/activate


echo "Node: $SLURMD_NODENAME"
echo "GPUs allocated: $CUDA_VISIBLE_DEVICES"
nvidia-smi

# 设置缓存路径
export HF_HOME=/scratch/eecs545w26_class_root/eecs545w26_class/haolunca/qwen35-deploy/hf_cache
export CUDA_VISIBLE_DEVICES=0

# 创建日志目录
mkdir -p logs

# 启动 vLLM 服务
vllm serve Qwen/Qwen3.5-35B-A3B-GPTQ-Int4 \
    --port 8000 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1 \
    --max-model-len 65536 \
    --gpu-memory-utilization 0.78 \
    --kv-cache-dtype fp8 \
    --quantization gptq_marlin \
    --dtype bfloat16 \
    --max-num-batched-tokens 2096 \
    --enable-prefix-caching \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder \
    --trust-remote-code
```