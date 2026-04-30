
### Test — 代码提取、执行、比较

---

### Code Extraction

从 LLM 输出中提取 `test_transform` 函数：

```python
def extract_code(text: str) -> str | None:
    """从 LLM 文本输出中提取 test_transform 函数代码。

    策略：
    1. 找所有 ```python ... ``` 代码块
    2. 优先取包含 `def test_transform` 的最后一个代码块
    3. 如果没有代码块包含 test_transform，返回 None

    返回 None 时，status 应标记为 error_extract。
    """
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if not matches:
        return None

    # 倒序查找包含 test_transform 的代码块
    for code in reversed(matches):
        if "def test_transform" in code:
            return code.strip()

    return None
```

---

### Grid Comparison

```python
def compare_grids(predicted: list[list[int]], expected: list[list[int]]) -> dict:
    """比较两个 grid，返回 {"correct": bool, "cell_accuracy": float}。

    逻辑：
    1. shape 不匹配 → correct=False, cell_accuracy=0.0
    2. shape 匹配 → 逐 cell 比较，cell_accuracy = 正确 cell 数 / 总 cell 数
    3. correct = (cell_accuracy == 1.0)
    """
```

---

### Run Tests

对每个 test case 执行 `test_transform` 并比较结果：

```python
def run_tests(
    code: str,
    test_cases: list[dict],     # [{"input": grid, "output": grid}, ...]
    python_path: str,
) -> dict:
    """执行提取的代码并验证所有 test case。

    返回:
    {
        "passed": int,          # 通过的 test case 数
        "total": int,           # 总 test case 数
        "correct": bool,        # 全部通过
        "details": [            # 每个 test case 的详细结果
            {"correct": bool, "cell_accuracy": float, "error": str | None},
            ...
        ],
        "status": str,          # "success" | "wrong_answer" | "error_exec"
    }
    """
```

实现思路：
1. 构造执行脚本：把 `code`（包含 `def test_transform`）+ 调用代码拼成一个临时 .py 文件
2. 对每个 test case，在脚本末尾添加 `print(json.dumps(test_transform(input_grid)))`
3. 调用 `execute_python()` 执行
4. 解析 stdout（JSON 格式的 grid），与 expected output 调用 `compare_grids()` 比较

```python
# 构造执行脚本示例
script = code + "\n\nimport json\n"
for i, tc in enumerate(test_cases):
    script += f"print(json.dumps(test_transform({tc['input']})))\n"
```

---

### 错误分类

| 情况 | status | 说明 |
|------|--------|------|
| `extract_code()` 返回 None | `error_extract` | LLM 没有输出有效的 test_transform |
| `execute_python()` 返回非零 exit_code | `error_exec` | 代码执行报错（语法错误、runtime error、超时） |
| stdout 无法解析为 grid | `error_exec` | 输出格式不对 |
| grid 比较不通过 | `wrong_answer` | 代码执行成功但答案错误 |
| 全部 test case 通过 | `success` | |
