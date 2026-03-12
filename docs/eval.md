# ARC-AGI LLM 评估流水线

## 1. 流水线概述

`arc/eval` 是一个基于大语言模型（LLM）的 ARC-AGI 任务评估流水线。核心目标：

- 给 LLM 展示 ARC 任务的训练样例（输入/输出网格对）
- 要求 LLM 编写 `transform(input_grid)` 函数来实现变换规则
- 在训练样例上验证代码正确性，通过后在测试样例上评估
- 支持多轮重试：失败时将错误信息反馈给 LLM，引导其修正代码
- 所有结果持久化到 SQLite 数据库，支持断点续跑

## 2. 模块架构

```
arc/eval/
├── config.py       # 配置加载（.env + config.yaml + endpoint.yaml）
├── prompt.py       # Prompt 构建（system prompt、初始消息、重试追加）
├── llm_client.py   # OpenAI SDK 调用封装（含自动重试）
├── code_extract.py # 从 LLM 响应中提取 Python 代码
├── safe_exec.py    # 子进程沙盒执行 LLM 生成的代码
├── evaluate.py     # 网格比较和训练集验证
├── db.py           # SQLite 结果记录（runs/tasks/attempts 三表）
└── run.py          # CLI 入口和主评估循环
```

各模块职责：

| 模块 | 职责 |
|------|------|
| `config` | 从三个配置文件加载参数：API endpoint、数据集路径、默认超参 |
| `prompt` | 构造聊天消息：system prompt 定义角色，user prompt 展示训练样例和测试输入 |
| `llm_client` | 封装 OpenAI SDK 调用，处理速率限制和 API 错误的自动重试 |
| `code_extract` | 从 LLM 响应中提取 Python 代码块，支持 \`\`\`python 块、通用代码块、裸函数回退 |
| `safe_exec` | 将代码写入临时文件，通过子进程执行，隔离不可信代码 |
| `evaluate` | `compare_grids` 逐像素比较网格，`verify_on_train` 在所有训练样例上验证代码 |
| `db` | SQLite 写入层，每次 attempt 立即 commit，支持断点续跑查询 |
| `run` | CLI 解析、任务加载、主评估循环、结果汇总 |

## 3. 评估循环

对每个任务的每个测试用例，执行以下基于重试的循环（最多 `max_retries` 次）：

```
┌─ 构建初始 prompt（训练样例 + 测试输入）
│
├─ for attempt in 1..max_retries:
│   │
│   ├─ 1. 调用 LLM → 获取响应
│   │   └─ 失败 → 记录 api_error，跳出循环
│   │
│   ├─ 2. 提取代码 → extract_code(response)
│   │   └─ 失败 → 记录 extraction_failed，追加错误反馈，继续重试
│   │
│   ├─ 3. 训练集验证 → verify_on_train(code, train_examples)
│   │   │   对每个训练样例执行代码并比较输出
│   │   └─ 失败 → 记录 train_fail，追加错误反馈，继续重试
│   │
│   ├─ 4. 测试执行 → execute_transform(code, test_input)
│   │   └─ 失败 → 记录 test_exec_error，追加错误反馈，继续重试
│   │
│   └─ 5. 输出比较 → compare_grids(actual, expected)
│       ├─ 正确 → 记录成功，跳出循环
│       └─ 错误 → 记录 wrong_output，追加错误反馈（含期望/实际网格、准确率），继续重试
│
└─ 记录任务级结果（solved/failed、通过测试数、耗时、最终代码）
```

重试机制的关键设计：每次失败时，将 LLM 的响应和详细错误信息追加到对话历史中，让 LLM 看到所有历史尝试，避免重复犯错。

## 4. 数据流

**输入**：ARC-AGI JSON 任务文件

```
data/ARC-AGI/data/training/*.json
```

每个文件结构：
```json
{
  "train": [
    {"input": [[0,1,...], ...], "output": [[2,3,...], ...]}
  ],
  "test": [
    {"input": [[...]], "output": [[...]]}
  ]
}
```

**输出**：SQLite 数据库 `results/<run_name>/results.db`

三张表：
- `runs` — 运行元数据（数据集、超参数、启动时间）
- `tasks` — 任务级结果（是否解决、通过测试数、耗时、最终代码）
- `attempts` — 每次尝试的详细记录（LLM 响应、提取代码、训练通过与否、测试正确与否、cell 准确率、错误类型和消息）

## 5. 配置系统

三个配置文件协同工作：

| 文件 | 内容 | 示例 |
|------|------|------|
| `config.yaml` | 数据集路径、默认超参、Python 解释器路径 | `max_retries: 3`, `timeout: 30` |
| `endpoint.yaml` | LLM API endpoint 定义和活跃 endpoint 选择 | `base_url`, `model`, `api_key_env` |
| `.env` | API 密钥等敏感信息 | `OPENAI_API_KEY=sk-...` |

`endpoint.yaml` 支持多个 endpoint 定义，通过 `active` 字段切换，方便在不同 LLM 提供商之间切换。

## 6. 断点续跑

通过 `--run-name` 参数实现：

```bash
# 首次运行
python -m arc.eval.run --dataset arc1 --split training --run-name exp01

# 中断后恢复（自动跳过已完成的任务）
python -m arc.eval.run --dataset arc1 --split training --run-name exp01
```

机制：
1. 启动时查询 `tasks` 表中该 `run_id` 已有的 `task_id`
2. 从任务列表中过滤掉已完成的任务
3. 只评估剩余任务

如果不指定 `--run-name`，自动生成时间戳名称（如 `20260311_143000`），每次都是全新运行。
