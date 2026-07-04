"""Wave-4: multimodal encoders + fusion (real, trainable PyTorch).

Canon (Aspect 13; C04/C05/C07): NexusNet ingests text, vision, audio, video, tables, and code, and
FUSES them into one shared cognition space. Each encoder projects its modality into the model's
d_model token space; `MultimodalFusion` concatenates the modality token streams and fuses them with
cross-attention so downstream layers see a single unified sequence. All differentiable end-to-end.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from .layers import RMSNorm


class TextEncoder(nn.Module):
    """Token ids -> embeddings (B, T, d_model)."""

    def __init__(self, vocab_size: int, d_model: int) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        return self.embed(token_ids)


class CodeEncoder(TextEncoder):
    """Source code as its own token stream (separate vocab from natural-language text)."""


class VisionEncoder(nn.Module):
    """Patchify an image (B, C, H, W) into patch tokens -> linear patch embedding (B, P, d_model)."""

    def __init__(self, d_model: int, *, in_channels: int = 3, patch: int = 4) -> None:
        super().__init__()
        self.patch = patch
        self.proj = nn.Linear(in_channels * patch * patch, d_model)

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        B, C, H, W = image.shape
        p = self.patch
        if H % p or W % p:
            raise ValueError("image dims must be divisible by patch size")
        # (B, C, H/p, p, W/p, p) -> (B, num_patches, C*p*p)
        x = image.reshape(B, C, H // p, p, W // p, p)
        x = x.permute(0, 2, 4, 1, 3, 5).reshape(B, (H // p) * (W // p), C * p * p)
        return self.proj(x)


class AudioEncoder(nn.Module):
    """Waveform/feature frames (B, L, n_mels) -> strided conv frames -> tokens (B, T, d_model)."""

    def __init__(self, d_model: int, *, n_mels: int = 32, kernel: int = 4, stride: int = 2) -> None:
        super().__init__()
        self.conv = nn.Conv1d(n_mels, d_model, kernel_size=kernel, stride=stride)

    def forward(self, frames: torch.Tensor) -> torch.Tensor:
        x = frames.transpose(1, 2)                       # (B, n_mels, L)
        y = self.conv(x)                                 # (B, d_model, T)
        return y.transpose(1, 2)                         # (B, T, d_model)


class VideoEncoder(nn.Module):
    """Frames (B, F, C, H, W) -> per-frame VisionEncoder -> per-frame mean -> frame tokens (B, F, d_model)."""

    def __init__(self, d_model: int, *, in_channels: int = 3, patch: int = 4) -> None:
        super().__init__()
        self.frame = VisionEncoder(d_model, in_channels=in_channels, patch=patch)

    def forward(self, video: torch.Tensor) -> torch.Tensor:
        B, F, C, H, W = video.shape
        flat = video.reshape(B * F, C, H, W)
        tokens = self.frame(flat)                        # (B*F, P, d_model)
        frame_tok = tokens.mean(dim=1)                   # pool patches per frame
        return frame_tok.reshape(B, F, -1)               # (B, F, d_model)


class TableEncoder(nn.Module):
    """Structured numeric rows (B, n_features) -> one token (B, 1, d_model)."""

    def __init__(self, d_model: int, *, n_features: int) -> None:
        super().__init__()
        self.proj = nn.Linear(n_features, d_model)

    def forward(self, table: torch.Tensor) -> torch.Tensor:
        return self.proj(table).unsqueeze(1)


MODALITIES = ("text", "vision", "audio", "video", "table", "code")


class MultimodalFusion(nn.Module):
    """Fuse modality token streams into one unified sequence via cross-attention.

    Each modality stream is RMSNorm'd and tagged with a learned modality embedding, concatenated along
    the sequence axis, then fused with self-attention so any token can attend across modalities.
    Returns the unified token sequence (B, sum_T, d_model).
    """

    def __init__(self, d_model: int, n_heads: int = 2) -> None:
        super().__init__()
        self.d_model = d_model
        self.norm = RMSNorm(d_model)
        self.modality_embed = nn.Parameter(torch.randn(len(MODALITIES), d_model) * 0.02)
        self.fuse = nn.MultiheadAttention(d_model, num_heads=n_heads, batch_first=True)
        self.out_norm = RMSNorm(d_model)

    def forward(self, streams: dict[str, torch.Tensor]) -> torch.Tensor:
        if not streams:
            raise ValueError("at least one modality stream is required")
        tagged = []
        for name, stream in streams.items():
            if name not in MODALITIES:
                raise ValueError(f"unknown modality {name!r}; allowed {MODALITIES}")
            idx = MODALITIES.index(name)
            tagged.append(self.norm(stream) + self.modality_embed[idx])
        seq = torch.cat(tagged, dim=1)                   # (B, sum_T, d_model)
        fused, _ = self.fuse(seq, seq, seq)              # cross-modality attention
        return self.out_norm(seq + fused)
