
## Native tool call (qwen official api)

已弃用，不好用

问题：
1. max tool call 6次以后，response直接结束
2. 偶尔出现"code": "server_error", "message": "<400> InternalError.Algo.InvalidParameter: The \"function.arguments\" parameter of the code model must be in JSON format."
3. cache全是0


### Basic Call example 
```python
# 导入依赖与创建客户端...
response = client.responses.create(
    model="qwen3-max-2026-01-23",
    input="123的21次方是多少？",
    tools=[
        {"type": "code_interpreter"},
        
    ],
    extra_body={
        "enable_thinking": True
    }
)

print(response.output_text)
```

Other tool support (Won't be used in this project): {"type": "web_search"}, {"type": "web_extractor"},


### stream example

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1"
)

response = client.responses.create(
    model="qwen3-max-2026-01-23",
    input="12的3次方",
    tools=[
        {"type": "code_interpreter"}
    ],
    extra_body={
        "enable_thinking": True
    },
    stream=True
)

def print_section(title):
    print(f"\n{'=' * 20}{title}{'=' * 20}")

current_section = None
final_response = None

for event in response:
    # 思考过程增量输出
    if event.type == "response.reasoning_summary_text.delta":
        if current_section != "reasoning":
            print_section("思考过程")
            current_section = "reasoning"
        print(event.delta, end="", flush=True)

    # 代码解释器调用完成
    elif event.type == "response.output_item.done" and hasattr(event.item, "code"):
        print_section("代码执行")
        print(f"代码:\n{event.item.code}")
        if event.item.outputs:
            print(f"结果: {event.item.outputs[0].logs}")
        current_section = "code"

    # 最终回复增量输出
    elif event.type == "response.output_text.delta":
        if current_section != "answer":
            print_section("完整回复")
            current_section = "answer"
        print(event.delta, end="", flush=True)

    # 响应完成，保存最终结果用于获取 usage
    elif event.type == "response.completed":
        final_response = event.response

# 输出 Token 消耗和工具调用次数
if final_response and final_response.usage:
    print_section("Token 消耗与工具调用")
    usage = final_response.usage
    print(f"输入 Token: {usage.input_tokens}")
    print(f"输出 Token: {usage.output_tokens}")
    print(f"思考 Token: {usage.output_tokens_details.reasoning_tokens}")
    print(f"代码解释器调用次数: {usage.x_tools.get('code_interpreter', {}).get('count', 0)}")

```