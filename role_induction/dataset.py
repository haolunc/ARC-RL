"""
PyTorch Dataset for ARC tasks.

Supports two modes:
  1. GridDataset       — individual grids for Stage A (reconstruction pretraining)
  2. EpisodicDataset   — full task episodes for Stage B/C (role induction + end-to-end)
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import torch
from torch.utils.data import Dataset


def load_tasks(data_dir: str | Path) -> dict[str, dict]:
    """Load all ARC task JSON files from a directory."""
    data_dir = Path(data_dir)
    tasks = {}
    for f in sorted(data_dir.glob("*.json")):
        with open(f) as fp:
            tasks[f.stem] = json.load(fp)
    return tasks


def grid_to_tensor(grid: list[list[int]]) -> torch.Tensor:
    """Convert a grid (list of lists) to a LongTensor."""
    return torch.tensor(grid, dtype=torch.long)


def pad_grid(grid: torch.Tensor, max_h: int = 30, max_w: int = 30,
             pad_value: int = 0) -> torch.Tensor:
    """Pad a (H, W) grid to (max_h, max_w)."""
    H, W = grid.shape
    padded = torch.full((max_h, max_w), pad_value, dtype=grid.dtype)
    padded[:H, :W] = grid
    return padded


class GridDataset(Dataset):
    """
    Stage A dataset: each sample is a single grid for self-reconstruction.
    Extracts all grids (both inputs and outputs) from all tasks.
    """

    def __init__(self, data_dir: str | Path, max_h: int = 30, max_w: int = 30,
                 include_test: bool = False):
        super().__init__()
        self.max_h = max_h
        self.max_w = max_w
        self.grids: list[tuple[list[list[int]], int, int]] = []  # (grid, H, W)

        tasks = load_tasks(data_dir)
        for task in tasks.values():
            for pair in task["train"]:
                self._add(pair["input"])
                self._add(pair["output"])
            if include_test:
                for pair in task["test"]:
                    self._add(pair["input"])
                    if "output" in pair:
                        self._add(pair["output"])

    def _add(self, grid: list[list[int]]):
        h, w = len(grid), len(grid[0])
        if h <= self.max_h and w <= self.max_w:
            self.grids.append((grid, h, w))

    def __len__(self) -> int:
        return len(self.grids)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        grid, h, w = self.grids[idx]
        tensor = grid_to_tensor(grid)
        padded = pad_grid(tensor, self.max_h, self.max_w)
        return {
            "grid": padded,       # (max_h, max_w)
            "height": h,
            "width": w,
            "mask": self._spatial_mask(h, w),  # (max_h, max_w) bool
        }

    def _spatial_mask(self, h: int, w: int) -> torch.Tensor:
        mask = torch.zeros(self.max_h, self.max_w, dtype=torch.bool)
        mask[:h, :w] = True
        return mask


class EpisodicDataset(Dataset):
    """
    Stage B/C dataset: each sample is a full ARC task episode.
    Returns support pairs + query pair for meta-learning.
    """

    def __init__(self, data_dir: str | Path, max_h: int = 30, max_w: int = 30,
                 max_support: int = 4):
        super().__init__()
        self.max_h = max_h
        self.max_w = max_w
        self.max_support = max_support
        self.tasks: list[tuple[str, dict]] = []

        tasks = load_tasks(data_dir)
        for tid, task in tasks.items():
            if task.get("test") and task["test"][0].get("output"):
                self.tasks.append((tid, task))

    def __len__(self) -> int:
        return len(self.tasks)

    def __getitem__(self, idx: int) -> dict:
        tid, task = self.tasks[idx]

        train_pairs = task["train"][:self.max_support]
        test_pair = task["test"][0]

        support_inputs, support_outputs = [], []
        support_heights_in, support_widths_in = [], []
        support_heights_out, support_widths_out = [], []

        for pair in train_pairs:
            inp = grid_to_tensor(pair["input"])
            out = grid_to_tensor(pair["output"])
            h_i, w_i = inp.shape
            h_o, w_o = out.shape

            support_inputs.append(pad_grid(inp, self.max_h, self.max_w))
            support_outputs.append(pad_grid(out, self.max_h, self.max_w))
            support_heights_in.append(h_i)
            support_widths_in.append(w_i)
            support_heights_out.append(h_o)
            support_widths_out.append(w_o)

        query_inp = grid_to_tensor(test_pair["input"])
        query_out = grid_to_tensor(test_pair["output"])
        qh_i, qw_i = query_inp.shape
        qh_o, qw_o = query_out.shape

        return {
            "task_id": tid,
            "n_support": len(train_pairs),
            "support_inputs": torch.stack(support_inputs),    # (n, max_h, max_w)
            "support_outputs": torch.stack(support_outputs),
            "support_h_in": torch.tensor(support_heights_in),
            "support_w_in": torch.tensor(support_widths_in),
            "support_h_out": torch.tensor(support_heights_out),
            "support_w_out": torch.tensor(support_widths_out),
            "query_input": pad_grid(query_inp, self.max_h, self.max_w),
            "query_output": pad_grid(query_out, self.max_h, self.max_w),
            "query_h_in": qh_i,
            "query_w_in": qw_i,
            "query_h_out": qh_o,
            "query_w_out": qw_o,
        }


def episodic_collate_fn(batch: list[dict]) -> dict:
    """
    Custom collate for EpisodicDataset.
    Since tasks have different numbers of support pairs, we pad to max.
    """
    max_n = max(b["n_support"] for b in batch)
    B = len(batch)
    max_h = batch[0]["support_inputs"].shape[1]
    max_w = batch[0]["support_inputs"].shape[2]

    support_inputs = torch.zeros(B, max_n, max_h, max_w, dtype=torch.long)
    support_outputs = torch.zeros(B, max_n, max_h, max_w, dtype=torch.long)
    support_h_in = torch.zeros(B, max_n, dtype=torch.long)
    support_w_in = torch.zeros(B, max_n, dtype=torch.long)
    support_h_out = torch.zeros(B, max_n, dtype=torch.long)
    support_w_out = torch.zeros(B, max_n, dtype=torch.long)
    n_support = torch.zeros(B, dtype=torch.long)

    for i, b in enumerate(batch):
        n = b["n_support"]
        n_support[i] = n
        support_inputs[i, :n] = b["support_inputs"]
        support_outputs[i, :n] = b["support_outputs"]
        support_h_in[i, :n] = b["support_h_in"]
        support_w_in[i, :n] = b["support_w_in"]
        support_h_out[i, :n] = b["support_h_out"]
        support_w_out[i, :n] = b["support_w_out"]

    return {
        "task_ids": [b["task_id"] for b in batch],
        "n_support": n_support,
        "support_inputs": support_inputs,
        "support_outputs": support_outputs,
        "support_h_in": support_h_in,
        "support_w_in": support_w_in,
        "support_h_out": support_h_out,
        "support_w_out": support_w_out,
        "query_input": torch.stack([b["query_input"] for b in batch]),
        "query_output": torch.stack([b["query_output"] for b in batch]),
        "query_h_in": torch.tensor([b["query_h_in"] for b in batch]),
        "query_w_in": torch.tensor([b["query_w_in"] for b in batch]),
        "query_h_out": torch.tensor([b["query_h_out"] for b in batch]),
        "query_w_out": torch.tensor([b["query_w_out"] for b in batch]),
    }
