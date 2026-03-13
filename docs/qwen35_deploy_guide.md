# Qwen3.5 部署指南：单卡 A40 + vLLM + SLURM

## 一、硬件约束分析

**NVIDIA A40 关键参数：**
- VRAM：48 GB GDDR6
- 架构：Ampere（Compute Capability 8.6）
- FP8 支持：**不原生支持 w8a8**（需 CC ≥ 8.9，即 Ada/Hopper），但 vLLM ≥ 0.9.0 通过 FP8 Marlin 支持 **w8a16** 模式
- BF16 / FP16：完全支持

**VRAM 预算公式：**

```
总 VRAM = 模型权重 + KV Cache + 运行时开销（~2-4 GB）
```

Qwen3.5 采用 Gated DeltaNet 混合架构（3:1 线性注意力与全注意力比例），线性注意力层将上下文压缩为固定大小状态，**KV Cache 占用远小于标准 Transformer**，这是它能在相对小的显存下支持 262K 上下文的关键。

---

## 二、模型选择与 Trade-off 分析

### 候选模型概览

| 模型 | 类型 | 总参数 | 活跃参数 | BF16 权重大小 | 特点 |
|------|------|--------|----------|--------------|------|
| Qwen3.5-9B | Dense | 9B | 9B | ~18 GB | 小模型中最强，超越上代 Qwen3-30B |
| Qwen3.5-4B | Dense | 4B | 4B | ~8 GB | 轻量多模态 agent 的甜蜜点 |
| Qwen3.5-2B | Dense | 2B | 2B | ~4 GB | 极低资源场景 |
| Qwen3.5-35B-A3B | MoE | 35B | 3B | ~70 GB | 性能超越上代 Qwen3-235B，但需量化才能上单卡 |
| Qwen3.5-27B | Dense | 27B | 27B | ~54 GB | 不量化放不进 48GB |

所有模型原生支持 **262K 上下文**，支持 thinking / non-thinking 双模式。

### 推荐方案（按优先级排列）

#### 方案 A（推荐）：Qwen3.5-35B-A3B GPTQ-Int4

- **权重占用：~22 GB**，剩余 ~22-24 GB 给 KV Cache + 开销
- **为什么选它：** 35B 总参数但每次推理只激活 3B，意味着生成速度接近 3B 模型的水平，但智能程度远超 9B。在多项基准上超越了上代拥有 22B 活跃参数的 Qwen3-235B
- **可用 context：** 配合 `--kv-cache-dtype fp8`，可支持 **64K-128K** context
- **注意事项：**
  - Qwen3.5 的 GDN 层使用 Triton kernel，首次推理时 autotune 会临时占用 4-8 GB 显存，需要将 `--gpu-memory-utilization` 设低一些（如 0.75-0.80）
  - 需要使用 vLLM **nightly 版本**（截至 2026 年 3 月，stable 版本尚未完全支持 Qwen3.5）
  - `--max-num-batched-tokens` 至少设为 2096（GDN 注意力块对齐要求）
  - 已有社区在单卡 A100-40GB 上通过 AWQ-4bit 成功运行此模型并设置 65K context

#### 方案 B（稳妥之选）：Qwen3.5-9B BF16（无需量化）

- **权重占用：~18 GB**，剩余 ~26-28 GB 给 KV Cache
- **为什么选它：** 48GB 卡上全精度运行，无量化损失。9B 是同尺寸级别最强小模型（GPQA Diamond 81.7，超越上代 Qwen3-30B 甚至 80B 的某些指标）
- **可用 context：** BF16 KV Cache 下轻松支持 **128K+** context；加 `--kv-cache-dtype fp8` 可进一步扩展
- **注意事项：** Dense 模型，推理速度与 9B 参数量匹配（不像 MoE 那样只激活一小部分）

#### 方案 C（极限性能）：Qwen3.5-9B FP8 (w8a16 Marlin)

- **权重占用：~9 GB**，剩余 ~37 GB 给 KV Cache
- **为什么选它：** 最大化可用 context window，理论上可达接近 **262K 全量上下文**
- **注意事项：** A40 上 FP8 走 Marlin w8a16 路径，计算仍以 FP16 进行，权重节省一半但计算速度提升有限

#### 方案 D（轻量快速）：Qwen3.5-4B BF16

- **权重占用：~8 GB**，剩余 ~36 GB
- **适合场景：** 对模型智能要求不高，追求极低延迟，或用作轻量 agent / 工具调用
- **可用 context：** 非常充裕，全量 262K 不成问题

### 决策矩阵

| 需求 | 推荐方案 |
|------|----------|
| 最高智能 + 长 context | 方案 A：35B-A3B GPTQ-Int4 |
| 稳定可靠 + 全精度 + 长 context | 方案 B：9B BF16 |
| 极长 context（200K+） | 方案 C：9B FP8 |
| 低延迟 / 轻量 agent | 方案 D：4B BF16 |
| 刚入门想快速跑通 | 方案 B：9B BF16（最简单） |

---

## 三、Step-by-Step 部署流程

### Step 1：环境准备

```bash
# 在你的 home 目录或 scratch 目录下创建项目目录
mkdir -p qwen35-deploy && cd qwen35-deploy

# 创建 conda 环境（如果集群用 module 管理，先 load）
module load mamba/py3.11   
module load cuda/12.6   # 确保 CUDA >= 12.1

conda create -n vllm python=3.11 -y
conda activate vllm
```

### Step 2：安装 vLLM

**重要：Qwen3.5 需要 vLLM nightly 版本（截至 2026-03）。**

```bash
# 安装最新 nightly（推荐）
pip install vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 安装 huggingface 工具（下载模型用）
pip install huggingface_hub hf_transfer
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
module load mamba/py3.11
module load cuda/12.6
conda activate vllm


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

> **参数说明：**
> - `--max-model-len 65536`：设置 64K context。如果 OOM，降到 32768；如果显存有余，可尝试 131072
> - `--gpu-memory-utilization 0.78`：留出余量给 Triton autotune（首次推理需要 4-8GB 临时显存）
> - `--kv-cache-dtype fp8`：将 KV Cache 压缩为 FP8，显著扩展可用 context
> - `--quantization gptq_marlin`：使用 Marlin 优化的 GPTQ 推理 kernel
> - `--dtype bfloat16`：GPTQ-Int4 模型中混合了 BF16 权重，必须指定 bfloat16（float16 会崩溃）
> - `--max-num-batched-tokens 2096`：Qwen3.5 GDN 架构要求的最小 attention block 对齐

#### 方案 B 的 SLURM 脚本（9B BF16）

```bash
#!/bin/bash
#SBATCH --job-name=qwen35-9b
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

module load anaconda3
module load cuda/12.4
conda activate vllm

export HF_HOME=~/hf_cache
export CUDA_VISIBLE_DEVICES=0

mkdir -p logs

vllm serve Qwen/Qwen3.5-9B \
    --port 8000 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1 \
    --max-model-len 131072 \
    --gpu-memory-utilization 0.90 \
    --kv-cache-dtype fp8 \
    --enable-prefix-caching \
    --reasoning-parser qwen3 \
    --trust-remote-code
```

> **参数说明：**
> - `--max-model-len 131072`：128K context，9B 模型在 48GB 上非常充裕
> - `--gpu-memory-utilization 0.90`：Dense 模型没有 Triton autotune 问题，可以设高
> - 不需要 `--quantization`，全精度 BF16 直接跑

### Step 5：提交任务并连接

```bash
# 提交 SLURM 作业
sbatch run_qwen35.sh  # 你的脚本文件名

# 查看作业状态
squeue -u $USER

# 查看日志，等待 "Uvicorn running" 出现表示服务已就绪
tail -f logs/qwen35-*_<JOB_ID>.out
```

### Step 6：建立 SSH 隧道访问服务

vLLM 服务跑在计算节点上，你需要通过 SSH 隧道访问：

```bash
# 先查看你的作业跑在哪个节点
squeue -u $USER
# 假设输出显示节点为 gpu-node-01

# 建立隧道（在本地终端执行）
ssh -N -L 8000:gpu-node-01:8000 your_username@login_node_address
```

### Step 7：测试推理

```bash
# 简单测试
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-9B",
    "messages": [
      {"role": "user", "content": "用三句话解释量子计算"}
    ],
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "max_tokens": 2048
  }'
```

**Python 客户端（使用 OpenAI SDK）：**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # vLLM 本地不需要 key
)

response = client.chat.completions.create(
    model="Qwen/Qwen3.5-9B",  # 换成你部署的模型名
    messages=[
        {"role": "user", "content": "帮我分析一下这段代码的复杂度..."}
    ],
    temperature=0.7,
    top_p=0.8,
    max_tokens=4096,
    extra_body={
        "top_k": 20,
        # 控制 thinking 模式：
        # "chat_template_kwargs": {"enable_thinking": True}
    }
)

print(response.choices[0].message.content)
```

---

## 四、Thinking 模式说明

Qwen3.5 支持 thinking（深度推理）和 non-thinking（快速回答）两种模式：

- **9B / 4B / 2B / 0.8B 小模型**：默认 **关闭** thinking
- **35B-A3B / 27B 等中型模型**：默认 **开启** thinking

通过 `--reasoning-parser qwen3` 启动后，可以在请求中动态控制：

```python
# 开启 thinking（适合复杂推理、数学、编程）
extra_body={"chat_template_kwargs": {"enable_thinking": True}}

# 关闭 thinking（适合简单对话、快速回复）
extra_body={"chat_template_kwargs": {"enable_thinking": False}}
```

> **注意：** Thinking 模式会消耗大量输出 token（Qwen3.5 小模型在测试中生成了 230-390M token）。如果你的 context window 预算紧张，对简单任务请关闭 thinking。

---

## 五、常见问题排查

| 问题 | 解决方案 |
|------|----------|
| OOM: max seq len 太大 | 降低 `--max-model-len`，如从 131072 降到 65536 或 32768 |
| 首次推理 OOM（35B-A3B） | 降低 `--gpu-memory-utilization` 到 0.75，给 Triton autotune 留空间 |
| vLLM 不认识 Qwen3.5 | 确认使用 nightly 版本：`pip install -U vllm --pre` |
| FP8 相关报错（A40） | A40 不支持原生 FP8 w8a8。对于 GPTQ 模型用 `--quantization gptq_marlin`；对于 KV cache 用 `--kv-cache-dtype fp8`（这个 Ampere 支持） |
| GPTQ float16 崩溃 | 必须用 `--dtype bfloat16`，不能用 float16 |
| 下载太慢 | `export HF_HUB_ENABLE_HF_TRANSFER=1` 并确保 `pip install hf_transfer` |
| 模型输出乱码/重复 | 检查推理参数：temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.05 |
| max-num-batched-tokens 报错 | 35B-A3B 模型至少设为 2096（GDN 块对齐要求） |

---

## 六、量化方式对比速查

| 量化方式 | 权重精度 | 计算精度 | A40 兼容性 | 适用场景 |
|----------|----------|----------|------------|----------|
| BF16（无量化） | 16-bit | 16-bit | 完全支持 | 小模型（≤9B）首选 |
| FP8 Marlin (w8a16) | 8-bit | 16-bit | 支持（vLLM ≥ 0.9） | 节省权重内存，精度损失极小 |
| GPTQ-Int4 (Marlin) | 4-bit | 16-bit | 完全支持 | 大模型塞进单卡的最佳方式 |
| AWQ-Int4 | 4-bit | 16-bit | 完全支持 | 与 GPTQ 类似，社区反馈 AWQ 偶有兼容问题 |
| KV Cache FP8 | N/A | 8-bit cache | 支持 | 不影响权重，只压缩缓存，显著扩展 context |
