# 配置系统与数据流

## 1. 配置文件结构

所有配置集中在一个 YAML 文件中（CLI 仅接受配置文件路径作为参数）：

```bash
python -m arc.eval.run config.yaml
```

完整配置文件：

```yaml
python_path: "/path/to/python"

datasets:                          # 数据集路径映射
  arc1:
    training: "ARC-AGI/data/training"
    evaluation: "ARC-AGI/data/evaluation"
  arc2:
    training: "ARC-AGI-2/data/training"
    evaluation: "ARC-AGI-2/data/evaluation"

endpoint:                          # LLM endpoint 设置
  base_url: "http://..."
  model: "Qwen/..."
  api_key_env: QWEN_API_KEY        # 环境变量名（实际密钥在 .env 中）
  temperature: 0.7

data:                              # 数据选择
  dataset: arc1                    # arc1 或 arc2
  split: training                  # training 或 evaluation
  task_ids: null                   # null = 全部任务，或 ["id1", "id2"]
  max_tasks: null                  # null = 无限制

eval:                              # 评估参数
  mode: "simple"                   # "simple" 或 "agentic"
  max_retries: 5                   # 简单模式最大重试次数
  max_steps: 20                    # 智能体模式最大步数
  timeout: 30                      # 代码执行超时（秒）
  run_name: null                   # null = 自动时间戳
```

## 2. 配置字段详解

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `eval.mode` | string | `"simple"` | 评估模式。`"simple"` = 重试循环；`"agentic"` = 工具调用循环 |
| `eval.max_retries` | int | 5 | 简单模式下每个测试用例的最大重试次数 |
| `eval.max_steps` | int | 20 | 智能体模式下每个测试用例的最大步数（每步 = 一次 LLM 调用）|
| `eval.timeout` | int | 30 | 每次代码执行的超时秒数 |
| `eval.run_name` | string/null | null | 运行名称，用于目录和断点续跑。null 时自动生成时间戳 |

## 3. 模式对应参数

| 参数 | 简单模式 | 智能体模式 |
|------|----------|------------|
| `max_retries` | 使用 | 不使用 |
| `max_steps` | 不使用 | 使用 |
| `timeout` | 使用 | 使用 |

## 4. API 密钥管理

API 密钥通过 `.env` 文件管理（由 `python-dotenv` 加载）。配置文件中的 `endpoint.api_key_env` 指定环境变量名称：

```yaml
endpoint:
  api_key_env: QWEN_API_KEY   # .env 中应有 QWEN_API_KEY=sk-...
```

## 5. 断点续跑

设置固定的 `run_name`，重新运行同一命令即可。已完成的任务会自动跳过：

```yaml
eval:
  run_name: exp01    # 固定名称，重新运行自动续跑
```

## 6. 数据流

### 输入

ARC-AGI JSON 任务文件：

```
ARC-AGI/data/training/*.json
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

### 输出

SQLite 数据库 `results/<run_name>/results.db`，包含三张表：`tasks`、`llm_calls` 和 `tool_calls`（详见 [database.md](database.md)）。

### CLI 输出示例

**简单模式**：
```
[1/400] Task: 007bbfb7 (3 train, 1 test)
  Test case 1/1
    [1/5] Calling LLM (1 messages in context)...
    [1/5] LLM responded (12s, 1523 chars, 2048 in / 512 out)
    [1/5] FAIL: train verification failed
    [2/5] Calling LLM (3 messages in context)...
    [2/5] LLM responded (15s, 1821 chars, 3072 in / 680 out)
    [2/5] SOLVED!
  SOLVED (1/1 test cases, 27.3s) | Running: 1/1 solved (100%)

=== Summary ===
Tasks evaluated: 400
Tasks solved:    120 (30.0%)
Test cases:      120/400
LLM calls:       1350
Tokens:          2845000 in / 892000 out
LLM time:        4520.3s
Results DB:      results/20260312_143000/results.db
```

**智能体模式**：
```
[1/400] Task: 007bbfb7 (3 train, 1 test)
  Test case 1/1
    [step 1/20] Calling LLM...
    [step 1/20] LLM made 1 tool call(s) (8s, 2048 in / 320 out)
      -> run_python
    [step 2/20] Calling LLM...
    [step 2/20] LLM made 1 tool call(s) (5s, 3200 in / 450 out)
      -> run_python
    [step 3/20] Calling LLM...
    [step 3/20] LLM made 1 tool call(s) (12s, 4500 in / 800 out)
      -> test_transform
    [step 4/20] Calling LLM...
    [step 4/20] LLM made 1 tool call(s) (10s, 5800 in / 750 out)
      -> test_transform
    [step 5/20] Calling LLM...
    [step 5/20] LLM made 1 tool call(s) (3s, 6200 in / 200 out)
      -> submit_transform
    [step 5/20] SOLVED!
  SOLVED (1/1 test cases, 38.2s) | Running: 1/1 solved (100%)
```
