# GRPO Training Notes

The current `arc_eval.gpro` implementation is not true online GRPO training. It
is grouped sampling plus verifier feedback:

1. Build an ARC prompt for one task.
2. Sample a group of candidate programs.
3. Execute each candidate on training examples.
4. Assign a reward from training-example correctness.
5. Use the best candidate for retry or final test execution.

That is useful for collecting rollout data, but it does not update model
weights. Actual GRPO training requires a locally trainable model, GPU resources,
and a trainer such as TRL.

## Collect Rollouts

Run GPRO with prompt/response logging enabled:

```bash
RUN_NAME=grpo_rollout_arc1_20 \
DATASET=arc1 \
SPLIT=training \
MAX_TASKS=20 \
GROUP_SIZE=4 \
GPRO_STEPS=3 \
TEMPERATURE=0.8 \
LOG_SAMPLE_TEXT=1 \
./run_gpro.sh
```

Export the logged samples:

```bash
python -m arc_eval.export_grpo_data results/grpo_rollout_arc1_20
```

The output is:

```text
results/grpo_rollout_arc1_20/grpo_rollouts.jsonl
```

Each row contains:

- `messages`: chat messages used as the prompt.
- `prompt`: flattened prompt text.
- `completion`: sampled model response.
- `extracted_code`: extracted Python code, when extraction succeeded.
- `reward`: verifier reward from ARC training examples.
- `train_pass`: whether the sampled program solved all training examples.

## Recommended Training Direction

Use the exported file in two phases:

1. SFT warm start: train on high-reward rows, e.g. `reward >= 1.0`.
2. GRPO / preference optimization: use the verifier reward as the reward signal
   while sampling groups from the trainable local model.

For an ablation in the project report, keep GRPO training separate from the API
evaluation runs. The clean comparison should be:

- No GPRO: `run_ablation.sh`, one sample per task, no group search.
- GPRO inference: `run_gpro.sh`, grouped sampling and retry, no weight update.
- GRPO-trained model: same evaluator as above, but with the trained checkpoint.

This separation prevents mixing inference-time search gains with training gains.
