"""
Evaluation script for the trained ARC role-induction model.

Runs inference on evaluation tasks, computes exact-match accuracy
and cell-level accuracy, optionally visualises slot masks and roles.

Usage:
  python -m role_induction.evaluate --checkpoint checkpoints/best.pt
  python -m role_induction.evaluate --checkpoint checkpoints/best.pt --dataset evaluation --num-tasks 50
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from .models import ARCModel
from .dataset import EpisodicDataset, episodic_collate_fn


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@torch.no_grad()
def evaluate(
    model: ARCModel,
    data_dir: str,
    device: torch.device,
    num_tasks: int | None = None,
    temperature: float = 0.1,
) -> dict:
    model.eval()
    model = model.to(device)

    dataset = EpisodicDataset(data_dir)
    if num_tasks:
        dataset.tasks = dataset.tasks[:num_tasks]

    loader = DataLoader(dataset, batch_size=1, shuffle=False,
                        num_workers=0, collate_fn=episodic_collate_fn)

    results = []
    correct_count = 0
    total_cells = 0
    correct_cells = 0

    for batch in loader:
        task_id = batch["task_ids"][0]
        n_sup = batch["n_support"][0].item()

        support_inputs = [batch["support_inputs"][:, i].to(device) for i in range(n_sup)]
        support_outputs = [batch["support_outputs"][:, i].to(device) for i in range(n_sup)]
        query_input = batch["query_input"].to(device)
        query_output = batch["query_output"].to(device)

        qh = batch["query_h_out"][0].item()
        qw = batch["query_w_out"][0].item()

        output = model.forward_task(
            support_inputs, support_outputs, query_input,
            (qh, qw), temperature=temperature,
        )

        pred = output["pred_logits"][0, :qh, :qw, :].argmax(dim=-1)  # (H, W)
        target = query_output[0, :qh, :qw]

        cell_correct = (pred == target).sum().item()
        cell_total = qh * qw
        exact_match = (cell_correct == cell_total)

        total_cells += cell_total
        correct_cells += cell_correct
        if exact_match:
            correct_count += 1

        n_roles_used = 0
        if output.get("all_in_roles"):
            role_probs = output["all_in_roles"][0][0]  # (K, R)
            assigned = role_probs.argmax(dim=-1)
            n_roles_used = len(assigned.unique())

        result = {
            "task_id": task_id,
            "correct": exact_match,
            "cell_accuracy": round(cell_correct / cell_total, 4),
            "n_roles_used": n_roles_used,
            "predicted": pred.cpu().tolist(),
            "expected": target.cpu().tolist(),
        }
        results.append(result)

        status = "✓" if exact_match else "✗"
        print(f"  {status} {task_id} (cell_acc={cell_correct}/{cell_total}={cell_correct/cell_total:.1%}, roles={n_roles_used})")

    task_acc = correct_count / len(results) if results else 0
    cell_acc = correct_cells / total_cells if total_cells else 0

    summary = {
        "method": "role_induction_neural",
        "total_tasks": len(results),
        "correct_tasks": correct_count,
        "task_accuracy": round(task_acc, 4),
        "cell_accuracy": round(cell_acc, 4),
        "results": results,
    }

    print("-" * 60)
    print(f"Task accuracy: {correct_count}/{len(results)} = {task_acc:.2%}")
    print(f"Cell accuracy: {correct_cells}/{total_cells} = {cell_acc:.2%}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="ARC Role-Induction Evaluation")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--dataset", choices=["training", "evaluation"], default="evaluation")
    parser.add_argument("--version", choices=["ARC-AGI", "ARC-AGI-2"], default="ARC-AGI")
    parser.add_argument("--num-tasks", type=int, default=None)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--n-slots", type=int, default=8)
    parser.add_argument("--n-roles", type=int, default=16)
    args = parser.parse_args()

    device = get_device()
    print(f"Device: {device}")

    data_dir = args.data_dir or str(
        Path(__file__).parent.parent / args.version / "data" / args.dataset
    )

    model = ARCModel(d_model=args.d_model, n_slots=args.n_slots, n_roles=args.n_roles)
    state = torch.load(args.checkpoint, map_location=device, weights_only=True)
    model.load_state_dict(state)
    print(f"Loaded checkpoint: {args.checkpoint}")

    summary = evaluate(model, data_dir, device, args.num_tasks)

    output_path = args.output or f"results_neural_{args.version}_{args.dataset}.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
