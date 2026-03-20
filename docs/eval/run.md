
### Run — 入口与并发执行

检查错误处理链条，能保证正常运行，以及报错的保存！

---

### evaluate_single_task

串起 prompt → LLM → test → DB 的核心函数：

```python
def evaluate_single_task(
    task_id: str,
    task_data: dict,
    client,
    cfg: dict,
    db: ResultDB,
    run_name: str,
) -> dict:
    start = time.time()
    mode = cfg["eval"]["mode"]

    try:
        # 1. Build prompt
        messages = build_messages(task_data["train"], [tc["input"] for tc in task_data["test"]])

        # 2. Call LLM
        llm_result = call_llm(client, cfg, messages)
        # llm_result: LLMResult(text, usage, tool_rounds)

        # 3. Extract code
        code = extract_code(llm_result.text)
        if code is None:
            → save status="error_extract", return

        # 4. Run tests
        test_result = run_tests(code, task_data["test"], cfg["python_path"])

        # 5. Save result
        → save with test_result.status, return

    except Exception as e:
        → save status="error_llm", error_message=str(e), return
```

---

### main

```python
def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument("config", type=str, help="Path to config YAML file")
    args = parser.parse_args()

    cfg = load_config(args.config)
    project_root = Path(__file__).resolve().parent.parent.parent

    # Initialize LLM client
    ep = cfg["endpoint"]
    ev = cfg["eval"]
    client = OpenAI(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        timeout=float(ev["llm_timeout"]),
    )

    python_path = cfg["python_path"]
    mode = ev["mode"]
    max_workers = ev.get("max_workers", 1)

    split = cfg["data"]["split"]
    max_tasks = cfg["data"].get("max_tasks")
    cfg_task_ids = cfg["data"].get("task_ids")

    # Resolve data directory
    data_dir = project_root / _DATA_DIR_TEMPLATE.format(split=split)
    all_tasks = load_tasks(str(data_dir))

    # Task selection
    if cfg_task_ids:
        tasks = {tid: all_tasks[tid] for tid in cfg_task_ids}
    elif max_tasks:
        tasks = dict(list(all_tasks.items())[:max_tasks])
    else:
        tasks = all_tasks

    # Determine run name, open/create DB
    run_name = ev.get("run_name") or datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    db = ResultDB(results_dir / "results.db")

    # Dedup — skip already completed tasks
    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print(f"Run: {run_name} | Mode: {mode} | Tasks: {len(remaining)}/{len(tasks)} remaining")

    # ThreadPoolExecutor 并发执行
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(evaluate_single_task, tid, td, client, cfg, db, run_name): tid
            for tid, td in remaining.items()
        }
        for future in as_completed(futures):
            tid = futures[future]
            result = future.result()
            completed += 1
            status = result["status"]
            print(f"[{completed}/{len(remaining)}] {tid}: {status}")

    # Print summary
    summary = db.get_run_summary(run_name)
    print(f"\nDone. Accuracy: {summary['correct']}/{summary['total']} ({summary['accuracy']:.1%})")
```
