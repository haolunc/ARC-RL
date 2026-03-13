#!/bin/bash
# Run ARC-AGI-2 training evaluation in simple mode with caffeinate

cd "$(dirname "$0")"

CONFIG="config_arc2_simple.yaml"

# Create config if it doesn't exist
if [ ! -f "$CONFIG" ]; then
  cat > "$CONFIG" <<'EOF'
python_path: "/opt/homebrew/Caskroom/miniforge/base/envs/arc/bin/python"

datasets:
  arc1:
    training: "ARC-AGI/data/training"
    evaluation: "ARC-AGI/data/evaluation"
  arc2:
    training: "ARC-AGI-2/data/training"
    evaluation: "ARC-AGI-2/data/evaluation"

endpoint:
  base_url: "http://promaxgb10-d668.eecs.umich.edu:8000/v1"
  model: "Qwen/Qwen3-VL-30B-A3B-Instruct"
  api_key_env: CLASS_QWEN_API_KEY
  temperature: 0.7
  llm_timeout: 180

data:
  dataset: arc2
  split: training
  task_ids: null
  max_tasks: null

eval:
  mode: "simple"
  max_retries: 5
  timeout: 30
  run_name: "arc2_training_simple"
EOF
  echo "Created $CONFIG"
fi

caffeinate -dims /opt/homebrew/Caskroom/miniforge/base/envs/arc/bin/python -m arc.eval.run "$CONFIG"
