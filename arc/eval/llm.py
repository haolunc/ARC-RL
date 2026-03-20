"""LLM calling logic — sandbox_tools loop, direct mode, and code execution."""

import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass

import openai

from arc.eval.config import MAX_TOOL_ROUNDS, WARN_THRESHOLD, TEMPERATURE, EXEC_TIMEOUT
from arc.eval.prompt import (
    DIRECT_INSTRUCTION,
    SANDBOX_TOOLS_INSTRUCTION,
    TOOL_CALL_WARNING,
    TOOL_CALL_FINAL,
)

MAX_RETRIES = 3
BACKOFF_BASE = 2

_TOOLS = [
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
                    "description": "Python code to execute",
                }
            },
            "required": ["code"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


@dataclass
class LLMResult:
    text: str
    extracted_code: str | None
    usage: dict
    tool_rounds: int
    raw_responses: list[dict]


def execute_python(code: str, python_path: str, timeout: int = EXEC_TIMEOUT) -> dict:
    """Execute Python code in a subprocess sandbox.

    Returns: {"stdout": str, "stderr": str, "exit_code": int}
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
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


def _serialize_output(output_items) -> str:
    """Serialize response output items into readable text (reasoning + message + tool calls)."""
    parts = []
    for item in output_items:
        if item.type == "reasoning":
            summaries = getattr(item, "summary", None)
            if summaries:
                for s in summaries:
                    text = getattr(s, "text", str(s))
                    parts.append(f"[Reasoning]\n{text}")
        elif item.type == "message":
            for content in item.content:
                if hasattr(content, "type") and content.type == "output_text":
                    parts.append(f"[Response]\n{content.text}")
        elif item.type == "function_call":
            try:
                args = json.loads(item.arguments)
                code = args.get("code", item.arguments)
            except (json.JSONDecodeError, AttributeError):
                code = item.arguments
            parts.append(f"[Tool Call: {item.name}]\n{code}")
    return "\n\n".join(parts)


def _usage_to_dict(usage) -> dict:
    return {
        "input": getattr(usage, "input_tokens", 0),
        "output": getattr(usage, "output_tokens", 0),
        "reasoning": getattr(getattr(usage, "output_tokens_details", None), "reasoning_tokens", 0),
        "cached": getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0),
    }


def extract_code(text: str) -> str | None:
    """Extract test_transform function from LLM text output.

    Returns the code string, or None if no valid test_transform found.
    """
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if not matches:
        return None
    for code in reversed(matches):
        if "def test_transform" in code:
            return code.strip()
    return None


def _api_call(client, **kwargs):
    """Call client.responses.create with retry on transient errors."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.responses.create(**kwargs)
        except (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.InternalServerError,
        ):
            if attempt == MAX_RETRIES:
                raise
            time.sleep(BACKOFF_BASE ** (attempt + 1))


def call_llm(client, cfg: dict, messages: list[dict]) -> LLMResult:
    """Call LLM based on mode (sandbox_tools or direct). Returns LLMResult.

    text contains the full transcript: reasoning + response + tool calls + tool results.
    """
    model = cfg["endpoint"]["model"]
    mode = cfg["eval"]["mode"]

    if mode == "direct":
        response = _api_call(
            client,
            model=model,
            instructions=DIRECT_INSTRUCTION,
            input=messages,
            temperature=TEMPERATURE,
        )
        last_text = _serialize_output(response.output)
        return LLMResult(
            text=last_text,
            extracted_code=extract_code(last_text),
            usage=_usage_to_dict(response.usage),
            tool_rounds=0,
            raw_responses=[response.model_dump()],
        )

    # sandbox_tools mode
    input_list = list(messages)
    total_usage = {"input": 0, "output": 0, "reasoning": 0, "cached": 0}
    tool_rounds = 0
    transcript_parts = []
    raw_responses = []

    for round_num in range(MAX_TOOL_ROUNDS):
        remaining = MAX_TOOL_ROUNDS - round_num

        if remaining <= 1:
            input_list.append({"role": "user", "content": TOOL_CALL_FINAL})
        elif remaining <= WARN_THRESHOLD:
            input_list.append({"role": "user", "content": TOOL_CALL_WARNING.format(remaining=remaining)})

        response = _api_call(
            client,
            model=model,
            instructions=SANDBOX_TOOLS_INSTRUCTION,
            input=input_list,
            tools=_TOOLS,
            temperature=TEMPERATURE,
            parallel_tool_calls=True,
        )

        raw_responses.append(response.model_dump())

        usage = _usage_to_dict(response.usage)
        for k in total_usage:
            total_usage[k] += usage[k]

        last_response_text = _serialize_output(response.output)
        transcript_parts.append(last_response_text)

        input_list += response.output

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            break

        tool_rounds += 1

        for tc in tool_calls:
            try:
                args = json.loads(tc.arguments)
                result = execute_python(args["code"], cfg["python_path"])
            except (json.JSONDecodeError, KeyError) as e:
                result = {"stdout": "", "stderr": str(e), "exit_code": -1}

            tr_lines = [f"[Tool Result] exit_code={result['exit_code']}"]
            if result["stdout"]:
                tr_lines.append(f"stdout:\n{result['stdout']}")
            if result["stderr"]:
                tr_lines.append(f"stderr:\n{result['stderr']}")
            transcript_parts.append("\n".join(tr_lines))

            input_list.append({
                "type": "function_call_output",
                "call_id": tc.call_id,
                "output": json.dumps(result, ensure_ascii=False),
            })

        continue_msg = "Code execution results returned. Continue analyzing and solving the problem."
        input_list.append({"role": "user", "content": continue_msg})
        transcript_parts.append(f"[User]\n{continue_msg}")
    else:
        # Exhausted all rounds — still got tool calls on last round
        raise RuntimeError("exceeded max tool rounds")

    return LLMResult(
        text="\n\n".join(transcript_parts),
        extracted_code=extract_code(last_response_text),
        usage=total_usage,
        tool_rounds=tool_rounds,
        raw_responses=raw_responses,
    )
