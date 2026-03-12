# LLM 客户端与代码执行

## 1. LLMResponse 数据类

两个调用函数均返回 `LLMResponse` dataclass，包含 API 响应的全部有用信息：

```python
@dataclass
class LLMResponse:
    # 内容
    content: str | None           # 响应文本
    tool_calls: list | None       # 工具调用列表（OpenAI tool_call 对象）

    # 元数据
    response_id: str | None       # response.id
    actual_model: str | None      # response.model（实际使用的模型）
    finish_reason: str | None     # "stop" / "tool_calls" / "length"

    # Token 用量
    input_tokens: int | None      # prompt_tokens
    output_tokens: int | None     # completion_tokens
    cached_tokens: int | None     # prompt_tokens_details.cached_tokens（可为 null）

    # 耗时
    duration_seconds: float | None  # wall-clock 时间（含重试等待）

    # 请求上下文
    requested_model: str | None   # 请求的模型名
    temperature: float | None     # 请求的温度
```

Token 字段通过 `getattr` 防御性提取，兼容 vLLM 等不完整实现。

## 2. call_llm()

统一的 LLM 调用函数，简单模式和智能体模式共用：

```python
def call_llm(messages, tools=None, temperature=None, model=None, max_api_retries=3) -> LLMResponse:
```

- 不传 `tools` 时用于简单模式（文本调用），返回的 `tool_calls` 为 `None`
- 传入 `tools` 时用于智能体模式（工具调用），返回的 `LLMResponse` 可能包含 `tool_calls` 列表

重试逻辑：
- `RateLimitError` → 指数退避重试
- `APIError` / `APITimeoutError` → 指数退避重试（最后一次抛出异常）
- 最大重试次数：`max_api_retries`（默认 3）
- 计时在重试循环外开始，`duration_seconds` 包含所有重试等待时间

## 4. 代码执行沙盒

### 4.1 execute_transform()

用于执行 `def transform(input_grid)` 函数（两种模式共用）：

```python
def execute_transform(code, input_grid, timeout, python_path) -> dict:
    # 返回 {"success": True, "output": grid} 或 {"success": False, "error": msg}
```

- 使用 `DRIVER_TEMPLATE` 将代码包装成可执行脚本
- 通过 stdin 传入 input_grid（JSON 格式）
- 通过 stdout 读取输出网格（JSON 格式）
- 在 `/tmp` 目录下执行，有超时限制

### 4.2 execute_analysis()

用于 `run_python` 工具（智能体模式专用）：

```python
def execute_analysis(code, train_examples, test_input, timeout, python_path) -> dict:
    # 返回 {"success": True, "output": stdout} 或 {"success": False, "error": msg}
```

- 使用 `ANALYSIS_DRIVER_TEMPLATE` 将网格数据作为 JSON 字面量注入脚本顶部
- 预注入变量：`train_inputs`, `train_outputs`, `test_input`
- numpy 已导入为 `np`
- 捕获 stdout 作为返回值（截断到 5000 字符）
- stderr 截断到 2000 字符，如有则附加到输出末尾

两种执行函数的对比：

| | `execute_transform` | `execute_analysis` |
|---|---|---|
| 用途 | 执行 transform 函数 | 执行任意分析代码 |
| 输入传递 | stdin (JSON) | 脚本内 JSON 字面量 |
| 输出 | JSON 网格 | stdout 文本 |
| 预注入变量 | 无 | `train_inputs`, `train_outputs`, `test_input` |
| 输出截断 | 无 | 5000 字符 |
