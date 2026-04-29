# Comprehensive Metrics: Training vs Evaluation

## Summary Table

| Metric | Train | Eval | Difference |
|--------|-------|------|------------|
| **Total Tasks Evaluated** | 100 | 50 | - |
| **Tasks Solved** | 48 | 2 | -46 |
| **Solve Rate (%)** | 48.00% | 4.00% | -44.00pp |
| | | | |
| **Total Test Cases** | 104 | 75 | - |
| **Test Cases Passed** | 51 | 3 | - |
| **Test Case Pass Rate (%)** | 49.04% | 4.00% | -45.04pp |
| | | | |
| **Total Attempts** | 218 | 153 | - |
| **Correct Attempts** | 51 | 3 | - |
| **Attempt Success Rate (%)** | 23.39% | 1.96% | -21.43pp |
| **Avg Attempts per Task** | 2.18 | 3.06 | 0.88 |
| **Max Attempts per Task** | 5 | 6 | - |
| | | | |
| **Total Tokens Used** | 280,455 | 311,809 | 31,354 |
| **Avg Tokens per Attempt** | 1286.49 | 2037.97 | 751.48 |
| **Min Tokens per Attempt** | 208 | 548 | - |
| **Max Tokens per Attempt** | 5425 | 4058 | - |
| **Avg Tokens per Solved Task** | 5842.81 | 155904.50 | - |
| | | | |
| **Avg Cell Accuracy** | 0.9537 | 0.5961 | -0.3576 |
| **Attempts ≥50% Accurate** | 149 | 49 | - |
| **Perfect Accuracy Attempts** | 107 | 7 | - |
| | | | |
| **Avg Time per Task (sec)** | 294.67 | 639.23 | - |
| **Total Runtime (sec)** | 29466.83 | 31961.68 | - |

## Outcome Breakdown

| Outcome Category | Train | Eval |
|---|---|---|
| api_error | 10 (4.6%) | 9 (5.9%) |
| non_executable | 1 (0.5%) | 0 (0.0%) |
| success | 107 (49.1%) | 7 (4.6%) |
| train_fail | 96 (44.0%) | 136 (88.9%) |
| wrong_output | 4 (1.8%) | 1 (0.7%) |

## Key Insights

- **Generalization Gap**: 44.00 percentage points (Train 48.0% vs Eval 4.0%)
- **Token Cost**: Eval requires 751 MORE tokens per attempt (+58.4%)
- **Inference Efficiency**: Train solves tasks with 5843 avg tokens/solved task
- **Inference Efficiency**: Eval solves tasks with 155904 avg tokens/solved task
- **Error Profile**: Eval has 10 API errors vs Train's 10
- **Pattern Recognition**: Eval ~2.0% attempt success vs Train's 23.4%
