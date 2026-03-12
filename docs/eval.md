# ARC-AGI LLM 评估流水线

## 概述

`arc/eval` 是一个基于大语言模型（LLM）的 ARC-AGI 任务评估流水线。核心目标：

- 给 LLM 展示 ARC 任务的训练样例（输入/输出网格对）
- 要求 LLM 编写 `transform(input_grid)` 函数来实现变换规则
- 在训练样例上验证代码正确性，通过后在测试样例上评估
- 所有结果持久化到 SQLite 数据库，已完成的任务自动跳过

流水线支持两种评估模式：

| 模式 | 配置值 | 说明 |
|------|--------|------|
| **简单模式** (Simple) | `mode: "simple"` | 经典重试循环：提取代码 → 执行 → 反馈 → 重试 |
| **智能体模式** (Agentic) | `mode: "agentic"` | 工具调用循环：LLM 通过工具主动探索、测试、提交 |

## 模块架构

```
arc/eval/
├── config.py       # 配置加载（统一 YAML 配置文件）
├── prompt.py       # Prompt 构建（简单模式 + 智能体模式）
├── llm_client.py   # OpenAI SDK 调用封装（文本模式 + 工具调用模式）
├── code_extract.py # 从 LLM 响应中提取 Python 代码 + thinking 内容
├── safe_exec.py    # 子进程沙盒执行（transform 执行 + 分析代码执行）
├── evaluate.py     # 网格比较和训练集验证
├── tools.py        # 工具定义和调度器（智能体模式专用）
├── db.py           # SQLite 结果记录（tasks/llm_calls/tool_calls 三表）
└── run.py          # CLI 入口和主评估循环（简单 + 智能体）
```

| 模块 | 职责 |
|------|------|
| `config` | 加载统一 YAML 配置文件，验证 `mode` 字段，设置默认值 |
| `prompt` | 构造聊天消息。简单模式：`SYSTEM_PROMPT` + 训练样例 + 重试追加。智能体模式：`AGENTIC_SYSTEM_PROMPT`（描述 3 个工具 + 推荐工作流）|
| `llm_client` | `call_llm()` 和 `call_llm_with_tools()` 均返回 `LLMResponse` 数据类（含 content、tool_calls、token 用量、耗时、finish_reason 等元数据）。两者共享重试逻辑 |
| `code_extract` | `extract_code()` 从响应中提取代码块。`extract_thinking()` 提取 `<think>` 标签内容用于日志记录 |
| `safe_exec` | `execute_transform()` 执行 `def transform` 函数。`execute_analysis()` 执行任意分析代码（预注入网格变量）|
| `evaluate` | `compare_grids` 逐像素比较网格，`verify_on_train` 在所有训练样例上验证代码 |
| `tools` | `TOOL_DEFINITIONS` 定义 3 个 OpenAI 格式工具。`execute_tool()` 调度并执行工具调用 |
| `db` | SQLite 写入层，三表结构：`tasks`（任务级结果）、`llm_calls`（每次 LLM 调用详情）、`tool_calls`（工具执行记录）|
| `run` | CLI 解析、任务加载、根据 `mode` 路由到 `evaluate_task()` 或 `evaluate_task_agentic()`、结果汇总 |

## 详细文档

- [**评估模式**](eval/modes.md) — 简单模式、智能体模式（工具定义、评估循环、反馈机制）、Thinking 提取、模式对比
- [**数据库**](eval/database.md) — 三表 Schema（tasks / llm_calls / tool_calls）、设计理由、查询示例
- [**LLM 客户端与代码执行**](eval/llm-client.md) — LLMResponse 数据类、API 调用封装、代码执行沙盒
- [**配置系统与数据流**](eval/config.md) — YAML 配置结构、API 密钥管理、断点续跑、CLI 输出示例
