"""MCTS-style tree search over solution attempts for ARC tasks."""

import json
import math
from dataclasses import dataclass, field

from arc.eval.llm import LLMResult, call_llm, execute_python
from arc.eval.prompt import build_messages, build_refinement_message
from arc.eval.test import compare_grids


@dataclass
class TreeNode:
    id: int
    parent: "TreeNode | None"
    children: list["TreeNode"] = field(default_factory=list)
    code: str | None = None
    score: float = 0.0
    value: float = 0.0
    visit_count: int = 0
    llm_result: LLMResult | None = None
    depth: int = 0
    terminal: bool = False
    train_details: list[dict] | None = None


def score_on_training(
    code: str | None, train_examples: list[dict], python_path: str,
) -> tuple[float, list[dict]]:
    """Score code against training examples.

    Returns (score, details) where score is mean cell_accuracy in [0, 1].
    """
    if code is None:
        return 0.0, [{"correct": False, "cell_accuracy": 0.0, "error": "no code"}]

    script = code + "\n\nimport json\n"
    for ex in train_examples:
        script += f"print(json.dumps(test_transform({ex['input']})))\n"

    result = execute_python(script, python_path)
    total = len(train_examples)

    if result["exit_code"] != 0:
        return 0.0, [{"correct": False, "cell_accuracy": 0.0,
                       "error": result["stderr"]}] * total

    lines = result["stdout"].strip().splitlines()
    if len(lines) != total:
        return 0.0, [{"correct": False, "cell_accuracy": 0.0,
                       "error": f"Expected {total} outputs, got {len(lines)}"}] * total

    details = []
    total_acc = 0.0
    for line, ex in zip(lines, train_examples):
        try:
            predicted = json.loads(line)
        except json.JSONDecodeError as e:
            details.append({"correct": False, "cell_accuracy": 0.0, "error": str(e)})
            continue
        cmp = compare_grids(predicted, ex["output"])
        import numpy as np
        pred_shape = tuple(np.array(predicted).shape) if predicted else (0,)
        exp_shape = tuple(np.array(ex["output"]).shape) if ex["output"] else (0,)
        details.append({
            **cmp, "error": None,
            "predicted_shape": pred_shape,
            "expected_shape": exp_shape,
        })
        total_acc += cmp["cell_accuracy"]

    score = total_acc / total if total > 0 else 0.0
    return score, details


def _puct_score(child: TreeNode, parent_visits: int, c_puct: float) -> float:
    """PUCT score: Q + exploration term."""
    if parent_visits <= 0:
        return float("inf")
    exploration = c_puct * math.sqrt(math.log(parent_visits)) / (1 + child.visit_count)
    return child.value + exploration


def _select(root: TreeNode, min_children: int, max_depth: int, c_puct: float) -> TreeNode:
    """Traverse tree from root to an expandable node using PUCT."""
    # Force breadth first: ensure minimum fresh attempts
    if len(root.children) < min_children:
        return root

    node = root
    while True:
        # Filter to non-terminal children that can still be expanded
        expandable = [c for c in node.children if not c.terminal]
        if not expandable:
            return node  # all children terminal, expand from this node

        # Pick best child by PUCT
        best = max(expandable, key=lambda c: _puct_score(c, node.visit_count, c_puct))

        # If best child is a leaf (no children) or at max depth, return it
        if not best.children or best.depth >= max_depth:
            return best

        node = best


def _collect_scores(node: TreeNode) -> list[float]:
    """Collect scores from all scored descendants (excluding root-like nodes with no code)."""
    scores = []
    if node.code is not None:
        scores.append(node.score)
    for child in node.children:
        scores.extend(_collect_scores(child))
    return scores


def _backpropagate(node: TreeNode):
    """Update visit counts and values from node up to root."""
    current = node
    while current is not None:
        current.visit_count += 1
        scores = _collect_scores(current)
        current.value = sum(scores) / len(scores) if scores else 0.0
        current = current.parent


class TreeSearch:
    """MCTS-style tree search over solution attempts."""

    def __init__(self, task_id: str, task_data: dict, client, cfg: dict, log_db=None):
        self.task_id = task_id
        self.task_data = task_data
        self.client = client
        self.cfg = cfg
        self.log_db = log_db

        ts_cfg = cfg["eval"]["tree_search"]
        self.max_nodes = ts_cfg["max_nodes"]
        self.max_depth = ts_cfg["max_depth"]
        self.min_children = ts_cfg["min_children"]
        self.c_puct = ts_cfg["exploration_weight"]
        self.early_stop = ts_cfg["early_stop"]
        self.node_max_output_tokens = ts_cfg.get("max_output_tokens", 8192)
        self.node_max_tool_rounds = ts_cfg.get("max_tool_rounds", 6)
        self.node_token_budget = ts_cfg.get("token_budget", 60000)

        self._next_id = 0
        self.root = self._make_node(parent=None, depth=0)
        self.all_nodes: list[TreeNode] = [self.root]

    def _make_node(self, parent: TreeNode | None, depth: int) -> TreeNode:
        node = TreeNode(id=self._next_id, parent=parent, depth=depth)
        self._next_id += 1
        return node

    def run(self) -> str | None:
        """Run tree search. Returns best code or None."""
        print(f"[{self.task_id}] Tree search: max_nodes={self.max_nodes}, "
              f"max_depth={self.max_depth}, min_children={self.min_children}")

        for i in range(self.max_nodes):
            # 1. SELECT
            leaf = _select(self.root, self.min_children, self.max_depth, self.c_puct)
            print(f"\n[{self.task_id}] === Iteration {i+1}/{self.max_nodes} ===")
            print(f"[{self.task_id}] Selected node {leaf.id} "
                  f"(depth={leaf.depth}, score={leaf.score:.2f}, visits={leaf.visit_count})")

            # 2. EXPAND
            if leaf is self.root:
                child = self._expand_fresh()
            else:
                child = self._expand_refine(leaf)
            leaf.children.append(child)
            self.all_nodes.append(child)

            # 3. EVALUATE
            print(f"[{self.task_id}] Scoring node {child.id} on training examples...")
            child.score, child.train_details = score_on_training(
                child.code, self.task_data["train"], self.cfg["python_path"],
            )

            # Pruning
            if child.score == 0.0:
                child.terminal = True
            if child.depth >= self.max_depth:
                child.terminal = True
            if (child.code and leaf.code
                    and child.code.strip() == leaf.code.strip()):
                child.terminal = True

            print(f"[{self.task_id}] Node {child.id}: score={child.score:.2f}, "
                  f"depth={child.depth}, terminal={child.terminal}")

            # 4. BACKPROPAGATE
            _backpropagate(child)

            # 5. Print tree state
            self._print_tree_state()

            # 6. EARLY STOP
            if self.early_stop and child.score == 1.0:
                print(f"[{self.task_id}] Early stop: perfect training score at node {child.id}")
                return child.code

        best = self._best_node()
        if best:
            print(f"[{self.task_id}] Tree search complete: best node {best.id}, "
                  f"score={best.score:.2f}")
            return best.code
        print(f"[{self.task_id}] Tree search complete: no valid code found")
        return None

    def _expand_fresh(self) -> TreeNode:
        """Create a fresh solution attempt from root."""
        child = self._make_node(parent=self.root, depth=1)
        print(f"[{self.task_id}] Expanding fresh attempt -> node {child.id}")

        messages = build_messages(
            self.task_data["train"],
            [tc["input"] for tc in self.task_data["test"]],
        )

        # Use sandbox_tools mode for the inner call
        node_cfg = {**self.cfg, "eval": {**self.cfg["eval"], "mode": "sandbox_tools"}}
        node_task_id = f"{self.task_id}_n{child.id}"

        child.llm_result = call_llm(
            self.client, node_cfg, messages, node_task_id, self.log_db,
            max_tool_rounds=self.node_max_tool_rounds,
            max_output_tokens=self.node_max_output_tokens,
            token_budget=self.node_token_budget,
        )
        child.code = child.llm_result.extracted_code
        return child

    def _expand_refine(self, parent: TreeNode) -> TreeNode:
        """Create a refinement attempt from a scored node."""
        child = self._make_node(parent=parent, depth=parent.depth + 1)
        print(f"[{self.task_id}] Refining node {parent.id} -> node {child.id}")

        messages = build_messages(
            self.task_data["train"],
            [tc["input"] for tc in self.task_data["test"]],
        )

        # Add refinement context
        if parent.code and parent.train_details:
            refinement_msg = build_refinement_message(
                parent.code, parent.score,
                parent.train_details, self.task_data["train"],
            )
            messages.append(refinement_msg)

        node_cfg = {**self.cfg, "eval": {**self.cfg["eval"], "mode": "sandbox_tools"}}
        node_task_id = f"{self.task_id}_n{child.id}"

        child.llm_result = call_llm(
            self.client, node_cfg, messages, node_task_id, self.log_db,
            max_tool_rounds=self.node_max_tool_rounds,
            max_output_tokens=self.node_max_output_tokens,
            token_budget=self.node_token_budget,
        )
        child.code = child.llm_result.extracted_code
        return child

    def _best_node(self) -> TreeNode | None:
        """Return the node with highest score across the tree."""
        scored = [n for n in self.all_nodes if n.code is not None]
        if not scored:
            return None
        return max(scored, key=lambda n: n.score)

    def _print_tree_state(self):
        """Print current tree state for debugging."""
        print(f"[{self.task_id}] Tree state:")
        for node in self.all_nodes:
            if node is self.root:
                print(f"  Root (id=0): {len(node.children)} children, "
                      f"value={node.value:.2f}, visits={node.visit_count}")
            else:
                parent_id = node.parent.id if node.parent else "-"
                print(f"  Node {node.id}: parent={parent_id}, depth={node.depth}, "
                      f"score={node.score:.2f}, value={node.value:.2f}, "
                      f"visits={node.visit_count}, terminal={node.terminal}")

    def build_result(self) -> dict:
        """Build aggregated result for DB storage."""
        total_usage = {"input": 0, "output": 0, "reasoning": 0, "cached": 0}
        total_tool_rounds = 0
        all_raw_responses = []

        for node in self.all_nodes:
            if node.llm_result:
                for k in total_usage:
                    total_usage[k] += node.llm_result.usage.get(k, 0)
                total_tool_rounds += node.llm_result.tool_rounds
                all_raw_responses.extend(node.llm_result.raw_responses)

        return {
            "token_usage": total_usage,
            "tool_rounds": total_tool_rounds,
            "raw_responses": all_raw_responses,
        }

    def build_log_text(self) -> str:
        """Concatenate all node transcripts with headers."""
        parts = []
        for node in self.all_nodes:
            if node.llm_result:
                parts.append(
                    f"=== Node {node.id} (depth={node.depth}, "
                    f"score={node.score:.2f}) ===\n{node.llm_result.text}"
                )
        return "\n\n".join(parts)
