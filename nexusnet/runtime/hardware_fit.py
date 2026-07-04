"""PB-2026-06-03-100 - Hardware-Aware Local Model Fit Recommender (native, redacted, no installs).

Canon doctrine: assimilate the `llm-checker` CAPABILITY natively, do not blindly depend on the npm
package. Detect hardware -> recommend models by task category, explaining which local models /
quantizations / backends are viable for THIS machine. Hardware evidence is REDACTED (no serial numbers
or user paths, no telemetry/federation of private identifiers). The recommender NEVER installs
packages, downloads models, or mutates provider routes. An external `llm-checker` adapter is allowed
only after package/dependency/license review (not invoked here).
"""
from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HardwareSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cpu: str = ""
    ram_gb: float = 0.0
    gpu: str = ""
    vram_gb: float = 0.0
    backend: str = "cpu"                  # cpu | cuda | rocm | metal | directml | ...
    os: str = ""
    accelerator: str = ""
    # raw identifiers that must be redacted from shared evidence
    serial: str = ""
    user_path: str = ""

    def redacted(self) -> dict[str, Any]:
        """Hardware evidence safe to share: strips serials/user paths, scrubs path-like CPU/GPU strings."""
        def _scrub(s: str) -> str:
            s = re.sub(r"[A-Za-z]:\\\\?[^\s]+|/home/[^\s]+|/Users/[^\s]+", "<path>", s)
            return s
        return {
            "cpu": _scrub(self.cpu), "ram_gb": self.ram_gb, "gpu": _scrub(self.gpu),
            "vram_gb": self.vram_gb, "backend": self.backend, "os": self.os,
            "accelerator": self.accelerator,
            "redacted_fields": [f for f in ("serial", "user_path") if getattr(self, f)],
        }


class ModelFitCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    task_categories: list[str] = Field(default_factory=list)
    min_ram_gb: float = 0.0
    min_vram_gb: float = 0.0               # 0 => CPU-runnable
    quantization: str = "fp16"
    expected_latency_ms: float = 0.0
    privacy_class: Literal["public", "internal", "private"] = "public"
    cost_per_1k: float = 0.0
    license_status: Literal["approved", "needs_review", "blocked"] = "needs_review"
    eval_score: float = 0.0


class ModelFitRecommender:
    """Rank candidate models that FIT the machine for a task category. Read-only, no installs/downloads."""

    mutates_production = False
    performs_install_or_download = False

    def __init__(self, candidates: list[ModelFitCandidate] | None = None) -> None:
        self.candidates = list(candidates or [])

    def add(self, candidate: ModelFitCandidate) -> None:
        self.candidates.append(candidate)

    def _fits(self, c: ModelFitCandidate, hw: HardwareSnapshot) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if c.min_ram_gb > hw.ram_gb:
            reasons.append("insufficient_ram")
        if c.min_vram_gb > 0 and c.min_vram_gb > hw.vram_gb:
            reasons.append("insufficient_vram")
        if c.license_status == "blocked":
            reasons.append("license_blocked")
        return (not reasons, reasons)

    def recommend(self, hardware: HardwareSnapshot, task_category: str, *, top_k: int = 5
                  ) -> dict[str, Any]:
        """Return ranked fitting candidates + the blocked ones (with reasons) + redacted hw evidence."""
        viable: list[tuple[float, ModelFitCandidate]] = []
        blocked: list[dict[str, Any]] = []
        for c in self.candidates:
            if task_category not in c.task_categories:
                continue
            fits, reasons = self._fits(c, hardware)
            if not fits:
                blocked.append({"model_id": c.model_id, "reasons": reasons})
                continue
            # rank: higher eval, lower latency, lower cost, license-approved bonus
            score = (c.eval_score
                     - 0.0005 * c.expected_latency_ms
                     - 0.1 * c.cost_per_1k
                     + (0.1 if c.license_status == "approved" else 0.0))
            viable.append((score, c))
        viable.sort(key=lambda t: t[0], reverse=True)
        ranked = [{"model_id": c.model_id, "quantization": c.quantization,
                   "min_vram_gb": c.min_vram_gb, "expected_latency_ms": c.expected_latency_ms,
                   "license_status": c.license_status, "eval_score": c.eval_score,
                   "fit_score": round(s, 4)}
                  for s, c in viable[:top_k]]
        return {
            "task_category": task_category,
            "hardware": hardware.redacted(),
            "recommendations": ranked,
            "blocked": blocked,
            "any_viable": bool(ranked),
            "performs_install_or_download": False,
            "mutates_production": False,
        }
