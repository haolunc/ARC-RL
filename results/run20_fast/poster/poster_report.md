# ARC GPRO Poster Summary

- Run directory: `results/run20_fast`
- Model: `qwen3.6-35b-a3b`
- Dataset: `arc1` / `training`
- Group size: `4`
- GPRO steps: `5`
- Temperature: `0.7`

## Core Metrics
- Tasks solved: **9/20 (45.0%)**
- Test cases passed: **9/20**
- Total attempts logged: **30**
- Avg task time: **212.64s** (p50=141.4s, max=551.69s)
- GPRO sample count: **20**
- Avg GPRO reward: **0.1360**

## Attempt Outcomes
- success: 19
- train_fail: 5
- api_error: 5
- wrong_output: 1

## Reward by GPRO Step
- Step 1: n=20, avg_reward=0.136, max_reward=1.0, train_pass=10

## Output Files
- `poster_metrics.csv`
- `poster_outcomes.csv`
- `poster_step_rewards.csv`
