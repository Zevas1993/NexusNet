"""Wave-10: end-to-end integration - a multimodal NexusNet + a per-expert birth pipeline.

Brings the wave modules together into runnable wholes:

  - MultimodalNexusNet   encoders (Wave 4) -> MultimodalFusion -> canon TransformerBlocks (RoPE + GQA
                         + MoE) -> Cortex pool -> head. One network that ingests several modalities.
  - birth_expert         the per-EXPERT birth flow: build the expert's DOMAIN corpus (Wave 3 corpora)
                         -> train (optionally DISTILL from a teacher, Wave 3) -> measure the capsule's
                         EVAL GATES on held-out data (Wave 3) -> independence milestones (birth gate).
                         Optionally binds GOVERNED SPARSE ROUTING (Wave 2) during training.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from .layers import build_rope, CortexPool
from .transformer import TransformerBlock
from .encoders import (
    TextEncoder, VisionEncoder, AudioEncoder, VideoEncoder, TableEncoder, MultimodalFusion,
)
from .lm import NexusNetLM
from .corpora import domain_corpus_for_capsule
from .birth import make_corpus_windows, split_windows, train_language_model, independence_milestones
from .distill import FrozenTeacher, train_with_distillation
from .eval_gates import evaluate_capsule_gates
from .governed_routing import GovernedSparseRouter


class MultimodalNexusNet(nn.Module):
    """A NexusNet that ingests multiple modalities, fuses them, and reasons over the unified sequence."""

    def __init__(
        self,
        *,
        num_classes: int,
        d_model: int = 48,
        n_heads: int = 4,
        n_kv_heads: int = 2,
        num_experts: int = 6,
        top_k: int = 2,
        d_hidden: int = 96,
        num_layers: int = 2,
        text_vocab: int = 50,
        vision_channels: int = 3,
        vision_patch: int = 4,
        audio_mels: int = 16,
        table_features: int = 8,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.head_dim = d_model // n_heads
        self.text = TextEncoder(text_vocab, d_model)
        self.vision = VisionEncoder(d_model, in_channels=vision_channels, patch=vision_patch)
        self.audio = AudioEncoder(d_model, n_mels=audio_mels)
        self.video = VideoEncoder(d_model, in_channels=vision_channels, patch=vision_patch)
        self.table = TableEncoder(d_model, n_features=table_features)
        self.fusion = MultimodalFusion(d_model, n_heads=2)
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden)
            for _ in range(num_layers)
        ])
        self.cortex = CortexPool(d_model)
        self.head = nn.Linear(d_model, num_classes)

    def encode(self, inputs: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        enc = {"text": self.text, "vision": self.vision, "audio": self.audio,
               "video": self.video, "table": self.table}
        return {name: enc[name](inputs[name]) for name in inputs if name in enc}

    def trunk(self, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
        streams = self.encode(inputs)
        h = self.fusion(streams)                                  # (B, sum_T, d_model)
        cos, sin = build_rope(h.shape[1], self.head_dim, harmonic=True, device=h.device)
        for block in self.blocks:
            h = block(h, cos, sin)
        return self.cortex(h)                                     # (B, d_model)

    def forward(self, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
        return self.head(self.trunk(inputs))

    def update_load_bias(self, update_rate: float = 0.001) -> None:
        for block in self.blocks:
            block.moe.update_load_bias(update_rate)

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def birth_expert(
    capsule_key: str,
    *,
    teacher: NexusNetLM | None = None,
    epochs: int = 80,
    seq_len: int = 24,
    n_sentences: int = 240,
    seed: int = 0,
    accuracy_threshold: float = 0.0,
    perplexity_threshold: float = 1e9,
    govern_allowed: list[int] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Birth one expert end-to-end: DOMAIN corpus -> (distill|train) -> eval gates -> milestones.

    If `teacher` is given, the student distills from it (Wave 3 KD bridge); else it trains on hard
    next-token CE. If `govern_allowed` is given, Governed Sparse Routing (Wave 2) is bound first.
    """
    torch.manual_seed(seed)
    corpus = domain_corpus_for_capsule(capsule_key, n_sentences=n_sentences, seed=seed)
    x, y = make_corpus_windows(corpus, seq_len=seq_len)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed)
    cfg = {"d_model": 64, "n_heads": 4, "n_kv_heads": 2, "num_experts": 6, "top_k": 2,
           "d_hidden": 128, "num_layers": 2}
    if config:
        cfg.update(config)
    student = NexusNetLM(**cfg)

    if govern_allowed is not None:
        GovernedSparseRouter(num_experts=cfg["num_experts"]).govern(student, allowed=govern_allowed)

    if teacher is not None:
        # distillation expects matching shapes; flatten (B,T,V) logits over the token axis for KD.
        frozen = FrozenTeacher(teacher)

        class _FlatStudent(nn.Module):
            def __init__(self, m): super().__init__(); self.m = m
            def forward(self, xb): return self.m(xb).reshape(-1, self.m.head.out_features)
            def parameters(self, *a, **k): return self.m.parameters(*a, **k)
            def update_load_bias(self, *a, **k): return self.m.update_load_bias(*a, **k)

        class _FlatTeacher(nn.Module):
            def __init__(self, t): super().__init__(); self.t = t
            @torch.no_grad()
            def forward(self, xb):
                return self.t(xb).reshape(-1, self.t.model.head.out_features)

        flat_s, flat_t = _FlatStudent(student), _FlatTeacher(frozen)
        distill = train_with_distillation(flat_s, flat_t, x_tr, y_tr.reshape(-1),
                                          epochs=epochs, lr=3e-3)
        metrics = train_language_model(student, x_tr, y_tr, epochs=1, val_x=x_val, val_y=y_val)
        metrics["distillation"] = {k: distill[k] for k in
                                   ("final_loss", "student_matches_teacher", "gradients_flowed")}
    else:
        metrics = train_language_model(student, x_tr, y_tr, epochs=epochs, val_x=x_val, val_y=y_val)

    gate_report = evaluate_capsule_gates(capsule_key, student, x_val, y_val,
                                         accuracy_threshold=accuracy_threshold,
                                         perplexity_threshold=perplexity_threshold)
    milestones = independence_milestones(metrics)
    return {
        "capsule": capsule_key,
        "model": student,
        "metrics": metrics,
        "eval_gates": gate_report,
        "milestones": milestones,
        "distilled": teacher is not None,
        "governed": govern_allowed is not None,
    }
