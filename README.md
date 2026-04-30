# ARC-RL

LLM evaluation pipeline for [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2) tasks.

## Setup

```bash
conda activate arc
pip install -e .
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
| `tree_search` | MCTS-style tree search over multiple solution attempts with PUCT selection and refinement (see [docs/tree_search.md](docs/tree_search.md)) |

## Results

Results are stored in `results/<run_name>/results.db` (SQLite). Set `run_name` in config to resume a previous run; completed tasks are automatically skipped.

Two baseline result databases are tracked:

| Run | Split | Tasks | Correct | Accuracy |
|-----|-------|-------|---------|----------|
| `results/train_sandbox_gl/results.db` | training | 300 | 114 | 38.0% |
| `results/evaluation_sandbox_gl/results.db` | evaluation | 120 | 6 | 5.0% |

See [docs/baseline_results.md](docs/baseline_results.md) for status and token summaries.

## Testing

Tests read `python_path` and endpoint settings from `test_config.yaml`, so create one first:

```bash
cp config.yaml.example test_config.yaml
# Edit test_config.yaml with your settings
```

```bash
# Run all unit tests (no API calls)
python -m pytest tests/ -v -m "not api"

# Run API tests (calls live LLM endpoint from test_config.yaml)
python -m pytest tests/ -v -m api
```

## Project Structure

```
arc/eval/
├── run.py          # Entry point, data loading, ThreadPoolExecutor
├── config.py       # Config loading
├── prompt.py       # Prompt constants + message building
├── llm.py          # LLM calling + subprocess code execution
├── test.py         # Code extraction, grid comparison, test running
├── tree.py         # MCTS tree search: TreeNode, PUCT, scoring
└── db.py           # SQLite result storage
```
