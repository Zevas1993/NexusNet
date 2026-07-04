"""Wave-6: hardware-aware adaptive runtime + Safe Mode gating the real forward.

Canon (C12/C06; Overlay hardware row): NexusNet detects hardware, adapts dtype/context/batch/quant,
and has a Safe Mode that auto-throttles or pauses on VRAM/thermal pressure (then resumes). Real,
deterministic policy logic; the actual forward is gated through `SafeModeGuard`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import torch


@dataclass
class HardwareProfile:
    has_cuda: bool
    vram_gb: float
    device: str
    name: str = "cpu"

    @classmethod
    def detect(cls) -> "HardwareProfile":
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            return cls(True, props.total_memory / 1e9, "cuda", props.name)
        return cls(False, 0.0, "cpu", "cpu")


@dataclass
class RuntimePlan:
    device: str
    dtype: str
    max_context: int
    batch_size: int
    quantize: bool
    rationale: list[str] = field(default_factory=list)


class AdaptiveRuntimePolicy:
    """Pick dtype/context/batch/quant from the hardware profile + model size (deterministic)."""

    def plan(self, profile: HardwareProfile, *, param_count: int) -> RuntimePlan:
        rationale: list[str] = []
        if profile.has_cuda:
            device, dtype = "cuda", "bf16"
            rationale.append("CUDA present -> bf16 mixed precision")
            if profile.vram_gb >= 12:
                max_context, batch, quantize = 8192, 8, False
                rationale.append(f"{profile.vram_gb:.0f}GB VRAM -> long context, no quant")
            else:
                max_context, batch, quantize = 4096, 4, True
                rationale.append("limited VRAM -> shorter context + int8 quant")
        else:
            device, dtype, max_context, batch, quantize = "cpu", "fp32", 1024, 1, True
            rationale.append("no GPU -> CPU fp32, small context, int8 quant for footprint")
        if param_count > 50_000_000:
            quantize = True
            rationale.append("large model -> force quantization")
        return RuntimePlan(device, dtype, max_context, batch, quantize, rationale)


@dataclass
class SafeModeDecision:
    safe: bool
    action: str            # "proceed" | "throttle" | "pause"
    batch_size: int
    max_context: int
    reasons: list[str]


class SafeModeGuard:
    """Monitor VRAM/thermal pressure and throttle/pause the forward when unsafe; resume when clear."""

    def __init__(self, *, vram_limit_gb: float, temp_limit_c: float = 85.0,
                 base_batch: int = 8, base_context: int = 8192) -> None:
        self.vram_limit_gb = vram_limit_gb
        self.temp_limit_c = temp_limit_c
        self.base_batch = base_batch
        self.base_context = base_context
        self.paused = False

    def assess(self, *, vram_used_gb: float, temp_c: float) -> SafeModeDecision:
        reasons: list[str] = []
        vram_ratio = vram_used_gb / max(1e-6, self.vram_limit_gb)
        over_temp = temp_c >= self.temp_limit_c
        if vram_ratio >= 0.98 or temp_c >= self.temp_limit_c + 5:
            self.paused = True
            reasons.append("critical VRAM/thermal -> PAUSE")
            return SafeModeDecision(False, "pause", 0, 0, reasons)
        if vram_ratio >= 0.85 or over_temp:
            self.paused = False
            reasons.append(f"pressure (vram {vram_ratio:.0%}, temp {temp_c:.0f}C) -> throttle")
            return SafeModeDecision(False, "throttle", max(1, self.base_batch // 2),
                                    max(512, self.base_context // 2), reasons)
        self.paused = False
        reasons.append("nominal -> proceed")
        return SafeModeDecision(True, "proceed", self.base_batch, self.base_context, reasons)


@torch.no_grad()
def safe_forward(model: torch.nn.Module, x: torch.Tensor, guard: SafeModeGuard,
                 *, vram_used_gb: float, temp_c: float) -> dict[str, Any]:
    """Gate a forward through Safe Mode: pause -> refuse; throttle -> trim batch; else run."""
    decision = guard.assess(vram_used_gb=vram_used_gb, temp_c=temp_c)
    if decision.action == "pause":
        return {"ran": False, "decision": decision, "output": None}
    xin = x
    if decision.action == "throttle" and x.shape[0] > decision.batch_size:
        xin = x[: decision.batch_size]                      # trim batch under pressure
    out = model(xin)
    return {"ran": True, "decision": decision, "output": out}
