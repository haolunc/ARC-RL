# Qwen3.6 35B FP8 Local Serving and GRPO Plan

This repo is currently an ARC evaluation loop:

1. Build an ARC prompt.
2. Call an OpenAI-compatible chat endpoint.
3. Extract a `transform(input_grid)` Python function.
4. Execute it on ARC training examples.
5. Use exact-match / cell accuracy as verification.

That makes it a good reward harness for RLVR, but it is not yet a GRPO trainer.

## Model

Use the official FP8 model for local serving:

```bash
Qwen/Qwen3.6-35B-A3B-FP8
```

Important details from the model card:

- 35B total parameters, about 3B activated per token.
- FP8 post-trained weights in Hugging Face Transformers format.
- Compatible with SGLang, vLLM, Transformers, and KTransformers.
- Native context length is 262K tokens, but ARC should start much smaller.

## Serve Locally

SGLang is the first choice for this model. Start with a conservative context
length; 262K context is unnecessary for ARC and expensive in KV cache.

```bash
conda create -n qwen36-sglang python=3.11 -y
conda activate qwen36-sglang
pip install -U "sglang[all]>=0.5.10" openai

python -m sglang.launch_server \
  --model-path Qwen/Qwen3.6-35B-A3B-FP8 \
  --host 0.0.0.0 \
  --port 8000 \
  --tp 1 \
  --context-length 32768 \
  --mem-fraction-static 0.85 \
  --trust-remote-code
```

If the model OOMs:

- lower `--context-length` to `16384`;
- lower `--mem-fraction-static`;
- increase tensor parallelism with `--tp 2` or more;
- use a 4-bit variant for inference-only experiments.

Then point this repo at the local endpoint:

```bash
export ARC_API_BASE_URL=http://localhost:8000/v1
export ARC_API_KEY=EMPTY
export ARC_MODEL=Qwen/Qwen3.6-35B-A3B-FP8

python -m arc_eval.run \
  --dataset arc1 \
  --split training \
  --max-tasks 5 \
  --max-retries 1 \
  --temperature 0.6 \
  --run-name qwen36_fp8_smoke
```

## Why FP8 Is Not the Training Policy

Use FP8 for serving / rollouts, not as the trainable policy weights. For GRPO
post-training, the trainable model should normally be BF16 or a PEFT adapter
on top of the BF16 base. Quantized FP8 weights are great for inference memory,
but they are not the right target for optimizer updates.

Recommended split:

- Rollout / eval server: `Qwen/Qwen3.6-35B-A3B-FP8`.
- Trainable policy: `Qwen/Qwen3.6-35B-A3B` with LoRA or FSDP/DeepSpeed.
- Reward: reuse this repo's code extraction plus train-example execution.

## GRPO Path

TRL is the simplest route for a first local run.

1. Build a dataset where each row contains:
   - `prompt`: ARC task prompt without hidden test output;
   - `train_examples`: examples used by the reward function;
   - optionally `task_id`.

2. Reward each sampled completion:
   - extract Python with `arc_eval.code_extract.extract_code`;
   - run it through `arc_eval.evaluate.verify_on_train`;
   - reward exact train pass strongly;
   - optionally add partial cell-accuracy shaping.

3. Run GRPO with multiple completions per prompt, e.g. 4 to 8 samples.

4. Keep evaluation separate:
   - train reward only uses public train examples;
   - final reporting can use the existing `arc_eval.run` path.

For TRL, use vLLM acceleration if available. TRL supports both colocated vLLM
and a separate vLLM server mode; server mode is cleaner when you have dedicated
rollout GPUs.

Sketch:

```python
from trl import GRPOConfig, GRPOTrainer

args = GRPOConfig(
    output_dir="runs/qwen36_arc_grpo_lora",
    learning_rate=1e-5,
    bf16=True,
    use_peft=True,
    num_generations=4,
    max_prompt_length=8192,
    max_completion_length=2048,
    use_vllm=True,
    vllm_mode="server",
)

trainer = GRPOTrainer(
    model="Qwen/Qwen3.6-35B-A3B",
    args=args,
    train_dataset=train_dataset,
    reward_funcs=arc_code_reward,
)
trainer.train()
```

## Practical Hardware Notes

For inference-only FP8, plan around at least a large 40-80 GB GPU depending on
context length and framework support. For GRPO training a 35B MoE model, expect
multi-GPU. A realistic first experiment is:

- SFT / GRPO LoRA on a smaller Qwen model to validate the reward loop;
- then scale to Qwen3.6 35B once the reward is stable;
- keep `max_completion_length` small at first, because code generation reward
  is slow due to subprocess execution.

## Next Implementation Step

Add `arc_eval/grpo_train.py` with:

- ARC dataset construction;
- `arc_code_reward(completions, train_examples, **kwargs)`;
- TRL `GRPOTrainer` wiring;
- CLI flags for model, output dir, dataset split, max tasks, and generation
  length.

The existing evaluation code can remain as the final benchmark runner.
