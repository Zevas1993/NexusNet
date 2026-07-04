from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProductTraceEvent(BaseModel):
    trace_id: str
    input_id: str
    brain_path: str = "NexusBrain.generate"
    capsule_routes: list[dict[str, Any]] = Field(default_factory=list)
    memory_operations: list[dict[str, Any]] = Field(default_factory=list)
    tool_attempts: list[dict[str, Any]] = Field(default_factory=list)
    security_decisions: list[dict[str, Any]] = Field(default_factory=list)
    critique_events: list[dict[str, Any]] = Field(default_factory=list)
    eval_labels: list[str] = Field(default_factory=lambda: ["trace_first", "diagnostic_only"])
    final_output_metadata: dict[str, Any] = Field(default_factory=dict)


def build_product_trace_event(
    *,
    trace_id: str,
    input_id: str,
    capsule_id: str | None,
    model_id: str,
    runtime_name: str,
    memory_retrieval_count: int,
    memory_write_planned: bool,
    fallback_used: bool,
    critique_id: str,
    critique_status: str,
) -> dict[str, Any]:
    event = ProductTraceEvent(
        trace_id=trace_id,
        input_id=input_id,
        capsule_routes=[
            {
                "capsule_id": capsule_id or "general",
                "confidence": 0.5 if fallback_used else 0.8,
                "risk": 0.2 if not fallback_used else 0.45,
                "model_id": model_id,
                "fallback_reason": "runtime_fallback" if fallback_used else None,
            }
        ],
        memory_operations=[
            {"operation": "retrieve", "count": memory_retrieval_count, "provenance_required": True},
            {"operation": "store", "planned": memory_write_planned, "provenance_required": True},
        ],
        tool_attempts=[],
        security_decisions=[
            {
                "status": "brain_internal_only",
                "reason": "No external tool execution was requested for this brain path.",
            }
        ],
        critique_events=[{"critique_id": critique_id, "status": critique_status}],
        final_output_metadata={
            "model_id": model_id,
            "runtime_name": runtime_name,
            "brain_path": "NexusBrain.generate",
        },
    )
    return event.model_dump(mode="json")
