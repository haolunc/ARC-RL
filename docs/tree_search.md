# Tree Search Strategy for ARC

Design document for solution-level tree search, adapted from [Brenner et al. 2026](https://arxiv.org/abs/2603.04735) ("Solving an Open Problem in Theoretical Physics using AI-Assisted Discovery").

## Background: Tree Search in the Paper

The paper combines Gemini Deep Think with a **Tree Search (TS)** framework to solve an open problem in theoretical physics. Key elements:

- **State Space**: Each node represents a proposed candidate solution (a mathematical expression + executable Python code).
- **Scoring**: Automated numerical verification — run the code, compare against high-precision numerical ground truth. Prune nodes with algebraic errors or numerical divergence.
- **Exploration**: PUCT (Predictor + Upper Confidence bound for Trees) balances exploitation of promising solutions with exploration of novel strategies. ~600 nodes explored, ~80% pruned by the automated verifier.
- **Negative Prompting**: Once valid solutions are found, inject constraints ("Do NOT use this method") to force the model to discover alternative approaches.
- **Intermittent Feedback**: When a node's code fails verification, the error and traceback are fed back to the model, allowing it to self-correct.

## Adaptation for ARC

### What Changes

| Paper (Physics) | ARC Adaptation |
|---|---|
| Node = mathematical expression + Python function | Node = `test_transform` function |
| Score = agreement with numerical integral | Score = cell accuracy on training examples |
| Negative prompting for method diversity | Refinement prompting with failure feedback |
| Single problem, many methods | Many tasks, tree search per task |

### What Stays the Same

- PUCT-based selection policy
- Automated scoring/pruning via code execution
- Solution-level nodes (each node = a complete attempt)
- Iterative refinement: parent solution informs child attempts

## Algorithm

### Data Structures

```
TreeNode:
    id: int
    parent: TreeNode | None
    children: list[TreeNode]
    code: str | None            # extracted test_transform
    score: float                # training accuracy [0.0, 1.0]
    value: float                # average score in subtree (for PUCT)
    visit_count: int            # times selected for expansion
    llm_result: LLMResult | None
    depth: int                  # 0 = root, 1 = fresh attempt, 2+ = refinement
```

### Main Loop

```
function tree_search(task) -> code:
    root = TreeNode(depth=0)

    for i in 1..max_nodes:
        # 1. SELECT — traverse from root to a leaf using PUCT
        leaf = select(root)

        # 2. EXPAND — generate a new solution from the leaf
        if leaf is root:
            child = fresh_attempt(task)       # new sandbox_tools conversation
        else:
            child = refine(task, leaf)         # refinement with failure feedback
        leaf.children.append(child)

        # 3. EVALUATE — score on training examples
        child.score = score_on_training(child.code, task["train"])

        # 4. BACKPROPAGATE — update values up to root
        backpropagate(child)

        # 5. EARLY STOP — perfect training score
        if child.score == 1.0:
            return child.code

    # Return best-scoring node
    return best_node(root).code
```

### Selection: PUCT

Traverse the tree from root to a leaf by repeatedly choosing the child with highest PUCT score:

```
PUCT(child) = Q(child) + c_puct * sqrt(ln(N(parent))) / (1 + N(child))
```

Where:
- **Q(child)** = `child.value` = mean score across child's subtree
- **N(parent)** = `parent.visit_count`
- **N(child)** = `child.visit_count`
- **c_puct** = exploration constant (default: 1.4)

At the root node, if fewer than `min_children` children exist, always expand (don't select among existing children). This ensures a minimum breadth of independent attempts before refinement begins.

If a node has no children, it is a leaf — expand it. If a node has reached `max_depth`, treat it as terminal and select a different path.

### Expansion

#### Fresh Attempt (depth 0 -> 1)

A standard `sandbox_tools` conversation:
- Build messages with `build_messages(train, test_inputs)`
- Call `call_llm()` in `sandbox_tools` mode
- Extract code from the result

To promote diversity across fresh attempts:
- Use temperature = 0.7 (existing default) — stochastic sampling naturally produces different approaches
- Optionally prepend a diversity hint to the user message (e.g., "Try approaching this by focusing on [colors/shapes/symmetry/positions]")

#### Refinement (depth 1+ -> 2+)

When refining a parent node that scored < 1.0:
1. Include the parent's extracted code in the prompt
2. Include specific training failures: which examples failed, predicted vs expected output (or shape mismatch)
3. Ask the LLM to analyze the failures and produce a corrected `test_transform`

Refinement prompt structure:
```
Your previous solution scored {score:.0%} on training examples.

Here is your previous code:
```python
{parent_code}
```

Failures:
- Example {i}: predicted shape {pred_shape} vs expected {exp_shape}
- Example {j}: cell accuracy {acc:.0%} (predicted differs at rows ...)

Analyze what went wrong and write a corrected test_transform function.
```

This is run as a fresh `sandbox_tools` conversation (the LLM gets the original task + refinement context).

### Evaluation

Score a node's extracted code against **all training examples**:

```
function score_on_training(code, train_examples) -> float:
    if code is None:
        return 0.0

    # Build test script: run test_transform on each training input
    script = code + "\nimport json\n"
    for ex in train_examples:
        script += f"print(json.dumps(test_transform({ex['input']})))\n"

    result = execute_python(script, python_path)
    if result.exit_code != 0:
        return 0.0

    # Compare each output line to expected
    total_accuracy = 0.0
    for line, ex in zip(result.stdout.lines, train_examples):
        predicted = json.loads(line)
        cmp = compare_grids(predicted, ex["output"])
        total_accuracy += cmp["cell_accuracy"]

    return total_accuracy / len(train_examples)
```

This reuses the existing `execute_python()` and `compare_grids()` functions.

### Backpropagation

After evaluating a new node:

```
function backpropagate(node):
    current = node
    while current is not None:
        current.visit_count += 1
        current.value = mean(child.score for child in all_descendants(current) if child.score is not None)
        current = current.parent
```

### Pruning Rules

- **Score = 0.0**: Node's code either wasn't extracted, failed to execute, or produced completely wrong outputs. Don't expand further (terminal).
- **Max depth reached**: Don't expand beyond `max_depth` levels of refinement.
- **Duplicate code**: If a child's code is identical to its parent's, mark as terminal (refinement didn't change anything).

## Integration with Existing Codebase

### Reused Components

| Component | Used For |
|---|---|
| `build_messages()` | Constructing initial prompts |
| `call_llm()` (sandbox_tools) | Generating each solution attempt |
| `execute_python()` | Running code for scoring |
| `compare_grids()` | Comparing predicted vs expected grids |
| `ResultDB` / `LogDB` | Storing final results and transcripts |
| `extract_code()` | Extracting test_transform from LLM output |

### New Components

| Component | Purpose |
|---|---|
| `TreeNode` | Tree node data structure |
| `TreeSearch` | Orchestrator: select, expand, evaluate, backpropagate loop |
| `score_on_training()` | Evaluate code against training examples |
| `build_refinement_messages()` | Construct refinement prompts with failure details |
| `select_puct()` | PUCT-based tree traversal |

### New File Structure

```
arc/eval/
├── tree.py             # TreeNode, TreeSearch, PUCT selection, scoring
├── llm.py              # (existing) — reused for solution generation
├── prompt.py           # (extended) — add refinement prompt builder
├── test.py             # (existing) — reused for compare_grids
├── run.py              # (extended) — add tree_search mode dispatch
├── config.py           # (extended) — add tree_search config validation
└── db.py               # (existing) — reused for persistence
```

## Configuration

```yaml
eval:
  mode: "tree_search"
  max_workers: 4          # parallel tasks (each task gets its own tree)
  tree_search:
    max_nodes: 16          # max solution attempts per task
    max_depth: 3           # max refinement depth (root=0, fresh=1, refine=2+)
    min_children: 3        # min fresh attempts before refinement starts
    exploration_weight: 1.4  # c_puct for PUCT formula
    early_stop: true       # stop search when training score = 1.0
```

### Parameter Guidance

- **max_nodes**: Total API calls per task. Higher = better coverage but more expensive. 8-32 is a reasonable range.
- **max_depth**: How many refinement rounds are allowed. 2-3 is usually sufficient; deeper refinement rarely helps.
- **min_children**: Ensures breadth before depth. Set to 2-4 for diverse initial exploration.
- **exploration_weight**: Higher values favor exploration of less-visited nodes. 1.0-2.0 is typical for PUCT.
- **early_stop**: Almost always `true` — if we score perfectly on training, there's no reason to keep searching.

## Example Walkthrough

Given a task with 3 training examples:

```
Iteration 1: Fresh attempt → score 0.4 (2/3 training examples partially correct)
Iteration 2: Fresh attempt → score 0.0 (code failed to execute)
Iteration 3: Fresh attempt → score 0.7 (all 3 partially correct)
Iteration 4: PUCT selects node with score 0.7 for refinement
             → Refinement: "Your solution scored 70%. Example 2 has wrong shape..."
             → score 0.9
Iteration 5: PUCT selects refinement (0.9) for further refinement
             → Refinement: "Almost there. Example 3 has 2 cells wrong at..."
             → score 1.0 → EARLY STOP
```

Total: 5 API calls instead of the single shot we do today. The tree explored 3 independent approaches, then refined the most promising one twice.

## Result Storage

The tree search result is stored the same way as existing modes — the winning node's code goes into `results.db`. Additionally:

- `tool_rounds` = total tool rounds across all nodes in the tree
- `token_usage` = sum of all token usage across the tree
- The log in `logs.db` contains all node transcripts, annotated with node IDs and scores

## Trade-offs

### Advantages over Single-Shot
- **Diversity**: Multiple independent attempts explore different strategies
- **Iterative refinement**: Targeted fixes for near-correct solutions
- **Automated pruning**: Bad solutions are abandoned early
- **Better use of compute**: Effort is concentrated on promising approaches

### Costs
- **More API calls**: `max_nodes` calls per task instead of 1
- **Higher latency**: Sequential within each task (though tasks are still parallel)
- **More tokens**: Each refinement includes the parent's code + failure details
- **Diminishing returns**: After ~8-16 nodes, improvements become rare for most tasks
