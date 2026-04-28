# ARC GPRO Poster Summary

- Run directory: `results/run20_grpo_parameter1`
- Model: `qwen3.6-35b-a3b`
- Dataset: `arc1` / `training`
- Group size: `4`
- GPRO steps: `5`
- Temperature: `0.7`

## Core Metrics
- Tasks solved: **12/20 (60.0%)**
- Test cases passed: **12/20**
- Total attempts logged: **64**
- Avg task time: **8015.51s** (p50=433.64s, max=52985.36s)
- GPRO sample count: **200**
- Avg GPRO reward: **-0.4146**

## Attempt Outcomes
- success: 26
- api_error: 19
- train_fail: 17
- wrong_output: 1
- test_exec_error: 1

## Reward by GPRO Step
- Step 1: n=80, avg_reward=0.1026, max_reward=1.0, train_pass=34
- Step 2: n=36, avg_reward=-0.5116, max_reward=1.0, train_pass=6
- Step 3: n=28, avg_reward=-0.7786, max_reward=0.42, train_pass=0
- Step 4: n=28, avg_reward=-0.8916, max_reward=0.42, train_pass=0
- Step 5: n=28, avg_reward=-0.9264, max_reward=0.42, train_pass=0

## Output Files
- `poster_metrics.csv`
- `poster_outcomes.csv`
- `poster_step_rewards.csv`
