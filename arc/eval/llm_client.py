"""LLM API client and solver using OpenAI SDK Responses API."""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from openai import OpenAI


@dataclass
class LLMResponse:
    """Structured response from a Responses API call."""
    # Content
    content: str | None = None           # final text from message items
    output_items: list | None = None     # serialized output items (for DB)
    raw_output: list | None = None       # raw response.output (for feeding back to API)
    tool_calls: list | None = None       # function_call items

    # Metadata
    response_id: str | None = None
    actual_model: str | None = None

    # Token usage (extended)
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None
    total_tokens: int | None = None
    x_tools: str | None = None           # JSON string of tool usage info

    # Timing
    duration_seconds: float | None = None

    # Request context
    requested_model: str | None = None
    temperature: float | None = None


def _serialize_output_items(output) -> list[dict]:
    """Serialize response.output items to JSON-safe dicts."""
    items = []
    for item in output:
        item_type = getattr(item, "type", None)
        d = {"type": item_type}
        if item_type == "message":
            d["role"] = getattr(item, "role", None)
            content = getattr(item, "content", [])
            d["content"] = [
                {"type": getattr(c, "type", None), "text": getattr(c, "text", None)}
                for c in content
            ]
        elif item_type == "function_call":
            d["name"] = getattr(item, "name", None)
            d["arguments"] = getattr(item, "arguments", None)
            d["call_id"] = getattr(item, "call_id", None)
        elif item_type == "reasoning":
            summary = getattr(item, "summary", [])
            d["summary"] = [
                {"type": getattr(s, "type", None), "text": getattr(s, "text", None)}
                for s in summary
            ]
        elif item_type == "code_interpreter_call":
            d["code"] = getattr(item, "code", None)
            results = getattr(item, "results", [])
            d["results"] = [
                {"type": getattr(r, "type", None), "output": getattr(r, "output", None)}
                for r in results
            ]
        else:
            d["raw"] = str(item)
        items.append(d)
    return items


def _parse_response(response, model: str, temperature: float,
                    t0: float) -> LLMResponse:
    """Parse a Responses API response into LLMResponse."""
    duration = time.time() - t0

    # Extract text content from message items
    text_parts = []
    tool_calls = []
    for item in response.output:
        item_type = getattr(item, "type", None)
        if item_type == "message":
            for c in getattr(item, "content", []):
                if getattr(c, "type", None) == "output_text":
                    text_parts.append(c.text)
        elif item_type == "function_call":
            tool_calls.append(item)

    content = "\n".join(text_parts) if text_parts else None

    # Token usage
    usage = response.usage
    input_tokens = output_tokens = reasoning_tokens = None
    cached_tokens = total_tokens = None
    x_tools_str = None

    if usage:
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

        out_details = getattr(usage, "output_tokens_details", None)
        if out_details:
            reasoning_tokens = getattr(out_details, "reasoning_tokens", None)

        in_details = getattr(usage, "input_tokens_details", None)
        if in_details:
            cached_tokens = getattr(in_details, "cached_tokens", None)

        x_tools_raw = getattr(usage, "x_tools", None)
        if x_tools_raw:
            x_tools_str = json.dumps(x_tools_raw)

    output_items = _serialize_output_items(response.output)

    return LLMResponse(
        content=content,
        output_items=output_items,
        raw_output=list(response.output),
        tool_calls=tool_calls or None,
        response_id=response.id,
        actual_model=getattr(response, "model", None),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        reasoning_tokens=reasoning_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        x_tools=x_tools_str,
        duration_seconds=round(duration, 3),
        requested_model=model,
        temperature=temperature,
    )


def call_llm(
    client: OpenAI,
    model: str,
    temperature: float,
    messages: list[dict],
    tools: list[dict] = None,
    max_api_retries: int = 3,
) -> LLMResponse:
    """Call the LLM via Responses API and return structured response."""
    kwargs = dict(model=model, input=messages, temperature=temperature)
    if tools is not None:
        kwargs["tools"] = tools

    t0 = time.time()
    last_error = None
    retry_delay = 2.0

    for attempt in range(max_api_retries):
        try:
            response = client.responses.create(**kwargs)
            return _parse_response(response, model, temperature, t0)
        except Exception as e:
            last_error = e
            if attempt < max_api_retries - 1:
                wait = retry_delay * (2 ** attempt)
                print(f"  LLM request attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)

    raise RuntimeError(f"LLM API failed after {max_api_retries} attempts: {last_error}") from last_error


@dataclass
class ToolCallRecord:
    """Record of a single tool call execution."""
    index: int
    tool_name: str
    call_id: str | None
    arguments: str
    output: str
    duration_seconds: float


@dataclass
class SolveStep:
    """One LLM call and its tool call results."""
    llm_result: LLMResponse
    input_messages: list
    tool_calls: list[ToolCallRecord] = field(default_factory=list)


@dataclass
class SolveResult:
    """Complete result of a solving session."""
    content: str | None
    steps: list[SolveStep]


def solve(
    client: OpenAI,
    model: str,
    temperature: float,
    messages: list[dict],
    *,
    tools: list[dict] | None = None,
    max_tool_calls: int = 0,
    run_tool_fn: Callable | None = None,
    log: Callable[[str], None] | None = None,
) -> SolveResult:
    """High-level solver with optional tool-call loop.

    Args:
        run_tool_fn: Callable(tool_call) -> (arguments_str, output_str).
            If provided, enables multi-turn tool-call loop.
            If None, makes a single LLM call.
        log: Optional logging function for progress messages.
    """
    if log is None:
        log = lambda msg: None

    if run_tool_fn is None:
        # Single-call mode (direct / native_tools)
        label = "native_tools" if tools else "direct"
        log(f"Calling LLM ({label})...")
        llm_result = call_llm(client, model, temperature, messages=messages, tools=tools)
        log(f"LLM responded ({llm_result.duration_seconds:.0f}s, "
            f"{llm_result.input_tokens or '?'} in / {llm_result.output_tokens or '?'} out"
            f"{f' / {llm_result.reasoning_tokens} reasoning' if llm_result.reasoning_tokens else ''})")
        step = SolveStep(llm_result=llm_result, input_messages=list(messages))
        return SolveResult(content=llm_result.content, steps=[step])

    # Multi-turn tool-call loop (sandbox_tools)
    input_list = list(messages)
    remaining = max_tool_calls
    steps: list[SolveStep] = []

    step_num = 0
    while remaining > 0:
        step_num += 1
        log(f"[step {step_num}] Calling LLM (sandbox_tools, {remaining} calls left)...")
        llm_result = call_llm(client, model, temperature, messages=input_list, tools=tools)

        solve_step = SolveStep(llm_result=llm_result, input_messages=list(input_list))
        steps.append(solve_step)

        if not llm_result.tool_calls:
            log(f"[step {step_num}] Final response ({llm_result.duration_seconds:.0f}s, "
                f"{llm_result.input_tokens or '?'} in / {llm_result.output_tokens or '?'} out)")
            final_content = llm_result.content
            if not final_content and llm_result.raw_output:
                # Model returned reasoning but no text — ask again without tools
                input_list.extend(llm_result.raw_output)
                step_num += 1
                log(f"[step {step_num}] No text in response, requesting final answer...")
                llm_result = call_llm(client, model, temperature, messages=input_list)
                steps.append(SolveStep(llm_result=llm_result, input_messages=list(input_list)))
                final_content = llm_result.content
            return SolveResult(content=final_content, steps=steps)

        n_tools = len(llm_result.tool_calls)
        log(f"[step {step_num}] {n_tools} tool call(s) "
            f"({llm_result.duration_seconds:.0f}s, "
            f"{llm_result.input_tokens or '?'} in / {llm_result.output_tokens or '?'} out)")

        # Append model's raw output to input for next round
        if llm_result.raw_output:
            input_list.extend(llm_result.raw_output)

        for tc_idx, tc in enumerate(llm_result.tool_calls):
            tool_name = getattr(tc, "name", "python")
            log(f"  -> {tool_name}")

            t_tool = time.time()
            arguments, output_text = run_tool_fn(tc)
            tool_duration = time.time() - t_tool

            remaining -= 1
            if remaining <= 3 and remaining > 0:
                output_text += f"\n\n[Warning: {remaining} tool call(s) remaining]"
            elif remaining <= 0:
                output_text += "\n\n[No more tool calls allowed. Please provide your final answer.]"

            input_list.append({
                "type": "function_call_output",
                "call_id": getattr(tc, "call_id", None),
                "output": output_text,
            })

            solve_step.tool_calls.append(ToolCallRecord(
                index=tc_idx,
                tool_name=tool_name,
                call_id=getattr(tc, "call_id", None),
                arguments=arguments,
                output=output_text,
                duration_seconds=round(tool_duration, 3),
            ))

        if remaining <= 0:
            # Force a final response without tools
            step_num += 1
            log(f"[step {step_num}] Tool limit reached, requesting final answer...")
            llm_result = call_llm(client, model, temperature, messages=input_list)
            steps.append(SolveStep(llm_result=llm_result, input_messages=list(input_list)))
            return SolveResult(content=llm_result.content, steps=steps)

    return SolveResult(content=None, steps=steps)
