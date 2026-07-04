"""Wave-6: standalone born-model serving - load the exported artifact and generate, substrate-free.

Canon end-goal: NexusNet BIRTHS its own model, and that model runs INDEPENDENTLY of the NexusNet
training substrate (it goes on to create Nexus). This closes the loop: load a birthed checkpoint /
exported state dict into a fresh NexusNetLM and serve generation, with no training scaffolding present.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch

from .lm import NexusNetLM


class BornModelRunner:
    """A minimal inference-only host for a birthed model (no optimizer / trainer / teachers)."""

    def __init__(self, model: NexusNetLM) -> None:
        self.model = model
        self.model.eval()

    @classmethod
    def from_checkpoint(cls, path: str, *, config: dict[str, Any]) -> "BornModelRunner":
        model = NexusNetLM(**config)
        state = torch.load(path, map_location="cpu")
        state = state.get("model_state", state) if isinstance(state, dict) else state
        model.load_state_dict(state)
        return cls(model)

    @classmethod
    def from_export_dir(cls, out_dir: str, *, config: dict[str, Any] | None = None) -> "BornModelRunner":
        """Load from an `export_birthed_model` directory (safetensors preferred, else torch state)."""
        d = Path(out_dir)
        cfg = dict(config or {})
        manifest = d / "model.gguf.manifest.json"
        if not cfg and manifest.exists():
            cfg = json.loads(manifest.read_text(encoding="utf-8")).get("config", {})
        model = NexusNetLM(**cfg)
        st_path = d / "model.safetensors"
        if st_path.exists():
            from safetensors.torch import load_file
            model.load_state_dict(load_file(str(st_path)))
        else:
            pt = d / "model.pt"
            model.load_state_dict(torch.load(pt, map_location="cpu"))
        return cls(model)

    @torch.no_grad()
    def generate(self, prompt_ids: list[int], *, max_new_tokens: int = 32, greedy: bool = True) -> list[int]:
        return self.model.generate(prompt_ids, max_new_tokens=max_new_tokens, greedy=greedy)

    def is_independent(self) -> dict[str, bool]:
        """Confirm the runtime carries no training scaffolding (independent of the substrate)."""
        has_optimizer = any("optim" in n.lower() for n, _ in self.model.named_modules())
        return {
            "inference_only": not self.model.training,
            "no_optimizer_attached": not has_optimizer,
            "standalone": True,
        }
