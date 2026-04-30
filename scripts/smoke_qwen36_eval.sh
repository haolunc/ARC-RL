#!/usr/bin/env bash
# Smoke test Qwen3.6 FP8 serving plus this repo's ARC evaluation loop.
set -euo pipefail

cd "$(dirname "$0")/.."

MODEL="${ARC_MODEL:-Qwen/Qwen3.6-35B-A3B-FP8}"
HOST="${ARC_HOST:-127.0.0.1}"
PORT="${ARC_PORT:-8000}"
TP="${ARC_TP:-1}"
CONTEXT_LENGTH="${ARC_CONTEXT_LENGTH:-32768}"
MAX_TASKS="${ARC_MAX_TASKS:-5}"
MIN_VRAM_MB="${ARC_MIN_VRAM_MB:-40000}"
FORCE_SERVE="${ARC_FORCE_SERVE:-0}"

echo "=== GPU ==="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found"
fi

echo "=== Python ==="
python --version

echo "=== Reward Function Smoke ==="
PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
from arc_eval.grpo_train import arc_code_reward

completion = """```python
def transform(input_grid):
    return input_grid
```"""
examples = [[{"input": [[1]], "output": [[1]]}]]
print(arc_code_reward([completion], examples))
PY

echo "=== Dependency Check ==="
python - <<'PY'
import importlib.util
import sys

missing = [
    name for name in ("openai", "sglang")
    if importlib.util.find_spec(name) is None
]
if missing:
    print("Missing Python packages:", ", ".join(missing))
    print("Install them in a GPU env before serving Qwen locally.")
    sys.exit(2)
print("openai and sglang are importable")
PY

echo "=== VRAM Check ==="
if command -v nvidia-smi >/dev/null 2>&1; then
  VRAM_MB="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
  echo "Detected GPU memory: ${VRAM_MB} MiB"
  if [ "$FORCE_SERVE" != "1" ] && [ "$VRAM_MB" -lt "$MIN_VRAM_MB" ]; then
    echo "Skipping Qwen3.6 FP8 local serve: need at least ${MIN_VRAM_MB} MiB for this smoke."
    echo "Set ARC_FORCE_SERVE=1 to override, or rerun on a larger GPU node."
    exit 0
  fi
fi

echo "=== Launching SGLang ==="
python -m sglang.launch_server \
  --model-path "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --tp "$TP" \
  --context-length "$CONTEXT_LENGTH" \
  --mem-fraction-static 0.85 \
  --trust-remote-code &

SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

echo "Waiting for server on http://$HOST:$PORT/v1 ..."
for _ in $(seq 1 180); do
  if curl -fsS "http://$HOST:$PORT/v1/models" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

curl -fsS "http://$HOST:$PORT/v1/models" >/dev/null

echo "=== Endpoint Smoke ==="
python - <<'PY'
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="EMPTY")
resp = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B-FP8",
    messages=[{"role": "user", "content": "Return exactly: ok"}],
    max_tokens=16,
    temperature=0,
)
print(resp.choices[0].message.content)
PY

echo "=== ARC Eval Smoke ==="
export ARC_API_BASE_URL="http://$HOST:$PORT/v1"
export ARC_API_KEY=EMPTY
export ARC_MODEL="$MODEL"

python -m arc_eval.run \
  --dataset arc1 \
  --split training \
  --max-tasks "$MAX_TASKS" \
  --max-retries 1 \
  --temperature 0.6 \
  --run-name qwen36_fp8_smoke
