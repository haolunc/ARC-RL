# 数据库

数据库采用三表结构，将 LLM 调用元数据与工具执行记录分离，避免数据重复。

## 1. Schema

### tasks 表（任务级结果）

| 列 | 类型 | 说明 |
|----|------|------|
| `run_id` | TEXT | 运行名称 |
| `task_id` | TEXT | 任务 ID |
| `solved` | INTEGER | 是否全部测试通过 (0/1) |
| `num_test_cases` | INTEGER | 测试用例数 |
| `test_cases_passed` | INTEGER | 通过的测试数 |
| `total_time_seconds` | REAL | 总耗时（含所有 LLM 调用 + 代码执行）|
| `final_code` | TEXT | 最终代码 |
| `completed_at` | TEXT | 完成时间 |

### llm_calls 表（每次 LLM API 调用一行）

| 列 | 类型 | 说明 |
|----|------|------|
| `run_id` | TEXT | 运行名称 |
| `task_id` | TEXT | 任务 ID |
| `test_index` | INTEGER | 测试用例索引 |
| `step` | INTEGER | 重试次序（简单模式）或步骤号（智能体模式）|
| **请求** | | |
| `input_messages` | TEXT | JSON：发给 LLM 的完整消息列表 |
| `requested_model` | TEXT | 请求的模型名 |
| `temperature` | REAL | 请求的温度参数 |
| **响应** | | |
| `response_id` | TEXT | OpenAI response.id |
| `actual_model` | TEXT | 实际使用的模型（可能与 requested 不同）|
| `finish_reason` | TEXT | `"stop"` / `"tool_calls"` / `"length"` |
| `llm_response` | TEXT | 响应文本内容 |
| `thinking` | TEXT | 提取的 `<think>...</think>` 内容 |
| **Token 用量** | | |
| `input_tokens` | INTEGER | prompt tokens |
| `output_tokens` | INTEGER | completion tokens |
| `cached_tokens` | INTEGER | 缓存命中 tokens（可为 NULL）|
| **耗时 & 状态** | | |
| `duration_seconds` | REAL | API 调用 wall-clock 时间（含重试等待）|
| `success` | INTEGER | 1=成功, 0=API 错误 |
| `error_type` | TEXT | 错误类型 |
| `error_msg` | TEXT | 错误消息 |
| **简单模式验证结果** | | 智能体模式下为 NULL |
| `extracted_code` | TEXT | 提取的代码 |
| `train_pass` | INTEGER | 训练集是否通过 (0/1/NULL) |
| `test_correct` | INTEGER | 测试是否正确 (0/1/NULL) |
| `cell_accuracy` | REAL | 像素准确率 |
| `created_at` | TEXT | 记录时间 |

### tool_calls 表（每个工具调用一行，仅智能体模式）

| 列 | 类型 | 说明 |
|----|------|------|
| `llm_call_id` | INTEGER | 外键 → llm_calls.id |
| `tool_call_index` | INTEGER | 在本次 LLM 响应中的顺序（0, 1, ...）|
| `tool_call_id` | TEXT | OpenAI tool_call.id |
| `tool_name` | TEXT | 工具名（`run_python` / `test_transform` / `submit_transform`）|
| `tool_arguments` | TEXT | 原始 JSON 参数（含完整代码）|
| `tool_output` | TEXT | 返回给 LLM 的结果文本 |
| `extracted_code` | TEXT | 提取的代码（用于日志记录）|
| `test_correct` | INTEGER | submit_transform 的 pass/fail（其他工具为 NULL）|
| `duration_seconds` | REAL | 工具执行耗时 |
| `created_at` | TEXT | 记录时间 |

## 2. 设计理由

旧设计用单一 `attempts` 表记录所有信息。问题：在智能体模式下，一次 LLM 调用可能产生多个 tool call，每个 tool call 创建一行，导致 LLM 响应文本、token 用量、耗时等信息被重复存储。

新设计将 LLM 调用元数据（`llm_calls`）与工具执行记录（`tool_calls`）分离：
- **llm_calls**：每次 API 调用恰好一行，包含请求（完整消息列表）、响应（内容、token、耗时）、状态
- **tool_calls**：通过 `llm_call_id` 外键关联到对应的 LLM 调用，无数据重复
- **简单模式**：验证结果直接存在 `llm_calls` 行上（因为是 1:1 关系），不产生 `tool_calls` 行

## 3. 不同模式的记录方式

**简单模式**：
- 每次 LLM 调用 → 一行 `llm_calls`
- `step` = 重试次数 (1, 2, 3, ...)
- `error_type` = `"extraction_failed"` / `"train_fail"` / `"test_exec_error"` / `"wrong_output"` / `"api_error"`
- `extracted_code`, `train_pass`, `test_correct`, `cell_accuracy` 记录验证结果
- 无 `tool_calls` 行

**智能体模式**：
- 每次 LLM 调用 → 一行 `llm_calls` + N 行 `tool_calls`
- `step` = 步骤号 (1, 2, 3, ...)
- `llm_calls` 行的验证相关字段为 NULL
- `tool_calls` 行记录每个工具的参数、输出、执行耗时
- `test_correct` 仅在 `submit_transform` 时非 NULL
- 纯文本响应（无 tool_calls）→ 仅一行 `llm_calls`，无 `tool_calls` 行

## 4. 查询示例

```sql
-- 某次运行的 token 消耗汇总
SELECT SUM(input_tokens), SUM(output_tokens), SUM(cached_tokens)
FROM llm_calls WHERE run_id = 'exp01' AND success = 1;

-- 某任务的 LLM 调用时间线
SELECT step, duration_seconds, input_tokens, output_tokens, finish_reason, error_type
FROM llm_calls WHERE run_id = 'exp01' AND task_id = '007bbfb7'
ORDER BY step;

-- 智能体模式：某步骤的工具调用详情
SELECT tc.tool_name, tc.duration_seconds, tc.test_correct, length(tc.tool_output)
FROM tool_calls tc
JOIN llm_calls lc ON tc.llm_call_id = lc.id
WHERE lc.run_id = 'exp01' AND lc.task_id = '007bbfb7'
ORDER BY lc.step, tc.tool_call_index;

-- 平均每次 LLM 调用的 token 用量
SELECT AVG(input_tokens), AVG(output_tokens), AVG(duration_seconds)
FROM llm_calls WHERE run_id = 'exp01' AND success = 1;
```
