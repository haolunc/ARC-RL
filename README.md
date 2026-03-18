# ARC-RL

LLM evaluation pipeline for [ARC-AGI](https://github.com/fchollet/ARC-AGI) tasks using the Responses API. Three evaluation modes:

| Mode | Thinking | Tool Calls | Description |
|------|----------|------------|-------------|
| `native_tools` | Yes | API code_interpreter | Single API call. Server runs code internally. |
| `sandbox_tools` | Yes | Our tool loop | Multi-round loop: LLM calls `python` tool → code runs in subprocess → result fed back. |
| `direct` | No | None | One-shot. LLM directly outputs `test_transform` function. |

All modes produce a `def test_transform(input_grid)` function, which is executed on the test input and compared against the expected output.

## Setup

```bash
conda create -n arc python=3.11
conda activate arc
pip install -e .
```

## Configuration

Two config files:

| File | Tracked | Purpose |
|------|---------|---------|
| `config.yaml.example` | Yes | Config template — copy and edit |
| `endpoint.yaml.example` | Yes | Endpoint registry template — copy and edit |
| `.env.example` | Yes | API key template |

```bash
cp config.yaml.example config.yaml       # edit with your settings
cp endpoint.yaml.example endpoint.yaml   # edit with your endpoints
cp .env.example .env                      # fill in API keys
```

**config.yaml** references an endpoint by name from `endpoint.yaml`:

```yaml
python_path: "/path/to/python"

endpoint: qwen_official          # name from endpoint.yaml

data:
  split: training                # training or evaluation
  task_ids: null                 # null = all, or ["id1", "id2"]
  max_tasks: null

eval:
  mode: "native_tools"           # native_tools | sandbox_tools | direct
  max_workers: 4                 # parallel task workers
  llm_timeout: 180               # LLM API request timeout (seconds)
  run_name: null                 # null = auto timestamp
```

**endpoint.yaml** defines all available endpoints (copy from `endpoint.yaml.example`):

```yaml
endpoints:
  qwen_official:
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: qwen3.5-flash
    api_key_env: QWEN_API_KEY

  greatlakes_qwen35:
    base_url: "http://localhost:8000/v1"
    model: "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"
    api_key_env: null
```

## Usage

```bash
python -m arc.eval.run config.yaml
```

### Resume a run

Set `run_name` in your config. Completed tasks are automatically skipped on re-run.

Results are stored in `results/<run_name>/results.db` (SQLite) with detailed token usage (reasoning_tokens, cached_tokens, x_tools).

## Testing

```bash
# Unit tests only (no API calls)
pytest tests/ -m "not llm"

# Integration tests with real LLM API
pytest tests/test_llm_integration.py -m llm --endpoint-config config.yaml

# Specific mode
pytest tests/test_llm_integration.py -k native_tools --endpoint-config config.yaml
```

## Reference Solutions

`reference_solutions/solutions/` contains 651 verified-correct `def transform` Python solutions downloaded from [Trelis/arc-agi-2-reasoning-5](https://huggingface.co/datasets/Trelis/arc-agi-2-reasoning-5) (Apache 2.0). Each file is named `{task_id}.py`.

| Subset               | Coverage          |
|----------------------|-------------------|
| ARC-AGI-1 training   | 323 / 400 (80.8%) |
| ARC-AGI-1 evaluation | 243 / 400 (60.8%) |
| ARC-AGI-2 training   | 648 / 1000 (64.8%)|

```bash
pip install datasets
python reference_solutions/download.py
```

## File Structure

```
.
├── .env.example                # API key template
├── config.yaml.example         # Config template
├── endpoint.yaml.example       # Endpoint registry template
├── endpoint.yaml               # Endpoint registry (gitignored)
├── pyproject.toml
├── README.md
│
├── arc/                        # Main package
│   └── eval/                   # Evaluation pipeline
│       ├── code_extract.py     # Extract test_transform() from LLM response
│       ├── config.py           # Config + endpoint loading
│       ├── db.py               # SQLite results storage
│       ├── evaluate.py         # Grid comparison
│       ├── llm_client.py       # Responses API client
│       ├── prompt.py           # Prompt construction (3 modes)
│       ├── run.py              # CLI entry point + evaluation loop
│       ├── safe_exec.py        # Subprocess code execution
│       └── tools.py            # Python tool for sandbox_tools mode
│
├── tests/
│   ├── test_code_extract.py    # No API
│   ├── test_evaluate.py        # No API
│   ├── test_safe_exec.py       # No API
│   ├── test_tools.py           # No API
│   ├── test_db.py              # No API
│   └── test_llm_integration.py # Real API (pytest -m llm)
│
├── reference_solutions/
│   └── solutions/{task_id}.py
│
└── results/<run_name>/results.db
```
