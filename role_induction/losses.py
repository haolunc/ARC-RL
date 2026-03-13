"""
Loss functions for ARC role-induction training.

  L_total = L_recon + α·L_role + β·L_task + λ·L_mdl

  - L_recon: grid reconstruction from slots (Stage A)
  - L_role:  cross-example role consistency via contrastive loss (Stage B)
  - L_task:  query output prediction accuracy (Stage C)
  - L_mdl:   MDL penalty for role sparsity
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def reconstruction_loss(
    recon_logits: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """
    Per-cell cross-entropy for grid reconstruction.
    Args:
        recon_logits: (B, H, W, C) — predicted colour logits
        target:       (B, H, W) — ground truth grid (long)
        mask:         (B, H, W) — valid region mask (True = compute loss)
    Returns:
        scalar loss
    """
    B, H, W, C = recon_logits.shape
    logits_flat = recon_logits.reshape(-1, C)
    target_flat = target.reshape(-1)

    if mask is not None:
        mask_flat = mask.reshape(-1)
        logits_flat = logits_flat[mask_flat]
        target_flat = target_flat[mask_flat]

    return F.cross_entropy(logits_flat, target_flat)


def mask_entropy_penalty(masks: torch.Tensor) -> torch.Tensor:
    """
    Encourage sharper slot masks (lower entropy → more decisive assignments).
    Args:
        masks: (B, K, H, W) — softmax-normalised over K
    Returns:
        scalar penalty
    """
    eps = 1e-8
    entropy = -(masks * (masks + eps).log()).sum(dim=1)  # (B, H, W)
    return entropy.mean()


def role_contrastive_loss(
    all_roles: list[torch.Tensor],
    all_slots: list[torch.Tensor],
    temperature: float = 0.1,
) -> torch.Tensor:
    """
    Cross-example role consistency via InfoNCE-style contrastive loss.
    Slots with the same role assignment across examples should have
    similar embeddings (positives); different roles are negatives.

    Args:
        all_roles: list of (B, K, R) — role distributions per example
        all_slots: list of (B, K, d) — slot embeddings per example
        temperature: contrastive temperature
    Returns:
        scalar loss
    """
    if len(all_roles) < 2:
        return torch.tensor(0.0, device=all_slots[0].device)

    B, K, d = all_slots[0].shape
    R = all_roles[0].shape[-1]

    # pool slot embeddings by role: weighted average per role
    role_embeds = []  # list of (B, R, d)
    role_counts = []  # list of (B, R) — total weight per role
    for roles, slots in zip(all_roles, all_slots):
        # roles: (B, K, R), slots: (B, K, d)
        weighted = torch.einsum("bkr,bkd->brd", roles, slots)  # (B, R, d)
        counts = roles.sum(dim=1)                                # (B, R)
        role_embeds.append(weighted / (counts.unsqueeze(-1) + 1e-8))
        role_counts.append(counts)

    total_loss = torch.tensor(0.0, device=all_slots[0].device)
    n_pairs = 0

    for i in range(len(role_embeds)):
        for j in range(i + 1, len(role_embeds)):
            # normalise embeddings
            ei = F.normalize(role_embeds[i], dim=-1)  # (B, R, d)
            ej = F.normalize(role_embeds[j], dim=-1)

            # cosine similarity matrix
            sim = torch.einsum("brd,bsd->brs", ei, ej) / temperature  # (B, R, R)

            # positive pairs: same role index (diagonal)
            labels = torch.arange(R, device=sim.device).unsqueeze(0).expand(B, -1)

            # only count roles that are actually used (count > threshold)
            valid_i = role_counts[i] > 0.5  # (B, R)
            valid_j = role_counts[j] > 0.5
            valid = valid_i & valid_j       # (B, R)

            if valid.any():
                sim_valid = sim[valid]                                     # (N, R)
                labels_valid = labels[valid]
                loss_ij = F.cross_entropy(sim_valid, labels_valid)
                total_loss = total_loss + loss_ij
                n_pairs += 1

    return total_loss / max(n_pairs, 1)


def mdl_penalty(role_logits: list[torch.Tensor]) -> torch.Tensor:
    """
    MDL-inspired regularisation: penalise role complexity.
    Encourages sparse role usage (few active roles) via entropy of the
    marginal role distribution.

    Args:
        role_logits: list of (B, K, R) — role logits from all examples
    Returns:
        scalar penalty (lower is more complex → penalty = negative entropy)
    """
    all_probs = torch.cat(role_logits, dim=1)  # (B, total_K, R)
    marginal = all_probs.mean(dim=1)            # (B, R) — avg role distribution

    # negative entropy: more uniform = higher penalty
    eps = 1e-8
    entropy = -(marginal * (marginal + eps).log()).sum(dim=-1)  # (B,)

    # we WANT low entropy (sparse), so penalty = -entropy
    return -entropy.mean()


def task_prediction_loss(
    pred_logits: torch.Tensor,
    target: torch.Tensor,
    h: int,
    w: int,
) -> torch.Tensor:
    """
    Cross-entropy loss for query output prediction.
    Only computed on the valid region [0:h, 0:w].
    """
    logits = pred_logits[:, :h, :w, :]  # (B, h, w, C)
    tgt = target[:, :h, :w]             # (B, h, w)
    return F.cross_entropy(logits.reshape(-1, logits.shape[-1]), tgt.reshape(-1))


def slot_diversity_loss(slots: torch.Tensor) -> torch.Tensor:
    """
    Discourage slot collapse by maximising distance between slot embeddings.
    """
    B, K, d = slots.shape
    slots_norm = F.normalize(slots, dim=-1)
    sim = torch.einsum("bkd,bjd->bkj", slots_norm, slots_norm)  # (B, K, K)

    # remove diagonal
    eye = torch.eye(K, device=sim.device).unsqueeze(0)
    off_diag = sim * (1 - eye)

    return off_diag.abs().mean()


class ArcLoss(nn.Module):
    """Combined loss for all training stages."""

    def __init__(
        self,
        alpha_recon: float = 1.0,
        alpha_mask_ent: float = 0.1,
        alpha_slot_div: float = 0.1,
        alpha_role: float = 1.0,
        alpha_task: float = 1.0,
        alpha_mdl: float = 0.01,
        contrastive_temp: float = 0.1,
    ):
        super().__init__()
        self.alpha_recon = alpha_recon
        self.alpha_mask_ent = alpha_mask_ent
        self.alpha_slot_div = alpha_slot_div
        self.alpha_role = alpha_role
        self.alpha_task = alpha_task
        self.alpha_mdl = alpha_mdl
        self.contrastive_temp = contrastive_temp

    def forward(
        self,
        model_output: dict,
        query_target: torch.Tensor,
        query_h: int,
        query_w: int,
        stage: str = "full",
    ) -> dict[str, torch.Tensor]:
        """
        Compute losses based on training stage.
        stage: "recon" (A), "role" (B), "full" (C)
        """
        losses = {}
        total = torch.tensor(0.0, device=query_target.device)

        # --- reconstruction losses ---
        if stage in ("recon", "full"):
            recon_loss_sum = torch.tensor(0.0, device=query_target.device)
            mask_ent_sum = torch.tensor(0.0, device=query_target.device)
            n = 0
            for r in model_output.get("recon_results", []):
                in_recon, in_grid = r["in_recon"], r["in_grid"]
                H_i, W_i = in_grid.shape[1], in_grid.shape[2]
                in_mask = torch.zeros_like(in_grid, dtype=torch.bool)
                in_mask[:, :H_i, :W_i] = True
                recon_loss_sum = recon_loss_sum + reconstruction_loss(in_recon, in_grid, in_mask)

                out_recon, out_grid = r["out_recon"], r["out_grid"]
                H_o, W_o = out_grid.shape[1], out_grid.shape[2]
                out_mask = torch.zeros_like(out_grid, dtype=torch.bool)
                out_mask[:, :H_o, :W_o] = True
                recon_loss_sum = recon_loss_sum + reconstruction_loss(out_recon, out_grid, out_mask)
                n += 2

            if n > 0:
                losses["recon"] = recon_loss_sum / n
                total = total + self.alpha_recon * losses["recon"]

        # --- role losses ---
        if stage in ("role", "full"):
            all_in_roles = model_output.get("all_in_roles", [])
            all_out_roles = model_output.get("all_out_roles", [])
            all_roles = all_in_roles + all_out_roles

            if len(all_roles) >= 2:
                # need slots for contrastive — extract from recon_results
                # For simplicity, use role distributions directly
                losses["role_contrastive"] = role_contrastive_loss(
                    all_in_roles, all_in_roles,  # placeholder
                    temperature=self.contrastive_temp,
                )
                total = total + self.alpha_role * losses.get("role_contrastive", 0)

            if all_roles:
                losses["mdl"] = mdl_penalty(all_roles)
                total = total + self.alpha_mdl * losses["mdl"]

        # --- task prediction loss ---
        if stage in ("full",):
            pred_logits = model_output.get("pred_logits")
            if pred_logits is not None:
                losses["task"] = task_prediction_loss(
                    pred_logits, query_target, query_h, query_w,
                )
                total = total + self.alpha_task * losses["task"]

        losses["total"] = total
        return losses
