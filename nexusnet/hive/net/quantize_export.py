"""Wave-4: quantization-aware building blocks + multi-format export of the birthed model.

Canon (Overlay quantization row; C07): the birthed model must be quantization-aware and exportable to
the runtime formats (safetensors / TorchScript / ONNX / GGUF). This module provides:

  - FakeQuantize            differentiable straight-through int8 fake-quant (a QAT building block):
                            forward simulates int8 rounding, backward passes gradients through (STE).
  - quantize_dynamic_int8   real post-training dynamic int8 quantization of the Linear layers.
  - quantization_error      measured round-trip error of int8 weight quantization (honest metric).
  - export_birthed_model    write the model to multiple formats; each format reports a real status
                            (safetensors/torch state_dict always; TorchScript/ONNX best-effort; GGUF
                            as an honest conversion manifest since GGUF needs the llama.cpp converter).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn


class _RoundSTE(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)

    @staticmethod
    def backward(ctx, g):
        return g                                              # straight-through estimator


class FakeQuantize(nn.Module):
    """Per-tensor affine int8 fake-quant: simulate int8 in the forward, pass gradients in the backward.

    Quantization-aware training inserts this so the network learns weights robust to int8 rounding.
    """

    def __init__(self, num_bits: int = 8) -> None:
        super().__init__()
        self.qmin = -(2 ** (num_bits - 1))
        self.qmax = 2 ** (num_bits - 1) - 1

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        max_abs = x.detach().abs().max().clamp(min=1e-8)
        scale = max_abs / self.qmax
        q = _RoundSTE.apply(x / scale).clamp(self.qmin, self.qmax)
        return q * scale                                     # dequantized (simulated int8)


def quantization_error(model: nn.Module) -> dict[str, float]:
    """Mean relative L2 error of int8 round-trip over the model's weights (lower = more robust)."""
    fq = FakeQuantize()
    num = den = 0.0
    with torch.no_grad():
        for p in model.parameters():
            if p.dim() >= 2:
                err = (fq(p) - p).pow(2).sum().item()
                num += err
                den += p.pow(2).sum().item()
    rel = (num / den) ** 0.5 if den > 0 else 0.0
    return {"relative_l2_error": rel, "bits": 8}


def quantize_dynamic_int8(model: nn.Module) -> nn.Module:
    """Real post-training dynamic int8 quantization of Linear layers (CPU inference compression)."""
    model.eval()
    return torch.ao.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)


def _export_state_dict(model: nn.Module, out_dir: Path) -> dict[str, Any]:
    sd = model.state_dict()
    try:
        from safetensors.torch import save_file
        path = out_dir / "model.safetensors"
        save_file({k: v.contiguous() for k, v in sd.items()}, str(path))
        return {"format": "safetensors", "path": str(path), "status": "written"}
    except Exception:
        path = out_dir / "model.pt"
        torch.save(sd, path)
        return {"format": "torch_state_dict", "path": str(path),
                "status": "written", "note": "safetensors unavailable; wrote torch .pt"}


def _export_torchscript(model: nn.Module, out_dir: Path, example_input) -> dict[str, Any]:
    if example_input is None:
        return {"format": "torchscript", "status": "skipped", "reason": "no example_input"}
    try:
        model.eval()
        scripted = torch.jit.trace(model, example_input, check_trace=False)
        path = out_dir / "model.ts.pt"
        scripted.save(str(path))
        return {"format": "torchscript", "path": str(path), "status": "written"}
    except Exception as exc:  # data-dependent control flow can defeat tracing
        return {"format": "torchscript", "status": "failed", "reason": str(exc)[:200]}


def _export_onnx(model: nn.Module, out_dir: Path, example_input) -> dict[str, Any]:
    if example_input is None:
        return {"format": "onnx", "status": "skipped", "reason": "no example_input"}
    try:
        model.eval()
        path = out_dir / "model.onnx"
        torch.onnx.export(model, example_input, str(path), opset_version=17,
                          input_names=["input"], output_names=["logits"],
                          dynamic_axes={"input": {0: "batch"}})
        return {"format": "onnx", "path": str(path), "status": "written"}
    except Exception as exc:
        return {"format": "onnx", "status": "failed", "reason": str(exc)[:200]}


def _export_gguf_manifest(model: nn.Module, out_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    """GGUF needs the llama.cpp converter; write an honest conversion manifest (not a fake .gguf)."""
    path = out_dir / "model.gguf.manifest.json"
    manifest = {
        "target_format": "gguf",
        "status": "conversion_manifest",
        "note": "GGUF requires the llama.cpp convert script; this manifest records the metadata needed.",
        "config": config,
        "num_parameters": sum(p.numel() for p in model.parameters()),
        "tensor_names": list(model.state_dict().keys())[:64],
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"format": "gguf", "path": str(path), "status": "conversion_manifest"}


def export_birthed_model(
    model: nn.Module,
    out_dir: str,
    *,
    example_input: torch.Tensor | None = None,
    config: dict[str, Any] | None = None,
    formats: tuple[str, ...] = ("safetensors", "torchscript", "onnx", "gguf"),
) -> dict[str, Any]:
    """Export the birthed model to the requested runtime formats; returns a per-format status report."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    if "safetensors" in formats:
        results["safetensors"] = _export_state_dict(model, out)
    if "torchscript" in formats:
        results["torchscript"] = _export_torchscript(model, out, example_input)
    if "onnx" in formats:
        results["onnx"] = _export_onnx(model, out, example_input)
    if "gguf" in formats:
        results["gguf"] = _export_gguf_manifest(model, out, config or {})
    written = [k for k, v in results.items() if v.get("status") in ("written", "conversion_manifest")]
    return {"out_dir": str(out), "formats": results, "written": written}
