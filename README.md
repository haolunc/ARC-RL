# ARC-RL

LLM evaluation pipeline for [ARC-AGI](https://github.com/fchollet/ARC-AGI) tasks. Supports two evaluation modes:

- **Simple mode**: Retry loop — prompt LLM, extract code via regex, execute, give feedback, retry.
- **Agentic mode**: Tool-call loop — LLM actively explores grids, tests solutions, and submits answers via tool calls (`run_python`, `test_transform`, `submit_transform`).

## Setup

```bash
# Create conda environment
conda create -n arc python=3.11
conda activate arc
pip install -e .
```

## Configuration

All settings live in a single YAML config file. Two template files are provided:

| File | Tracked | Purpose |
|------|---------|---------|
| `config.yaml.example` | Yes | Config template — copy and edit |
| `.env.example` | Yes | API key template |

To get started:

```bash
cp config.yaml.example config.yaml   # edit with your endpoint and settings
cp .env.example .env                  # fill in API keys
```

The config file has five sections:

```yaml
python_path: "/path/to/python"       # Python interpreter for code execution

datasets:                             # Dataset path mappings
  arc1:
    training: "ARC-AGI/data/training"
    evaluation: "ARC-AGI/data/evaluation"
  arc2:
    training: "ARC-AGI-2/data/training"
    evaluation: "ARC-AGI-2/data/evaluation"

endpoint:                             # LLM endpoint settings
  base_url: "http://your-server:8000/v1"
  model: "Qwen/Qwen3-VL-30B-A3B-Instruct"
  api_key_env: QWEN_API_KEY           # env var name (actual key in .env)
  temperature: 0.7

data:                                 # What to evaluate
  dataset: arc1                       # arc1 or arc2
  split: training                     # training or evaluation
  task_ids: null                      # null = all tasks, or ["id1", "id2"]
  max_tasks: null                     # null = no limit

eval:                                 # Evaluation parameters
  mode: "simple"                      # "simple" (retry loop) or "agentic" (tool calls)
  max_retries: 5                      # max retry attempts (simple mode)
  max_steps: 20                       # max tool-call rounds (agentic mode)
  timeout: 30                         # code execution timeout in seconds
  run_name: null                      # null = auto timestamp
```

## Usage

The CLI takes a single argument — the path to a config YAML:

```bash
# Simple mode (default)
python -m arc.eval.run config.yaml

# Agentic mode — set mode: "agentic" in config.yaml, then:
python -m arc.eval.run config.yaml
```

### Resume a run

Set `run_name` in your config. Completed tasks are automatically skipped — just re-run the same command.

```yaml
eval:
  run_name: my_experiment    # reuse to resume
```

Results are stored in `results/<run_name>/results.db` (SQLite).

For detailed documentation on both evaluation modes, see [`docs/eval.md`](docs/eval.md).

## Reference Solutions

`reference_solutions/solutions/` contains 651 verified-correct `def transform` Python solutions downloaded from [Trelis/arc-agi-2-reasoning-5](https://huggingface.co/datasets/Trelis/arc-agi-2-reasoning-5) (Apache 2.0). Each file is named `{task_id}.py`.

| Subset               | Coverage          |
|----------------------|-------------------|
| ARC-AGI-1 training   | 323 / 400 (80.8%) |
| ARC-AGI-1 evaluation | 243 / 400 (60.8%) |
| ARC-AGI-2 training   | 648 / 1000 (64.8%)|

These can be used to test the evaluation pipeline without calling an LLM. To re-download or update:

```bash
pip install datasets
python reference_solutions/download.py
```

See [`reference_solutions/SUMMARY.md`](reference_solutions/SUMMARY.md) for full statistics.

## File Structure

```
.
├── .env.example                # API key template
├── .gitignore
├── config.yaml.example         # Config template
├── pyproject.toml
├── README.md
│
├── arc/                        # Main package
│   ├── __init__.py
│   └── eval/                   # Evaluation pipeline
│       ├── __init__.py
│       ├── code_extract.py     # Extract transform() + thinking from LLM response
│       ├── config.py           # Config loading (unified YAML)
│       ├── db.py               # SQLite results storage
│       ├── evaluate.py         # Grid comparison and train verification
│       ├── llm_client.py       # LLM API client (text + tool-call modes)
│       ├── prompt.py           # Prompt construction (simple + agentic)
│       ├── run.py              # CLI entry point (simple + agentic loops)
│       ├── safe_exec.py        # Sandboxed code execution (transform + analysis)
│       └── tools.py            # Tool definitions + dispatcher (agentic mode)
│
├── docs/
│   ├── dataset_overlap.md
│   └── eval.md
│
├── reference_solutions/
│   ├── download.py             # Download script (HuggingFace)
│   ├── SUMMARY.md
│   └── solutions/              # 651 verified transform() files
│       └── {task_id}.py
│
├── results/                    # Evaluation run outputs
│   └── <run_name>/
│       └── results.db          # SQLite database
│
├── ARC-AGI/                    # ARC-AGI-1 dataset (cloned, not in repo)
│   └── data/{training,evaluation}/*.json
│
└── ARC-AGI-2/                  # ARC-AGI-2 dataset (cloned, not in repo)
    └── data/{training,evaluation}/*.json
```
