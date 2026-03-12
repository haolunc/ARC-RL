# ARC-RL

LLM evaluation pipeline for [ARC-AGI](https://github.com/fchollet/ARC-AGI) tasks. Sends ARC puzzles to an LLM, extracts Python `transform` functions from responses, verifies them against training examples, and scores on held-out test cases.

## Setup

```bash
# Create conda environment
conda create -n arc python=3.11
conda activate arc
pip install -e .

# Clone datasets
git clone --depth 1 https://github.com/fchollet/ARC-AGI.git
git clone --depth 1 https://github.com/arcprize/ARC-AGI-2.git
```

## Configuration

Three config files, two of which are gitignored:

| File | Tracked | Purpose |
|------|---------|---------|
| `config.yaml` | Yes | Python path, dataset paths, default params |
| `endpoint.yaml` | No | LLM endpoint URLs, models, API key env vars |
| `.env` | No | API keys (loaded via `python-dotenv`) |

To get started:

```bash
cp endpoint.yaml.example endpoint.yaml   # edit with your endpoint
cp .env.example .env                      # fill in API keys
```

## Usage

```bash
# Evaluate on ARC-AGI training set (default)
python -m arc.eval.run

# Evaluate on ARC-AGI-2 evaluation split, max 10 tasks
python -m arc.eval.run --dataset arc2 --split evaluation --max-tasks 10

# Run a single task
python -m arc.eval.run --task-id 00d62c1b

# Adjust retries, timeout, temperature
python -m arc.eval.run --max-retries 3 --timeout 60 --temperature 0.5

# Resume a named run
python -m arc.eval.run --run-name my_run
```

Results are stored in `results/<run_name>/results.db` (SQLite).

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
