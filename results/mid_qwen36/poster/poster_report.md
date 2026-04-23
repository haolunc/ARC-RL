# ARC GPRO Poster Summary

- Run directory: `results/mid_qwen36`
- Model: `qwen3.6-35b-a3b`
- Dataset: `arc1` / `training`
- Group size: `4`
- GPRO steps: `5`
- Temperature: `0.8`

## Core Metrics
- Tasks solved: **15/20 (75.0%)**
- Test cases passed: **15/20**
- Total attempts logged: **57**
- Avg task time: **704.11s** (p50=296.98s, max=3633.94s)
- GPRO sample count: **160**
- Avg GPRO reward: **0.1919**

## Attempt Outcomes
- success: 32
- train_fail: 23
- wrong_output: 2

## Reward by GPRO Step
- Step 1: n=80, avg_reward=0.3873, max_reward=1.0, train_pass=35
- Step 2: n=32, avg_reward=0.1664, max_reward=1.0, train_pass=2
- Step 3: n=24, avg_reward=0.1757, max_reward=1.0, train_pass=3
- Step 4: n=12, avg_reward=-0.3189, max_reward=0.6458, train_pass=0
- Step 5: n=12, avg_reward=-0.5, max_reward=-0.5, train_pass=0

## Output Files
- `poster_metrics.csv`
- `poster_outcomes.csv`
- `poster_step_rewards.csv`
