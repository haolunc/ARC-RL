# ARC-RL

LLM evaluation pipeline for [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2) tasks.

## Setup

```bash
cp config.yaml.example config.yaml
cp endpoint.yaml.example endpoint.yaml
cp .env.example .env
# Edit each file with your settings
```

## Usage

```bash
python -m arc.eval.run config.yaml
```

## Evaluation Modes

| Mode | Description |
|------|-------------|
| `sandbox_tools` | Multi-round: LLM calls Python tool → code runs in subprocess → result fed back |
| `direct` | One-shot: LLM directly outputs `test_transform` function |

## Results

Results are stored in `results/<run_name>/results.db` (SQLite). Set `run_name` in config to resume a previous run — completed tasks are automatically skipped.

## Project Structure

```
arc/eval/
├── run.py          # Entry point, data loading, ThreadPoolExecutor
├── config.py       # Config loading
├── prompt.py       # Prompt constants + message building
├── llm.py          # LLM calling + subprocess code execution
├── test.py         # Code extraction, grid comparison, test running
└── db.py           # SQLite result storage
```
