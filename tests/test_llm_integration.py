"""LLM integration tests — require a real API endpoint.

Run with: pytest tests/test_llm_integration.py -m llm --endpoint-config config.yaml
"""

import pytest

from arc.eval.config import load_config, TEMPERATURE
from openai import OpenAI
from arc.eval.llm_client import call_llm
from arc.eval.prompt import build_messages
from arc.eval.code_extract import extract_code
from arc.eval.safe_exec import execute_transform
from arc.eval.evaluate import compare_grids
from arc.eval.tools import TOOL_DEFINITION, extract_tool_code, run_python_tool

from .conftest import PYTHON_PATH

pytestmark = pytest.mark.llm


@pytest.fixture(scope="module")
def endpoint_cfg(request):
    config_path = request.config.getoption("--endpoint-config")
    if config_path is None:
        pytest.skip("--endpoint-config not provided")
    return load_config(config_path)


@pytest.fixture(scope="module")
def llm_ready(endpoint_cfg):
    """Create the LLM client for the module."""
    ep = endpoint_cfg["endpoint"]
    ev = endpoint_cfg["eval"]
    client = OpenAI(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        timeout=float(ev["llm_timeout"]),
    )
    return {
        "client": client,
        "model": ep["model"],
        "temperature": TEMPERATURE,
        "cfg": endpoint_cfg,
    }


@pytest.fixture
def simple_task():
    """Load a simple ARC task (007bbfb7) for testing."""
    from .conftest import load_task
    return load_task("007bbfb7")


def test_basic_responses_api(llm_ready):
    """Verify that the Responses API returns a valid response."""
    result = call_llm(
        llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
        messages=[{"role": "user", "content": "Say hello in one word."}],
    )
    assert result.content is not None
    assert len(result.content.strip()) > 0
    assert result.input_tokens is not None
    assert result.output_tokens is not None
    assert result.duration_seconds > 0


def test_token_details(llm_ready):
    """Verify that extended token details are captured."""
    result = call_llm(
        llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
        messages=[{"role": "user", "content": "What is 2+2?"}],
    )
    assert result.total_tokens is not None
    assert result.total_tokens > 0
    # reasoning_tokens may or may not be present depending on model
    print(f"Token details: input={result.input_tokens}, output={result.output_tokens}, "
          f"reasoning={result.reasoning_tokens}, total={result.total_tokens}")


def test_direct_mode_single_task(llm_ready, simple_task):
    """Mode C: direct — single call, extract test_transform, evaluate."""
    train_examples = simple_task["train"]
    test_input = simple_task["test"][0]["input"]
    test_output = simple_task["test"][0]["output"]

    input_msgs = build_messages("direct", train_examples, test_input)
    result = call_llm(llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
                      messages=input_msgs)

    assert result.content is not None
    code = extract_code(result.content)
    # The LLM may or may not produce a correct solution — just verify the pipeline works
    print(f"Direct mode: extracted code = {code is not None}, "
          f"tokens = {result.input_tokens}/{result.output_tokens}")
    if code:
        test_result = execute_transform(code, test_input, timeout=30, python_path=PYTHON_PATH)
        if test_result["success"]:
            cmp = compare_grids(test_result["output"], test_output)
            print(f"Direct mode: correct={cmp['correct']}, cell_acc={cmp['cell_accuracy']:.1%}")


def test_native_tools_mode_single_task(llm_ready, simple_task):
    """Mode A: native_tools — single call with code_interpreter."""
    if llm_ready["cfg"]["eval"]["mode"] != "native_tools":
        pytest.skip("Config mode is not native_tools")

    train_examples = simple_task["train"]
    test_input = simple_task["test"][0]["input"]

    input_msgs = build_messages("native_tools", train_examples, test_input)
    result = call_llm(
        llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
        messages=input_msgs,
        tools=[{"type": "code_interpreter"}],
    )

    assert result.content is not None or result.output_items
    print(f"Native tools: output_items count = {len(result.output_items or [])}, "
          f"tokens = {result.input_tokens}/{result.output_tokens}, "
          f"x_tools = {result.x_tools}")


def test_sandbox_tools_mode_single_task(llm_ready, simple_task):
    """Mode B: sandbox_tools — tool call loop with python tool."""
    train_examples = simple_task["train"]
    test_input = simple_task["test"][0]["input"]

    task_context = {
        "train_examples": train_examples,
        "test_input": test_input,
        "timeout": 30,
        "python_path": PYTHON_PATH,
    }

    input_list = build_messages("sandbox_tools", train_examples, test_input)
    max_calls = 3  # keep it short for testing
    remaining = max_calls
    steps = 0

    while remaining > 0:
        steps += 1
        result = call_llm(llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
                         messages=input_list, tools=[TOOL_DEFINITION])

        if not result.tool_calls:
            break

        if result.output_items:
            input_list.extend(result.output_items)

        for tc in result.tool_calls:
            code = extract_tool_code(tc)
            tool_result = run_python_tool(code, task_context)
            remaining -= 1

            output_text = tool_result["output"]
            if remaining <= 0:
                output_text += "\n\n[No more tool calls allowed.]"

            input_list.append({
                "type": "function_call_output",
                "call_id": getattr(tc, "call_id", None),
                "output": output_text,
            })

        if remaining <= 0:
            result = call_llm(llm_ready["client"], llm_ready["model"], llm_ready["temperature"],
                             messages=input_list)
            break

    print(f"Sandbox tools: {steps} step(s), final content length = {len(result.content or '')}")
    assert steps >= 1
