"""
Three-stage training pipeline for ARC role-induction model.

  Stage A  — Perception pretraining: grid self-reconstruction (encoder + slots + decoder)
  Stage B  — Role induction: freeze perception, train role network with contrastive loss
  Stage C  — End-to-end: fine-tune entire model on task prediction with MDL + verifier reward

Usage:
  python -m role_induction.train --stage A --epochs 100
  python -m role_induction.train --stage B --epochs 50 --checkpoint checkpoints/stage_a.pt
  python -m role_induction.train --stage C --epochs 50 --checkpoint checkpoints/stage_b.pt
  python -m role_induction.train --stage all --epochs-a 100 --epochs-b 50 --epochs-c 50
"""

from __future__ import annotations

import argparse
import functools
import json
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

print = functools.partial(print, flush=True)

from .models import ARCModel
from .dataset import GridDataset, EpisodicDataset, episodic_collate_fn
from .losses import ArcLoss, reconstruction_loss, mask_entropy_penalty, slot_diversity_loss


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ============================================================
# Stage A: Perception Pretraining (self-reconstruction)
# ============================================================

def train_stage_a(
    model: ARCModel,
    data_dir: str,
    epochs: int = 100,
    batch_size: int = 32,
    lr: float = 3e-4,
    device: torch.device = torch.device("cpu"),
    save_dir: str = "checkpoints",
) -> ARCModel:
    print("=" * 60)
    print("Stage A: Perception Pretraining (Grid Reconstruction)")
    print("=" * 60)

    dataset = GridDataset(data_dir)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    print(f"  Grids: {len(dataset)}, Batches: {len(loader)}")

    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        total_recon = 0.0
        n_batches = 0

        for batch in loader:
            grid = batch["grid"].to(device)       # (B, 30, 30)
            h_vals = batch["height"]
            w_vals = batch["width"]
            mask = batch["mask"].to(device)        # (B, 30, 30)

            recon_logits, masks, slots, attn = model.reconstruct(grid)

            loss_recon = reconstruction_loss(recon_logits, grid, mask)
            loss_ent = mask_entropy_penalty(masks)
            loss_div = slot_diversity_loss(slots)

            loss = loss_recon + 0.1 * loss_ent + 0.1 * loss_div

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            total_recon += loss_recon.item()
            n_batches += 1

        scheduler.step()
        avg_loss = total_loss / n_batches
        avg_recon = total_recon / n_batches

        log_every = max(1, epochs // 20)
        if epoch % log_every == 0 or epoch == 1 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs} | loss={avg_loss:.4f} | recon={avg_recon:.4f}")

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_path / "stage_a.pt")
    print(f"  Saved to {save_path / 'stage_a.pt'}")
    return model


# ============================================================
# Stage B: Role Induction Training
# ============================================================

def train_stage_b(
    model: ARCModel,
    data_dir: str,
    epochs: int = 50,
    batch_size: int = 4,
    lr: float = 1e-4,
    device: torch.device = torch.device("cpu"),
    save_dir: str = "checkpoints",
    temperature_start: float = 2.0,
    temperature_end: float = 0.5,
) -> ARCModel:
    print("=" * 60)
    print("Stage B: Role Induction Training")
    print("=" * 60)

    # freeze perception modules
    for param in model.encoder.parameters():
        param.requires_grad = False
    for param in model.slot_attn.parameters():
        param.requires_grad = False
    for param in model.recon_decoder.parameters():
        param.requires_grad = False

    dataset = EpisodicDataset(data_dir)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True,
                        num_workers=0, collate_fn=episodic_collate_fn)
    print(f"  Tasks: {len(dataset)}, Batches: {len(loader)}")

    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=lr, weight_decay=1e-4)
    loss_fn = ArcLoss()

    model = model.to(device)

    for epoch in range(1, epochs + 1):
        model.train()
        temp = temperature_start + (temperature_end - temperature_start) * (epoch / epochs)
        total_loss = 0.0
        n_batches = 0

        for batch in loader:
            B = batch["query_input"].shape[0]
            n_sup = batch["n_support"][0].item()

            support_inputs = [batch["support_inputs"][:, i].to(device) for i in range(n_sup)]
            support_outputs = [batch["support_outputs"][:, i].to(device) for i in range(n_sup)]
            query_input = batch["query_input"].to(device)
            query_output = batch["query_output"].to(device)

            qh = batch["query_h_out"][0].item()
            qw = batch["query_w_out"][0].item()

            output = model.forward_task(
                support_inputs, support_outputs, query_input,
                (qh, qw), temperature=temp,
            )

            losses = loss_fn(output, query_output, qh, qw, stage="role")

            optimizer.zero_grad()
            losses["total"].backward()
            nn.utils.clip_grad_norm_(trainable, 1.0)
            optimizer.step()

            total_loss += losses["total"].item()
            n_batches += 1

        avg_loss = total_loss / max(n_batches, 1)
        log_every = max(1, epochs // 10)
        if epoch % log_every == 0 or epoch == 1 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs} | loss={avg_loss:.4f} | temp={temp:.2f}")

    # unfreeze all
    for param in model.parameters():
        param.requires_grad = True

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_path / "stage_b.pt")
    print(f"  Saved to {save_path / 'stage_b.pt'}")
    return model


# ============================================================
# Stage C: End-to-End Fine-tuning
# ============================================================

def train_stage_c(
    model: ARCModel,
    data_dir: str,
    epochs: int = 50,
    batch_size: int = 2,
    lr: float = 5e-5,
    device: torch.device = torch.device("cpu"),
    save_dir: str = "checkpoints",
    temperature: float = 0.5,
) -> ARCModel:
    print("=" * 60)
    print("Stage C: End-to-End Fine-tuning (Task Prediction)")
    print("=" * 60)

    dataset = EpisodicDataset(data_dir)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True,
                        num_workers=0, collate_fn=episodic_collate_fn)
    print(f"  Tasks: {len(dataset)}, Batches: {len(loader)}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    loss_fn = ArcLoss(alpha_recon=0.5, alpha_role=0.5, alpha_task=2.0, alpha_mdl=0.01)

    model = model.to(device)

    best_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        total_task = 0.0
        correct = 0
        total = 0
        n_batches = 0

        for batch in loader:
            B = batch["query_input"].shape[0]
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

            losses = loss_fn(output, query_output, qh, qw, stage="full")

            optimizer.zero_grad()
            losses["total"].backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += losses["total"].item()
            total_task += losses.get("task", torch.tensor(0.0)).item()

            # compute cell accuracy
            pred = output["pred_logits"][:, :qh, :qw, :].argmax(dim=-1)
            target = query_output[:, :qh, :qw]
            correct += (pred == target).sum().item()
            total += B * qh * qw
            n_batches += 1

        scheduler.step()
        avg_loss = total_loss / max(n_batches, 1)
        avg_task = total_task / max(n_batches, 1)
        cell_acc = correct / max(total, 1)

        log_every = max(1, epochs // 10)
        if epoch % log_every == 0 or epoch == 1 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs} | loss={avg_loss:.4f} | "
                  f"task={avg_task:.4f} | cell_acc={cell_acc:.2%}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), save_path / "best.pt")

    save_path = Path(save_dir)
    torch.save(model.state_dict(), save_path / "stage_c.pt")
    print(f"  Saved to {save_path / 'stage_c.pt'}")
    print(f"  Best model saved to {save_path / 'best.pt'}")
    return model


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="ARC Role-Induction Training")
    parser.add_argument("--stage", choices=["A", "B", "C", "all"], default="all")
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Path to ARC data (default: ARC-AGI/data/training)")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to checkpoint to resume from")
    parser.add_argument("--save-dir", type=str, default="checkpoints")
    parser.add_argument("--epochs-a", type=int, default=100)
    parser.add_argument("--epochs-b", type=int, default=50)
    parser.add_argument("--epochs-c", type=int, default=50)
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override epochs for single-stage run")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--n-slots", type=int, default=8)
    parser.add_argument("--n-roles", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-4)
    args = parser.parse_args()

    device = get_device()
    print(f"Device: {device}")

    data_dir = args.data_dir or str(
        Path(__file__).parent.parent / "ARC-AGI" / "data" / "training"
    )
    save_dir = str(Path(__file__).parent.parent / args.save_dir)

    model = ARCModel(
        d_model=args.d_model,
        n_slots=args.n_slots,
        n_roles=args.n_roles,
    )

    if args.checkpoint:
        print(f"Loading checkpoint: {args.checkpoint}")
        state = torch.load(args.checkpoint, map_location=device, weights_only=True)
        model.load_state_dict(state)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model params: {total_params:,} total, {trainable_params:,} trainable")

    if args.stage == "all":
        model = train_stage_a(model, data_dir, args.epochs_a, args.batch_size,
                              args.lr, device, save_dir)
        model = train_stage_b(model, data_dir, args.epochs_b, min(args.batch_size, 4),
                              args.lr * 0.3, device, save_dir)
        model = train_stage_c(model, data_dir, args.epochs_c, min(args.batch_size, 2),
                              args.lr * 0.1, device, save_dir)
    elif args.stage == "A":
        epochs = args.epochs or args.epochs_a
        train_stage_a(model, data_dir, epochs, args.batch_size, args.lr, device, save_dir)
    elif args.stage == "B":
        epochs = args.epochs or args.epochs_b
        train_stage_b(model, data_dir, epochs, min(args.batch_size, 4),
                      args.lr * 0.3, device, save_dir)
    elif args.stage == "C":
        epochs = args.epochs or args.epochs_c
        train_stage_c(model, data_dir, epochs, min(args.batch_size, 2),
                      args.lr * 0.1, device, save_dir)


if __name__ == "__main__":
    main()
