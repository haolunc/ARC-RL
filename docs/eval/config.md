# Configuration

## Config Files

| File | Tracked | Purpose |
|------|---------|---------|
| `config.yaml.example` | Yes | Config template — copy and edit |
| `endpoint.yaml.example` | Yes | Endpoint registry template — copy and edit |
| `.env.example` | Yes | API key template |

```bash
cp config.yaml.example config.yaml
cp endpoint.yaml.example endpoint.yaml
cp .env.example .env
```

## Config YAML

```yaml
python_path: "/path/to/python"

endpoint: qwen_official             # name from endpoint.yaml

data:
  split: training                   # training or evaluation
  task_ids: null                    # null = all tasks, or ["id1", "id2"]
  max_tasks: null                   # null = no limit

eval:
  mode: "native_tools"              # native_tools | sandbox_tools | direct
  max_workers: 4                    # parallel task evaluation (1 = sequential)
  llm_timeout: 180                  # LLM API request timeout (seconds)
  run_name: null                    # null = auto timestamp, or "my_experiment"
```

## Config Fields

| Field | Type | Description |
|-------|------|-------------|
| `python_path` | string | Path to Python interpreter for code execution |
| `endpoint` | string | Endpoint name from `endpoint.yaml` |
| `data.split` | string | `training` or `evaluation` |
| `data.task_ids` | list/null | Specific task IDs to evaluate, or null for all |
| `data.max_tasks` | int/null | Limit number of tasks, or null for no limit |
| `eval.mode` | string | `native_tools`, `sandbox_tools`, or `direct` |
| `eval.max_workers` | int | Number of parallel task workers (default: 1) |
| `eval.llm_timeout` | int | LLM API request timeout in seconds |
| `eval.run_name` | string/null | Run name for results directory; null = auto timestamp |

## Hardcoded Defaults

These values are constants in `arc/eval/config.py`:

| Constant | Value | Description |
|----------|-------|-------------|
| `EXEC_TIMEOUT` | 30 | Code execution timeout (seconds) |
| `MAX_TOOL_CALLS` | 10 | Max tool calls for sandbox_tools mode |
| `TEMPERATURE` | 0.7 | LLM sampling temperature |

Data is always loaded from `ARC-AGI-2/data/{split}`.

## API Key Management

API keys are managed via `.env` (loaded by `python-dotenv`). The `api_key_env` field in `endpoint.yaml` specifies the environment variable name:

```yaml
endpoints:
  qwen_official:
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: qwen3.5-flash
    api_key_env: QWEN_API_KEY    # .env should have QWEN_API_KEY=sk-...
```

## Resume a Run

Set a fixed `run_name` and re-run. Completed tasks are automatically skipped:

```yaml
eval:
  run_name: exp01
```
