# Baseline Results

This repository tracks two selected baseline runs from `refactor/v2`. The large raw transcript databases, SQLite WAL/SHM sidecars, flash smoke-test run, and report build artifacts are intentionally excluded from the integration branch.

## Selected Runs

| Run | Split | Tasks | Correct | Accuracy | Status Breakdown | Tool Rounds | Avg Duration |
|-----|-------|-------|---------|----------|------------------|-------------|--------------|
| `results/train_sandbox_gl/results.db` | training | 300 | 114 | 38.0% | success 114, error_extract 138, wrong_answer 37, error_exec 8, error_llm 3 | 1366 | 902.3s |
| `results/evaluation_sandbox_gl/results.db` | evaluation | 120 | 6 | 5.0% | success 6, wrong_answer 69, error_llm 30, error_extract 8, error_exec 7 | 1835 | 5590.0s |

## Token Totals

| Run | Input Tokens | Output Tokens | Cached Tokens |
|-----|--------------|---------------|---------------|
| `train_sandbox_gl` | 38,432,185 | 7,275,578 | 28,773,888 |
| `evaluation_sandbox_gl` | 82,705,871 | 7,392,112 | 21,752,288 |

## Dates

| Run | First Result | Last Result |
|-----|--------------|-------------|
| `train_sandbox_gl` | 2026-03-22 04:28:00 | 2026-03-22 21:02:24 |
| `evaluation_sandbox_gl` | 2026-03-21 04:39:57 | 2026-03-21 23:58:20 |
