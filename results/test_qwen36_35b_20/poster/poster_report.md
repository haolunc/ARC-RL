# ARC GPRO Poster Summary

- Run directory: `results/test_qwen36_35b_20`
- Model: `qwen3.6-35b-a3b`
- Dataset: `arc1` / `training`
- Group size: `1`
- GPRO steps: `1`
- Temperature: `0.7`

## Core Metrics
- Tasks solved: **10/20 (50.0%)**
- Test cases passed: **10/20**
- Total attempts logged: **31**
- Avg task time: **78.49s** (p50=57.78s, max=363.71s)
- GPRO sample count: **20**
- Avg GPRO reward: **0.4928**

## Attempt Outcomes
- success: 21
- train_fail: 9
- wrong_output: 1

## Reward by GPRO Step
- Step 1: n=20, avg_reward=0.4928, max_reward=1.0, train_pass=11

## Output Files
- `poster_metrics.csv`
- `poster_outcomes.csv`
- `poster_step_rewards.csv`
