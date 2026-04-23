# ARC GPRO Poster Summary

- Run directory: `results/arc2_train_100`
- Model: `qwen3.6-35b-a3b`
- Dataset: `arc2` / `training`
- Group size: `2`
- GPRO steps: `2`
- Temperature: `0.7`

## Core Metrics
- Tasks solved: **48/100 (48.0%)**
- Test cases passed: **51/104**
- Total attempts logged: **218**
- Avg task time: **294.67s** (p50=255.54s, max=1727.13s)
- GPRO sample count: **324**
- Avg GPRO reward: **0.1181**

## Attempt Outcomes
- success: 107
- train_fail: 96
- api_error: 10
- wrong_output: 4
- test_exec_error: 1

## Reward by GPRO Step
- Step 1: n=208, avg_reward=0.2441, max_reward=1.0, train_pass=78
- Step 2: n=116, avg_reward=-0.1078, max_reward=1.0, train_pass=12

## Output Files
- `poster_metrics.csv`
- `poster_outcomes.csv`
- `poster_step_rewards.csv`
