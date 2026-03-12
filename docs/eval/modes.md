# 评估模式

## 1. 简单模式 (Simple Mode)

### 1.1 评估循环

对每个任务的每个测试用例，执行以下基于重试的循环（最多 `max_retries` 次）：

```
┌─ 构建初始 prompt（训练样例 + 测试输入）
│
├─ for attempt in 1..max_retries:
│   │
│   ├─ 1. 调用 LLM → 获取 LLMResponse（含 token 用量、耗时、finish_reason）
│   │   └─ 失败 → 记录 llm_calls 行（success=0），跳出循环
│   │
│   ├─ 1.5. 提取 thinking 内容 → extract_thinking(response)
│   │   └─ 将 <think>...</think> 内容单独存入数据库
│   │
│   ├─ 2. 提取代码 → extract_code(response)
│   │   └─ 失败 → 记录 extraction_failed，追加错误反馈，继续重试
│   │
│   ├─ 3. 训练集验证 → verify_on_train(code, train_examples)
│   │   │   对每个训练样例执行代码并比较输出
│   │   └─ 失败 → 记录 train_fail，追加详细错误反馈（含期望/实际网格），继续重试
│   │
│   ├─ 4. 测试执行 → execute_transform(code, test_input)
│   │   └─ 运行时错误 → 记录 test_exec_error，追加错误反馈，继续重试
│   │
│   └─ 5. 输出比较 → compare_grids(actual, expected)
│       ├─ 正确 → 记录成功，跳出循环
│       └─ 错误 → 记录 wrong_output（数据库中保存完整对比详情）
│                 → 反馈给 LLM 仅告知"输出错误"（不泄露期望输出）
│                 → 继续重试
│
└─ 记录任务级结果（solved/failed、通过测试数、耗时、最终代码）
```

### 1.2 反馈机制

重试时的反馈策略：

| 错误阶段 | 反馈给 LLM 的内容 | 设计理由 |
|----------|-------------------|----------|
| 代码提取失败 | "无法提取 Python 函数，请写 `def transform` 在代码块中" | 格式指导 |
| 训练集失败 | 完整错误信息：期望输出 vs 实际输出、形状不匹配、cell 准确率 | 训练数据对 LLM 可见，详细反馈帮助修正 |
| 测试运行时错误 | 错误堆栈信息 | 不泄露答案 |
| 测试输出错误 | **仅告知"输出错误"，不显示期望 vs 实际** | 防止 LLM 通过测试反馈"记忆"答案，保持评估公正性 |

**注意**：数据库中的 `error_msg` 字段始终保存完整对比详情（供人工分析），但发送给 LLM 的反馈消息是受限的。

### 1.3 对话历史管理

每次失败时，LLM 的响应和错误信息都会追加到对话历史中。LLM 可以看到所有历史尝试，避免重复犯错。

```python
messages = [system_prompt, user_prompt]
# 第一次尝试后：
messages = [system_prompt, user_prompt, assistant_response_1, user_error_feedback_1]
# 第二次尝试后：
messages = [system_prompt, user_prompt, assistant_response_1, user_error_feedback_1,
            assistant_response_2, user_error_feedback_2]
# ...
```

## 2. 智能体模式 (Agentic Mode)

### 2.1 概述

智能体模式将评估从被动的"重试循环"转变为主动的"工具调用循环"。LLM 不再被要求一次性写出正确代码，而是可以：

1. 用 `run_python` 执行任意分析代码来理解网格模式
2. 用 `test_transform` 在训练样例上测试自己的 `transform` 函数
3. 用 `submit_transform` 提交最终答案

这种模式更接近人类解题过程：先观察、分析、实验，再提交。

### 2.2 三个工具

#### `run_python(code: str)`

执行任意 Python 代码来分析网格数据。

- **预注入变量**：
  - `train_inputs`: 所有训练输入网格的列表 (`list[list[list[int]]]`)
  - `train_outputs`: 所有训练输出网格的列表
  - `test_input`: 测试输入网格 (`list[list[int]]`)
  - `np`: numpy 已导入
- **返回**：stdout 输出（截断到 5000 字符）+ stderr（如果有）
- **用途**：分析网格形状、颜色分布、模式识别、差异计算等

使用示例（LLM 会生成类似代码）：
```python
# 分析每个训练样例的输入/输出形状
for i, (inp, out) in enumerate(zip(train_inputs, train_outputs)):
    print(f"Example {i+1}: input={len(inp)}x{len(inp[0])}, output={len(out)}x{len(out[0])}")

# 统计颜色分布
import numpy as np
for i, inp in enumerate(train_inputs):
    arr = np.array(inp)
    unique, counts = np.unique(arr, return_counts=True)
    print(f"Example {i+1} colors: {dict(zip(unique.tolist(), counts.tolist()))}")
```

**实现细节**：`safe_exec.py` 中的 `execute_analysis()` 函数使用 `ANALYSIS_DRIVER_TEMPLATE` 模板，将网格数据作为 JSON 字面量注入到脚本顶部，然后追加用户代码。通过子进程执行，捕获 stdout 作为返回值。

#### `test_transform(code: str)`

在所有训练样例上测试 `def transform(input_grid)` 函数。

- **返回**：逐样例结果
  - 通过：`Example 1: PASS`
  - 失败：`Example 1: FAIL` + 期望输出 vs 实际输出、形状不匹配提示、cell 准确率
  - 错误：`Example 1: ERROR` + 错误堆栈
- **详细程度**：完整展示期望 vs 实际输出（因为训练数据对 LLM 可见）
- **用途**：迭代调试 transform 函数

#### `submit_transform(code: str)`

提交最终 `def transform(input_grid)` 函数进行测试评估。

- **前置检查**：先静默验证训练样例。如果训练样例不通过，直接拒绝提交并告知原因
- **测试评估**：仅返回 pass/fail（不显示期望输出，不显示 cell 准确率）
- **返回消息**：
  - 训练不通过：`"Submission rejected: your code does not pass all training examples. Use test_transform to debug first."`
  - 运行时错误：`"Runtime error on test input: ..."` + 错误堆栈
  - 通过：`"Correct! Your submission passed the test case."`
  - 失败：`"Incorrect. Your submission did not produce the correct output for the test input."`
- **循环控制**：提交成功时标记为 solved 并结束循环；失败时 LLM 可以继续调试

### 2.3 评估循环

```
┌─ 构建初始消息（智能体 system prompt + 训练样例 + 测试输入）
│
├─ for step in 1..max_steps:
│   │
│   ├─ 1. 调用 LLM（带工具定义）→ 获取 LLMResponse
│   │   └─ API 失败 → 记录 llm_calls 行（success=0），跳出循环
│   │
│   ├─ 2. 提取 thinking 内容（如果有文本内容）
│   │
│   ├─ 3. 插入一行 llm_calls（含 token、耗时、finish_reason 等）
│   │
│   ├─ 4. 序列化并追加 assistant 消息到历史
│   │
│   ├─ 5a. 如果有 tool_calls:
│   │   │
│   │   ├─ 对每个 tool_call:
│   │   │   ├─ 解析参数（JSON）
│   │   │   ├─ 执行工具 → execute_tool(name, args, context)（记录执行耗时）
│   │   │   ├─ 追加 tool 结果消息到历史
│   │   │   ├─ 插入一行 tool_calls（关联 llm_call_id，含工具参数、输出、耗时）
│   │   │   │
│   │   │   └─ 如果是 submit_transform 且 solved:
│   │   │       └─ 标记成功，跳出循环
│   │   │
│   │   └─ 如果未 solved → 继续下一步
│   │
│   └─ 5b. 如果是纯文本响应（无 tool_calls）:
│       └─ 仅 llm_calls 行已记录，继续下一步（LLM 在思考）
│
├─ max_steps 耗尽 → 标记为失败
│
└─ 记录任务级结果
```

### 2.4 消息历史格式

智能体模式的消息历史遵循 OpenAI 的工具调用协议：

```python
[
    # 1. system prompt（描述工具和工作流）
    {"role": "system", "content": "You are an expert puzzle solver..."},

    # 2. user message（展示训练样例和测试输入）
    {"role": "user", "content": "Here are the training examples:\n..."},

    # 3. assistant 消息（可能包含 content 和/或 tool_calls）
    {
        "role": "assistant",
        "content": "Let me analyze the grid patterns...",  # 可选
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "run_python",
                    "arguments": "{\"code\": \"print(len(train_inputs))\"}"
                }
            }
        ]
    },

    # 4. tool 结果消息
    {
        "role": "tool",
        "tool_call_id": "call_abc123",
        "content": "3"
    },

    # 5. 后续 assistant 消息...
    # ...
]
```

### 2.5 智能体 System Prompt

智能体模式使用专用的 `AGENTIC_SYSTEM_PROMPT`，内容包括：

1. **角色定义**：ARC 专家 + Python 程序员
2. **网格颜色映射**：0-9 对应颜色名称
3. **工具说明**：每个工具的功能描述和使用场景
4. **推荐工作流**：分析 → 假设 → 编码 → 测试 → 提交
5. **代码规则**：函数签名、可用库、输出维度说明

### 2.6 序列化 Assistant 消息

`LLMResponse` 对象需要转换为可序列化的 dict 才能追加到消息历史中。`_serialize_assistant_msg()` 处理这个转换：

```python
def _serialize_assistant_msg(llm_result) -> dict:
    d = {"role": "assistant"}
    if llm_result.content:
        d["content"] = llm_result.content
    if llm_result.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in llm_result.tool_calls
        ]
    return d
```

## 3. Thinking 内容提取

### 3.1 背景

部分模型（如 Qwen3）在响应中使用 `<think>...</think>` 标签包裹推理过程。这些内容对分析模型的推理策略非常有价值，但不应参与代码提取。

### 3.2 实现

`code_extract.py` 中的 `extract_thinking()` 函数：

```python
def extract_thinking(text: str) -> tuple[str | None, str]:
    """返回 (thinking_content, stripped_text)"""
```

- 使用正则 `<think>(.*?)</think>` 提取所有 thinking 块
- 多个 thinking 块用换行拼接
- 返回元组：`(thinking_text, stripped_text)`
  - `thinking_text`: 提取的推理内容（无则为 `None`）
  - `stripped_text`: 移除 thinking 标签后的文本

### 3.3 使用

两种模式都会提取 thinking 内容：

- **简单模式**：在 `extract_code()` 之前调用 `extract_thinking()`，将 thinking 存入数据库的 `thinking` 列
- **智能体模式**：在每步收到 LLM 响应后，如果有文本内容就提取 thinking

注意：`extract_code()` 内部仍然调用 `strip_thinking()` 来移除 thinking 标签后再进行代码提取，保持向后兼容。

## 4. 两种模式的对比

| 维度 | 简单模式 | 智能体模式 |
|------|----------|------------|
| LLM 调用方式 | `call_llm()` → `LLMResponse` | `call_llm_with_tools()` → `LLMResponse` |
| 代码获取 | 正则提取代码块 | 工具参数中直接传递 |
| 探索能力 | 无（LLM 仅看到训练样例）| 可执行任意分析代码 |
| 测试方式 | 自动验证训练 → 测试 | LLM 主动调用 test/submit |
| 反馈来源 | 系统自动生成 | 工具返回值 |
| 训练反馈 | 详细（期望 vs 实际）| 详细（test_transform 工具）|
| 测试反馈 | 受限（仅 pass/fail）| 受限（submit_transform 仅 pass/fail）|
| 循环控制 | `max_retries` | `max_steps` |
| 终止条件 | 测试通过 或 重试耗尽 | submit_transform 成功 或 步数耗尽 |
| 典型步数 | 1-5 次 | 3-15 步 |
| 适用场景 | 快速基线评估 | 深度推理任务 |
