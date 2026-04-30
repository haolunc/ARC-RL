
## LLM Endpoint & Tool Call 设计文档

### LLM Endpoint

两种 endpoint，都走 OpenAI Response API（不用 Chat Completion API）：

1. **vLLM self-hosted endpoint** — 自己部署的 vLLM 服务
2. **Qwen official API** — Qwen 官方 API

两者都支持：
- Reasoning（思维链推理）
- 自定义 tool（function calling）
- Parallel tool call — Qwen 官方 API 通过 `parallel_tool_calls=true` 开启；vLLM 取决于 `--tool-call-parser` 选择

vLLM tool-call-parser 选择：

| Parser | 适用模型 | Streaming | Parallel | 备注 |
|--------|---------|-----------|----------|------|
| `hermes` | Qwen3 / Qwen3.5 (非 Coder) | Yes | Yes | **当前应使用** |
| `qwen3_xml` | Qwen3-Coder 系列 | Yes | Yes | Coder 推荐 |
| `qwen3_coder` | Qwen3-Coder 系列 | No | No | legacy，有安全漏洞，避免使用 |

> **注意**：当前 `deploy_vllm.sh` 用的是 `--tool-call-parser qwen3_coder`，但模型是 Qwen3.5-35B-A3B（非 Coder），应改为 `hermes`。

---

### LLM Response 处理

Response API 返回的 `response.output` 是一个 item list，包含两种类型：

- `message`（`type == "message"`）：LLM 的文本输出，包含 reasoning 和最终回答
- `function_call`（`type == "function_call"`）：LLM 请求调用 tool

从 response 中提取文本内容：
```python
def extract_text_from_response(response) -> str:
    """从 Response API output 中拼接所有文本内容"""
    parts = []
    for item in response.output:
        if item.type == "message":
            for content in item.content:
                if content.type == "output_text":
                    parts.append(content.text)
    return "\n".join(parts)
```

Token usage 从 `response.usage` 获取：
- `input_tokens`, `output_tokens`
- `input_tokens_details.cached_tokens`（prompt cache 命中）
- `output_tokens_details.reasoning_tokens`（思维链 tokens）

---

### 两种模式

| 模式 | 说明 |
|------|------|
| `direct` | 纯推理，直接输出 answer，单次 API 调用 |
| `sandbox_tools` | 带 code interpreter，LLM 可以调用 Python code 来辅助推理，多轮循环 |

---

### Direct 模式

单次调用，无 tool loop：

```python
def call_llm_direct(client, model, messages):
    response = client.responses.create(
        model=model,
        instructions=DIRECT_INSTRUCTION,
        input=messages,
    )
    text = extract_text_from_response(response)
    return LLMResult(text=text, usage=response.usage, tool_rounds=0)
```

---

### Sandbox Tools 模式 — Tool Call 流程

核心循环逻辑（每轮都传同样的 `instructions` 和 `tools`，不修改 tool definition）：

```python
MAX_ROUNDS = 10
WARN_THRESHOLD = 3

for round_num in range(MAX_ROUNDS):
    remaining = MAX_ROUNDS - round_num

    if remaining <= 1:
        input_list.append({"role": "user", "content": TOOL_CALL_FINAL})
    elif remaining <= WARN_THRESHOLD:
        input_list.append({"role": "user", "content": TOOL_CALL_WARNING.format(remaining=remaining)})

    response = client.responses.create(
        model=model,
        instructions=INSTRUCTION,
        input=input_list,
        tools=tools,
        parallel_tool_calls=True,
    )

    input_list += response.output

    tool_calls = [item for item in response.output if item.type == "function_call"]

    if not tool_calls:
        break

    for tc in tool_calls:
        result = execute_tool(tc)
        input_list.append(result)
```

**Prompt cache 分析**：每次调用实际拼出的 prompt 结构为 `[instructions][tools][input_list...]`。
`instructions` 和 `tools` 每轮相同，是固定前缀；`input_list` 只在尾部追加 → 前缀始终一致 → **不影响 prompt cache hit**。

---

### Code Interpreter Setting

Tool definition（Response API `tools` 参数）：

```python
tools = [
    {
        "type": "function",
        "name": "execute_python",
        "description": (
            "Execute Python code and return the output. "
            "Use for tasks that require precise computation, data analysis, "
            "pattern enumeration, or visualization. "
            "Use print() to output results."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                }
            },
            "required": ["code"],
            "additionalProperties": False
        },
        "strict": True
    }
]
```

Code executor（subprocess sandbox 执行）：

```python
def execute_python(code: str, python_path: str, timeout: int = 30) -> dict:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [python_path, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
        )
        return {
            "stdout": result.stdout[:5000],
            "stderr": result.stderr[:2000],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1}
    finally:
        os.unlink(tmp_path)
```

Tool call 结果回传格式（append 到 `input_list`）：

```python
for tc in tool_calls:
    args = json.loads(tc.arguments)
    result = execute_python(args["code"], python_path)

    input_list.append({
        "type": "function_call_output",
        "call_id": tc.call_id,
        "output": json.dumps(result, ensure_ascii=False),
    })
```

---

### 错误处理

LLM 调用的错误策略：**有限 retry（最多 3 次，间隔递增），仍失败则标记 error_llm**。

| 错误类型 | 处理方式 |
|---------|---------|
| 连接超时 / 网络错误 | retry（最多 3 次，backoff: 2s → 4s → 8s） |
| API 错误（rate limit / 5xx） | retry（同上） |
| API 错误（4xx 非 rate limit） | 不 retry，直接标记 `error_llm` |
| 最后一轮仍返回 tool call | 标记 `error_llm`，记录 "exceeded max tool rounds" |
| Tool call 解析错误（JSON parse 失败） | 返回 error 结果给 LLM，继续循环（不中断） |
| Code execute 超时 / 报错 | 返回 error 结果给 LLM，继续循环（不中断） |

Retry 实现：
```python
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds

for attempt in range(MAX_RETRIES + 1):
    try:
        response = client.responses.create(...)
        break
    except (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError, openai.InternalServerError) as e:
        if attempt == MAX_RETRIES:
            raise
        time.sleep(BACKOFF_BASE ** (attempt + 1))
```
