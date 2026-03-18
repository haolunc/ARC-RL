"""Quick test: call Qwen official endpoint in native_tools mode with streaming."""

import json
import os
import time
import traceback

from openai import OpenAI

from arc.eval.prompt import build_messages

# Load task
with open("ARC-AGI-2/data/training/1c0d0a4b.json") as f:
    task = json.load(f)

# Build messages
test_inputs = [tc["input"] for tc in task["test"]]
messages = build_messages("native_tools", task["train"], test_inputs)

# Create client
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-667f505276e7455d81c797db73333a33",
    timeout=180.0,
)


def print_section(title):
    print(f"\n{'=' * 20} {title} {'=' * 20}")


# ---------------------------------------------------------------------------
# Error categories:
#   api_connection   – network / DNS failure
#   api_timeout      – request exceeded timeout
#   api_auth         – invalid API key (401)
#   api_rate_limit   – rate limited (429)
#   api_bad_request  – bad parameters (400)
#   response_failed  – response completed with status="failed" + error object
#                      (e.g. "function.arguments must be in JSON format")
#   code_exec_error  – code_interpreter ran but code raised an error
#   stream_error     – stream interrupted / malformed event
#   stream_incomplete – stream ended without response.completed event
# ---------------------------------------------------------------------------

print("Calling Qwen API (native_tools mode, streaming)...")
t0 = time.time()

errors: list[dict] = []
final_response = None
current_section = None

try:
    stream = client.responses.create(
        model="qwen3.5-flash",
        input=messages,
        temperature=1.0,
        tools=[{"type": "code_interpreter"}],
        stream=True,
    )

    for event in stream:
        # --- reasoning summary (thinking) ---
        if event.type == "response.reasoning_summary_text.delta":
            if current_section != "reasoning":
                print_section("思考过程")
                current_section = "reasoning"
            print(event.delta, end="", flush=True)

        # --- code_interpreter call completed ---
        elif event.type == "response.output_item.done" and hasattr(event.item, "code"):
            print_section("代码执行")
            print(f"代码:\n{event.item.code}")
            if event.item.outputs:
                for out in event.item.outputs:
                    logs = getattr(out, "logs", None)
                    if logs:
                        print(f"结果: {logs}")
                        if "error" in logs.lower():
                            errors.append({"type": "code_exec_error", "detail": logs})
            current_section = "code"

        # --- text output ---
        elif event.type == "response.output_text.delta":
            if current_section != "answer":
                print_section("完整回复")
                current_section = "answer"
            print(event.delta, end="", flush=True)

        # --- response completed ---
        elif event.type == "response.completed":
            final_response = event.response
            if final_response.error:
                errors.append({
                    "type": "response_failed",
                    "code": final_response.error.code,
                    "message": final_response.error.message,
                })

except TimeoutError as e:
    errors.append({"type": "api_timeout", "message": str(e)})
    print(f"\n[ERROR] Timeout: {e}")
except Exception as e:
    cls = type(e).__name__
    # Classify by openai exception types
    if "AuthenticationError" in cls:
        etype = "api_auth"
    elif "RateLimitError" in cls:
        etype = "api_rate_limit"
    elif "BadRequestError" in cls:
        etype = "api_bad_request"
    elif "APIConnectionError" in cls:
        etype = "api_connection"
    else:
        etype = "stream_error"
    errors.append({
        "type": etype,
        "exception": cls,
        "message": str(e),
        "traceback": traceback.format_exc(),
    })
    print(f"\n[ERROR] {cls}: {e}")

if final_response is None and not any(e["type"] in ("api_timeout", "stream_error") for e in errors):
    errors.append({
        "type": "stream_incomplete",
        "message": "Stream ended without response.completed event",
    })

duration = time.time() - t0
print(f"\n\nDone in {duration:.1f}s")

# Token usage
if final_response and final_response.usage:
    print_section("Token 消耗")
    usage = final_response.usage
    print(f"输入 Token: {usage.input_tokens}")
    print(f"输出 Token: {usage.output_tokens}")
    if getattr(usage, "output_tokens_details", None):
        print(f"思考 Token: {usage.output_tokens_details.reasoning_tokens}")

# Error summary
if errors:
    print_section("错误记录")
    for i, err in enumerate(errors, 1):
        print(f"[{i}] {err['type']}: {err.get('message') or err.get('detail', '')}")

# Dump full response + errors to JSON
dump = {
    "duration": duration,
    "errors": errors,
    "response": final_response.model_dump() if final_response else None,
}
dump_path = f"response_dump_{int(t0) & 0xFFFFFFFF:08x}.json"
with open(dump_path, "w") as f:
    json.dump(dump, f, indent=2, ensure_ascii=False)
print(f"\nDump written to {dump_path}")
