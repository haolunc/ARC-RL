
config.yaml
|
config.py
|
run threadpool
|
build prompt
|
call llm
|
test
|
database


### Overview

LLM evaluation pipeline for [ARC-AGI](https://github.com/fchollet/ARC-AGI) tasks using the Responses API. Two evaluation modes:

| Mode | Thinking | Tool Calls | Description |
|------|----------|------------|-------------|
| `sandbox_tools` | Yes | Our tool loop | Multi-round loop: LLM calls `python` tool → code runs in subprocess → result fed back. |
| `direct` | No | None | One-shot. LLM directly outputs `test_transform` function. |

All modes produce a `def test_transform(input_grid)` function, which is executed on the test input and compared against the expected output.


### Usage

```bash
python -m arc.eval.run config.yaml
```


### Configuration

Two config files:

| File | Tracked | Purpose |
|------|---------|---------|
| `config.yaml.example` | Yes | Config template — copy and edit |
| `endpoint.yaml.example` | Yes | Endpoint registry template — copy and edit |
| `.env.example` | Yes | API key template |

```bash
cp config.yaml.example config.yaml       # edit with your settings
cp endpoint.yaml.example endpoint.yaml   # edit with your endpoints
cp .env.example .env                      # fill in API keys
```

**config.yaml** references an endpoint by name from `endpoint.yaml`:

```yaml
python_path: "/path/to/python"

endpoint: qwen_official          # name from endpoint.yaml

data:
  split: training                # training or evaluation
  task_ids: null                 # null = all, or ["id1", "id2"]
  max_tasks: null

eval:
  mode: "sandbox_tools"          # sandbox_tools | direct
  max_workers: 4                 # parallel task workers
  llm_timeout: 180               # LLM API request timeout (seconds)
  run_name: null                 # null = auto timestamp
```

**endpoint.yaml** defines all available endpoints (copy from `endpoint.yaml.example`):

```yaml
endpoints:
  qwen_official:
    base_url:
    model:
    api_key_env:
```


### Resume a run

Set `run_name` in your config. Completed tasks are automatically skipped on re-run.

Results are stored in `results/<run_name>/results.db` (SQLite) with detailed token usage (reasoning_tokens, cached_tokens, x_tools).


### Module Structure

```
arc/eval/
├── run.py          # 入口：main(), evaluate_single_task(), load_tasks(), ThreadPoolExecutor
├── config.py       # 加载 config.yaml + endpoint.yaml + .env
├── prompt.py       # prompt 常量 + build_messages()
├── llm.py          # call_llm() + execute_python(): LLM 调用 + subprocess 代码执行
├── test.py         # extract_code(), compare_grids(), run_tests()
└── db.py           # ResultDB: SQLite 结果读写
```

### Module Interaction

```
run.py  main()
 ├── config.py          load_config(path) → cfg dict
 ├── run.load_tasks()   load_tasks(data_dir) → {task_id: task_data}
 ├── db.py              ResultDB(db_path)
 │
 └── evaluate_single_task(task_id, task_data, ...)
      ├── prompt.py     build_messages(train, test_inputs) → messages
      ├── llm.py        call_llm(client, messages, mode, ...) → LLMResult
      │                 execute_python(code, python_path) → result
      ├── test.py       extract_code(response_text) → code_str
      │                 run_tests(code_str, test_cases, python_path) → TestResult
      └── db.py         db.save_result(...)
```
