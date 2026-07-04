"""Wave-14: agent observability - OpenTelemetry-GenAI-shaped spans for NexusNet forward passes.

Canon (Overlay agent-observability row): traces should follow OpenTelemetry GenAI semantic conventions
(gen_ai.* attributes) with prompt/completion redaction states, not custom-only JSON. This is a real,
dependency-free recorder: it times a forward pass and emits a span carrying gen_ai.* usage attributes
plus NexusNet specifics (expert load, ponder cost), with content redaction on by default (privacy).
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

import torch


@dataclass
class Span:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    start_ns: int = 0
    end_ns: int = 0
    status: str = "OK"

    @property
    def duration_ms(self) -> float:
        return (self.end_ns - self.start_ns) / 1e6


class GenAISpanRecorder:
    """Record OTel-GenAI-shaped spans. `redact=True` keeps raw token content out of the trace."""

    def __init__(self, *, system: str = "nexusnet", redact: bool = True) -> None:
        self.system = system
        self.redact = redact
        self.spans: list[Span] = []

    @contextmanager
    def span(self, operation: str, **attributes: Any):
        sp = Span(name=operation, attributes={"gen_ai.system": self.system,
                                              "gen_ai.operation.name": operation, **attributes})
        sp.start_ns = time.perf_counter_ns()
        try:
            yield sp
        except Exception as exc:                                   # record failure on the span
            sp.status = "ERROR"
            sp.attributes["error.type"] = type(exc).__name__
            raise
        finally:
            sp.end_ns = time.perf_counter_ns()
            self.spans.append(sp)

    @torch.no_grad()
    def record_forward(self, model: torch.nn.Module, token_ids: torch.Tensor) -> dict[str, Any]:
        """Run a forward pass inside a GenAI span and capture usage + NexusNet attributes."""
        with self.span("forward", **{"gen_ai.request.model": type(model).__name__}) as sp:
            was_training = model.training
            model.eval()
            out = model(token_ids)
            if was_training:
                model.train()
            sp.attributes["gen_ai.usage.input_tokens"] = int(token_ids.numel())
            sp.attributes["gen_ai.response.output_shape"] = list(out.shape)
            sp.attributes["gen_ai.response.finite"] = bool(torch.isfinite(out).all())
            sp.attributes["gen_ai.prompt.redacted"] = self.redact
            if not self.redact:
                sp.attributes["gen_ai.prompt.tokens"] = token_ids.detach().reshape(-1).tolist()
            # NexusNet specifics, when the model exposes them
            loads = [m.last_load.tolist() for m in model.modules()
                     if hasattr(m, "last_load") and m.last_load.numel() > 0]
            if loads:
                sp.attributes["nexusnet.expert_load"] = loads
            ponders = [float(m.last_ponder) for m in model.modules() if hasattr(m, "last_ponder")]
            if ponders:
                sp.attributes["nexusnet.ponder_cost"] = ponders
        return {"output": out, "span": self.spans[-1]}

    def to_otel(self) -> list[dict[str, Any]]:
        """Export accumulated spans as OTel-shaped dicts (name + attributes + duration + status)."""
        return [
            {"name": s.name, "attributes": s.attributes,
             "duration_ms": s.duration_ms, "status": s.status}
            for s in self.spans
        ]
