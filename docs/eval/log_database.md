
### Database

每个 run 的结果存储在 `results/<run_name>/results.db`（SQLite）。

---

### 表结构

```sql
CREATE TABLE IF NOT EXISTS results (
    run_name        TEXT    NOT NULL,
    task_id         TEXT    NOT NULL,
    mode            TEXT    NOT NULL,       -- sandbox_tools | direct
    endpoint_name   TEXT    NOT NULL,       -- model 从 endpoint.yaml 查
    status          TEXT    NOT NULL,       -- success | error_llm | error_extract | error_exec | wrong_answer
    raw_response    TEXT,                   -- LLM 完整文本输出
    extracted_code  TEXT,                   -- 提取出的 test_transform 代码
    test_passed     INTEGER DEFAULT 0,     -- 通过的 test case 数
    test_total      INTEGER DEFAULT 0,     -- 总 test case 数
    correct         INTEGER DEFAULT 0,     -- 1 = 全部通过, 0 = 否
    token_usage     TEXT,                   -- JSON: {"input": x, "output": x, "reasoning": x, "cached": x}
    tool_rounds     INTEGER DEFAULT 0,     -- 实际 tool call 轮数
    duration_s      REAL,                  -- 总耗时（秒）
    error_message   TEXT,                  -- 错误信息（status != success 时）
    created_at      TEXT    DEFAULT (datetime('now')),
    PRIMARY KEY (run_name, task_id)
);
```

#### status 含义

| status | 说明 |
|--------|------|
| `success` | 提取代码成功 + 所有 test case 通过 |
| `wrong_answer` | 提取代码成功 + 执行成功 + 但答案不对 |
| `error_llm` | LLM 调用失败（超时/网络/超过最大轮数） |
| `error_extract` | LLM 返回了内容，但无法提取出 `test_transform` 函数 |
| `error_exec` | 代码提取成功，但执行时报错 |

---

### ResultDB 接口

```python
class ResultDB:
    def __init__(self, db_path: Path):
        """打开或创建 SQLite 数据库，自动建表"""

    def save_result(self, result: dict):
        """INSERT OR REPLACE 一条结果记录"""

    def get_completed_task_ids(self, run_name: str) -> set[str]:
        """返回该 run 下已完成的 task_id 集合（用于 resume 去重）"""

    def get_run_summary(self, run_name: str) -> dict:
        """返回该 run 的汇总统计：
        {
            "total": int,
            "correct": int,
            "accuracy": float,
            "by_status": {"success": n, "wrong_answer": n, ...},
            "avg_duration_s": float,
            "total_tokens": {"input": n, "output": n, "reasoning": n, "cached": n},
        }
        """
```

---

### 记录时机

在 `evaluate_single_task()` 中，无论成功或失败，都调用 `db.save_result()` 记录结果。这样 resume 时能正确跳过已完成（包括已失败）的 task。
