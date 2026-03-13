"""
Neural modules for ARC role-induction system.

Architecture (following the deep-research-report):
  1. GridEncoder    — colour embedding + 2D position embedding + Transformer (ViT-style)
  2. SlotAttention  — iterative competitive attention → K object slots + soft masks
  3. RoleNetwork    — task-context-conditioned posterior q(r|slot, ctx) over R_max roles
  4. GridDecoder    — spatial broadcast decoder to reconstruct grids from slots
  5. TransformEncoder — encodes input→output slot-level transformations
  6. ARCModel       — end-to-end wrapper
"""

from __future__ import annotations

import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# 1. Grid Encoder (ViT-style, 1×1 patches = each cell is a token)
# ---------------------------------------------------------------------------

class GridEncoder(nn.Module):
    """Encodes an ARC grid (H×W, values 0-9) into d-dimensional token embeddings."""

    def __init__(self, d_model: int = 128, n_colors: int = 10,
                 max_h: int = 30, max_w: int = 30, n_layers: int = 4, n_heads: int = 4):
        super().__init__()
        self.d_model = d_model
        self.color_embed = nn.Embedding(n_colors, d_model)
        self.row_embed = nn.Embedding(max_h, d_model)
        self.col_embed = nn.Embedding(max_w, d_model)
        self.bg_indicator = nn.Embedding(2, d_model)  # 0=non-bg, 1=bg

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_model * 4,
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, grid: torch.Tensor) -> torch.Tensor:
        """
        Args:
            grid: (B, H, W) long tensor, values in [0,9]
        Returns:
            tokens: (B, H*W, d_model)
        """
        B, H, W = grid.shape
        rows = torch.arange(H, device=grid.device).unsqueeze(1).expand(H, W)
        cols = torch.arange(W, device=grid.device).unsqueeze(0).expand(H, W)

        color_emb = self.color_embed(grid)                          # (B, H, W, d)
        row_emb = self.row_embed(rows).unsqueeze(0).expand(B, -1, -1, -1)
        col_emb = self.col_embed(cols).unsqueeze(0).expand(B, -1, -1, -1)
        bg = (grid == 0).long()
        bg_emb = self.bg_indicator(bg)

        x = color_emb + row_emb + col_emb + bg_emb                 # (B, H, W, d)
        x = x.view(B, H * W, self.d_model)
        x = self.norm(self.transformer(x))
        return x


# ---------------------------------------------------------------------------
# 2. Slot Attention
# ---------------------------------------------------------------------------

class SlotAttention(nn.Module):
    """
    Slot Attention module (Locatello et al., 2020).
    Iterative competitive attention to produce K exchangeable object slots.
    """

    def __init__(self, d_input: int = 128, d_slot: int = 128, n_slots: int = 8,
                 n_iter: int = 3, mlp_hidden: int = 256, eps: float = 1e-8):
        super().__init__()
        self.n_slots = n_slots
        self.n_iter = n_iter
        self.d_slot = d_slot
        self.eps = eps

        self.norm_input = nn.LayerNorm(d_input)
        self.norm_slots = nn.LayerNorm(d_slot)
        self.norm_mlp = nn.LayerNorm(d_slot)

        self.slots_mu = nn.Parameter(torch.randn(1, 1, d_slot) * (d_slot ** -0.5))
        self.slots_log_sigma = nn.Parameter(torch.zeros(1, 1, d_slot))

        self.project_q = nn.Linear(d_slot, d_slot, bias=False)
        self.project_k = nn.Linear(d_input, d_slot, bias=False)
        self.project_v = nn.Linear(d_input, d_slot, bias=False)

        self.gru = nn.GRUCell(d_slot, d_slot)
        self.mlp = nn.Sequential(
            nn.Linear(d_slot, mlp_hidden),
            nn.GELU(),
            nn.Linear(mlp_hidden, d_slot),
        )

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            inputs: (B, N, d_input) — encoder output tokens
        Returns:
            slots:  (B, K, d_slot)
            attn:   (B, K, N) — attention weights (soft masks)
        """
        B, N, _ = inputs.shape
        mu = self.slots_mu.expand(B, self.n_slots, -1)
        sigma = self.slots_log_sigma.exp().expand(B, self.n_slots, -1)
        slots = mu + sigma * torch.randn_like(mu)

        inputs = self.norm_input(inputs)
        k = self.project_k(inputs)  # (B, N, d_slot)
        v = self.project_v(inputs)  # (B, N, d_slot)

        attn = None
        for _ in range(self.n_iter):
            slots_prev = slots
            slots = self.norm_slots(slots)
            q = self.project_q(slots)                               # (B, K, d_slot)

            scale = self.d_slot ** -0.5
            dots = torch.einsum("bkd,bnd->bkn", q, k) * scale      # (B, K, N)
            attn = F.softmax(dots, dim=1)                            # normalise over slots
            attn_normed = attn / (attn.sum(dim=-1, keepdim=True) + self.eps)

            updates = torch.einsum("bkn,bnd->bkd", attn_normed, v)  # (B, K, d_slot)

            slots = self.gru(
                updates.reshape(-1, self.d_slot),
                slots_prev.reshape(-1, self.d_slot),
            ).view(B, self.n_slots, self.d_slot)

            slots = slots + self.mlp(self.norm_mlp(slots))

        return slots, attn


# ---------------------------------------------------------------------------
# 3. Role Posterior Network
# ---------------------------------------------------------------------------

class RoleNetwork(nn.Module):
    """
    Produces per-slot role distributions q(r_k | s_k, c_task).
    Roles are categorical latent variables, relaxed via Gumbel-Softmax.
    """

    def __init__(self, d_slot: int = 128, n_roles: int = 16,
                 d_context: int = 128, n_heads: int = 4, n_layers: int = 2):
        super().__init__()
        self.n_roles = n_roles

        self.context_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=d_slot, nhead=n_heads, dim_feedforward=d_slot * 4,
                dropout=0.1, activation="gelu", batch_first=True,
            ),
            num_layers=n_layers,
        )
        self.context_pool = nn.Sequential(
            nn.LayerNorm(d_slot),
            nn.Linear(d_slot, d_context),
        )

        self.role_logits = nn.Sequential(
            nn.Linear(d_slot + d_context, d_slot),
            nn.GELU(),
            nn.Linear(d_slot, n_roles),
        )

        self.role_prototypes = nn.Parameter(torch.randn(n_roles, d_slot) * 0.02)

    def compute_context(self, all_slots: torch.Tensor) -> torch.Tensor:
        """
        Compute task-level context from all support example slots.
        Args:
            all_slots: (B, total_K, d_slot) — concatenated slots from all support examples
        Returns:
            context: (B, d_context)
        """
        h = self.context_encoder(all_slots)
        return self.context_pool(h.mean(dim=1))

    def forward(self, slots: torch.Tensor, context: torch.Tensor,
                temperature: float = 1.0, hard: bool = False
                ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            slots:   (B, K, d_slot)
            context: (B, d_context)
            temperature: Gumbel-Softmax temperature
            hard: if True, return one-hot (straight-through)
        Returns:
            role_probs: (B, K, n_roles) — soft or hard role assignments
            role_logits: (B, K, n_roles) — raw logits
        """
        B, K, d = slots.shape
        ctx = context.unsqueeze(1).expand(B, K, -1)
        combined = torch.cat([slots, ctx], dim=-1)                  # (B, K, d_slot+d_ctx)
        logits = self.role_logits(combined)                         # (B, K, n_roles)

        if self.training:
            role_probs = F.gumbel_softmax(logits, tau=temperature, hard=hard, dim=-1)
        else:
            role_probs = F.softmax(logits / max(temperature, 1e-6), dim=-1)

        return role_probs, logits

    def get_role_embeddings(self, role_probs: torch.Tensor) -> torch.Tensor:
        """Map soft role assignments to role-prototype-weighted embeddings."""
        return torch.einsum("bkr,rd->bkd", role_probs, self.role_prototypes)


# ---------------------------------------------------------------------------
# 4. Grid Decoder (spatial broadcast)
# ---------------------------------------------------------------------------

class GridDecoder(nn.Module):
    """
    Reconstructs a grid from slots via spatial broadcast decoding.
    Each slot broadcasts its features to every spatial position, then
    a small MLP outputs per-slot colour logits and mask logits.
    The final grid is a mixture.
    """

    def __init__(self, d_slot: int = 128, max_h: int = 30, max_w: int = 30,
                 n_colors: int = 10, hidden: int = 256):
        super().__init__()
        self.max_h = max_h
        self.max_w = max_w
        self.pos_embed = nn.Parameter(torch.randn(1, max_h * max_w, d_slot) * 0.02)

        self.decoder = nn.Sequential(
            nn.Linear(d_slot * 2, hidden),
            nn.GELU(),
            nn.Linear(hidden, hidden),
            nn.GELU(),
        )
        self.to_color = nn.Linear(hidden, n_colors)
        self.to_mask = nn.Linear(hidden, 1)

    def forward(self, slots: torch.Tensor, H: int, W: int
                ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            slots: (B, K, d_slot)
            H, W: target grid dimensions
        Returns:
            recon_logits: (B, H, W, n_colors) — per-cell colour logits
            masks: (B, K, H, W) — per-slot spatial masks
        """
        B, K, d = slots.shape
        N = H * W

        pos = self.pos_embed[:, :N, :]                              # (1, N, d)
        slots_broadcast = slots.unsqueeze(2).expand(B, K, N, d)     # (B, K, N, d)
        pos_broadcast = pos.unsqueeze(1).expand(B, K, N, d)         # (B, K, N, d)

        x = torch.cat([slots_broadcast, pos_broadcast], dim=-1)     # (B, K, N, 2d)
        h = self.decoder(x)                                         # (B, K, N, hidden)

        color_logits = self.to_color(h)                             # (B, K, N, n_colors)
        mask_logits = self.to_mask(h).squeeze(-1)                   # (B, K, N)

        masks = F.softmax(mask_logits, dim=1)                       # (B, K, N)
        recon = (masks.unsqueeze(-1) * color_logits).sum(dim=1)     # (B, N, n_colors)
        recon = recon.view(B, H, W, -1)
        masks = masks.view(B, K, H, W)

        return recon, masks


# ---------------------------------------------------------------------------
# 5. Transformation Encoder
# ---------------------------------------------------------------------------

class TransformEncoder(nn.Module):
    """
    Encodes how slots transform from input to output.
    Takes paired (input_slots, output_slots) and produces transformation embeddings.
    """

    def __init__(self, d_slot: int = 128, d_transform: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(d_slot * 2, d_slot),
            nn.GELU(),
            nn.Linear(d_slot, d_transform),
        )
        self.aggregator = nn.Sequential(
            nn.LayerNorm(d_transform),
            nn.Linear(d_transform, d_transform),
        )

    def forward(self, in_slots: torch.Tensor, out_slots: torch.Tensor,
                role_probs_in: torch.Tensor, role_probs_out: torch.Tensor
                ) -> torch.Tensor:
        """
        Align input/output slots by role similarity, then encode transforms.
        Args:
            in_slots:  (B, K, d_slot)
            out_slots: (B, K, d_slot)
            role_probs_in:  (B, K, R)
            role_probs_out: (B, K, R)
        Returns:
            transform_emb: (B, d_transform)
        """
        # soft alignment matrix via role similarity
        alignment = torch.einsum("bkr,bjr->bkj", role_probs_in, role_probs_out)  # (B, K, K)
        alignment = alignment / (alignment.sum(dim=-1, keepdim=True) + 1e-8)

        matched_out = torch.einsum("bkj,bjd->bkd", alignment, out_slots)         # (B, K, d)
        paired = torch.cat([in_slots, matched_out], dim=-1)                        # (B, K, 2d)
        per_slot = self.encoder(paired)                                            # (B, K, d_t)

        return self.aggregator(per_slot.mean(dim=1))                               # (B, d_t)


# ---------------------------------------------------------------------------
# 6. Output Predictor
# ---------------------------------------------------------------------------

class OutputPredictor(nn.Module):
    """
    Predicts the output grid given test input slots + learned transformation.
    Conditions the decoder on transformation embeddings.
    """

    def __init__(self, d_slot: int = 128, d_transform: int = 128,
                 max_h: int = 30, max_w: int = 30, n_colors: int = 10):
        super().__init__()
        self.transform_project = nn.Linear(d_transform, d_slot)

        self.decoder = GridDecoder(d_slot=d_slot, max_h=max_h, max_w=max_w,
                                   n_colors=n_colors)

    def forward(self, test_slots: torch.Tensor, transform_emb: torch.Tensor,
                H: int, W: int) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            test_slots: (B, K, d_slot)
            transform_emb: (B, d_transform)
        Returns:
            output_logits: (B, H, W, n_colors)
            masks: (B, K, H, W)
        """
        t = self.transform_project(transform_emb).unsqueeze(1)     # (B, 1, d_slot)
        conditioned = test_slots + t                                 # broadcast add
        return self.decoder(conditioned, H, W)


# ---------------------------------------------------------------------------
# 7. Full ARC Model
# ---------------------------------------------------------------------------

class ARCModel(nn.Module):
    """
    End-to-end ARC model:
      grid → encoder → slots → roles → {reconstruction, transformation, prediction}
    """

    def __init__(self, d_model: int = 128, n_slots: int = 8, n_roles: int = 16,
                 slot_iter: int = 3, enc_layers: int = 4, n_colors: int = 10):
        super().__init__()
        self.encoder = GridEncoder(d_model=d_model, n_layers=enc_layers)
        self.slot_attn = SlotAttention(d_input=d_model, d_slot=d_model, n_slots=n_slots,
                                        n_iter=slot_iter)
        self.role_net = RoleNetwork(d_slot=d_model, n_roles=n_roles, d_context=d_model)
        self.recon_decoder = GridDecoder(d_slot=d_model, n_colors=n_colors)
        self.transform_enc = TransformEncoder(d_slot=d_model, d_transform=d_model)
        self.output_pred = OutputPredictor(d_slot=d_model, d_transform=d_model,
                                            n_colors=n_colors)

    def encode_grid(self, grid: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Encode a grid → (slots, attn_masks)."""
        tokens = self.encoder(grid)
        return self.slot_attn(tokens)

    def reconstruct(self, grid: torch.Tensor
                    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Self-supervised reconstruction path."""
        B, H, W = grid.shape
        slots, attn = self.encode_grid(grid)
        recon_logits, masks = self.recon_decoder(slots, H, W)
        return recon_logits, masks, slots, attn

    def forward_task(
        self,
        support_inputs: list[torch.Tensor],   # list of (B, H_i, W_i)
        support_outputs: list[torch.Tensor],   # list of (B, H_o, W_o)
        query_input: torch.Tensor,             # (B, H_q, W_q)
        query_output_size: tuple[int, int],    # (H_out, W_out)
        temperature: float = 1.0,
    ) -> dict[str, torch.Tensor]:
        """
        Full episodic forward pass for a task.
        Returns dict with all intermediate tensors needed for loss computation.
        """
        B = query_input.shape[0]
        all_in_slots, all_out_slots = [], []
        all_in_roles, all_out_roles = [], []
        recon_results = []

        # encode all support pairs
        for inp, out in zip(support_inputs, support_outputs):
            in_slots, in_attn = self.encode_grid(inp)
            out_slots, out_attn = self.encode_grid(out)
            all_in_slots.append(in_slots)
            all_out_slots.append(out_slots)

            H_i, W_i = inp.shape[1], inp.shape[2]
            in_recon, in_masks = self.recon_decoder(in_slots, H_i, W_i)
            H_o, W_o = out.shape[1], out.shape[2]
            out_recon, out_masks = self.recon_decoder(out_slots, H_o, W_o)
            recon_results.append({
                "in_recon": in_recon, "in_grid": inp,
                "out_recon": out_recon, "out_grid": out,
            })

        # task context from all support slots
        concat_slots = torch.cat(all_in_slots + all_out_slots, dim=1)  # (B, total_K, d)
        context = self.role_net.compute_context(concat_slots)

        # role assignment for all slots
        for i in range(len(support_inputs)):
            in_roles, in_logits = self.role_net(all_in_slots[i], context, temperature)
            out_roles, out_logits = self.role_net(all_out_slots[i], context, temperature)
            all_in_roles.append(in_roles)
            all_out_roles.append(out_roles)

        # aggregate transformation across support pairs
        transform_embs = []
        for i in range(len(support_inputs)):
            t = self.transform_enc(
                all_in_slots[i], all_out_slots[i],
                all_in_roles[i], all_out_roles[i],
            )
            transform_embs.append(t)
        avg_transform = torch.stack(transform_embs, dim=0).mean(dim=0)  # (B, d_t)

        # predict query output
        q_slots, q_attn = self.encode_grid(query_input)
        q_roles, q_logits = self.role_net(q_slots, context, temperature)
        H_out, W_out = query_output_size
        pred_logits, pred_masks = self.output_pred(q_slots, avg_transform, H_out, W_out)

        return {
            "pred_logits": pred_logits,         # (B, H_out, W_out, 10)
            "pred_masks": pred_masks,
            "recon_results": recon_results,
            "all_in_roles": all_in_roles,       # list of (B, K, R)
            "all_out_roles": all_out_roles,
            "query_roles": q_roles,
            "query_role_logits": q_logits,
            "transform_emb": avg_transform,
        }
