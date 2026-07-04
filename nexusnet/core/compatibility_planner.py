from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..moe.expert_adapter import ExpertAdapterService


class CompatibilityStatus(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    ADAPTER_REQUIRED = "ADAPTER_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    UNVERIFIED = "UNVERIFIED"


class CompatibilityIssue(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "warning"
    field: str | None = None


class CompatibilityPlan(BaseModel):
    compatibility_plan_id: str
    status: CompatibilityStatus
    ok_for_product_attach: bool
    summary: str
    issues: list[CompatibilityIssue] = Field(default_factory=list)
    model_name: str | None = None
    model_family: str | None = None
    router_hidden_dim: int | None = None
    expert_hidden_dim: int | None = None
    vocab_size: int | None = None
    dtype: str | None = None
    device: str | None = None
    parameter_count: int | None = None
    adapter_recommendation: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseModelCompatibilityPlanner:
    def plan(
        self,
        *,
        metadata: dict[str, Any] | None = None,
        router_hidden_dim: int | None = None,
        expert_hidden_dim: int | None = None,
        strict_product_mode: bool = True,
    ) -> CompatibilityPlan:
        payload = dict(metadata or {})
        router_dim = self._int_value(router_hidden_dim if router_hidden_dim is not None else payload.get("router_hidden_dim"))
        expert_dim = self._int_value(
            expert_hidden_dim
            if expert_hidden_dim is not None
            else payload.get("expert_hidden_dim", payload.get("hidden_size"))
        )
        vocab_size = self._int_value(payload.get("vocab_size"))
        parameter_count = self._int_value(payload.get("parameter_count"))
        issues: list[CompatibilityIssue] = []

        if router_dim is None and strict_product_mode:
            issues.append(
                CompatibilityIssue(
                    code="missing-router-hidden-dim",
                    field="router_hidden_dim",
                    message="Product-mode attachment requires router hidden dimension metadata.",
                )
            )
        elif router_dim is not None and router_dim <= 0:
            issues.append(
                CompatibilityIssue(
                    code="invalid-router-hidden-dim",
                    field="router_hidden_dim",
                    severity="error",
                    message="Router hidden dimension must be a positive integer.",
                )
            )

        if expert_dim is None and strict_product_mode:
            issues.append(
                CompatibilityIssue(
                    code="missing-expert-hidden-dim",
                    field="expert_hidden_dim",
                    message="Product-mode attachment requires expert/model hidden dimension metadata.",
                )
            )
        elif expert_dim is not None and expert_dim <= 0:
            issues.append(
                CompatibilityIssue(
                    code="invalid-expert-hidden-dim",
                    field="expert_hidden_dim",
                    severity="error",
                    message="Expert hidden dimension must be a positive integer.",
                )
            )

        if vocab_size is not None and vocab_size <= 0:
            issues.append(
                CompatibilityIssue(
                    code="invalid-vocab-size",
                    field="metadata.vocab_size",
                    severity="error",
                    message="Vocabulary size must be a positive integer when provided.",
                )
            )
        if parameter_count is not None and parameter_count < 0:
            issues.append(
                CompatibilityIssue(
                    code="invalid-parameter-count",
                    field="metadata.parameter_count",
                    severity="error",
                    message="Parameter count cannot be negative.",
                )
            )

        adapter_recommendation = None
        if any(issue.severity == "error" for issue in issues):
            status = CompatibilityStatus.UNSUPPORTED
            summary = "Attachment metadata is invalid or unsafe for product-mode use."
        elif any(issue.code.startswith("missing-") for issue in issues):
            status = CompatibilityStatus.UNVERIFIED
            summary = "Attachment metadata is incomplete; product-mode compatibility is unverified."
        elif router_dim is not None and expert_dim is not None and router_dim == expert_dim:
            status = CompatibilityStatus.COMPATIBLE
            summary = "Router and expert hidden dimensions match; no adapter is required."
        elif router_dim is not None and expert_dim is not None:
            projection_plan = ExpertAdapterService().projection_plan(
                router_spec={
                    "component_id": "nexus-router",
                    "family": payload.get("router_family", "nexus-router"),
                    "hidden_size": router_dim,
                    "routing_dim": router_dim,
                    "context_window": payload.get("context_window", 4096),
                    "adapter_rank": payload.get("adapter_rank", 8),
                    "component_type": "router",
                },
                expert_spec={
                    "component_id": payload.get("model_name") or payload.get("model_id") or "candidate-expert",
                    "family": payload.get("model_family") or payload.get("architecture"),
                    "hidden_size": expert_dim,
                    "routing_dim": expert_dim,
                    "context_window": payload.get("context_window", 4096),
                    "adapter_rank": payload.get("adapter_rank", 8),
                    "component_type": "expert",
                },
            )
            adapter_recommendation = {
                "status": "passed" if projection_plan.get("compatible") else "failed",
                "adapter_type": "projection",
                "projection_plan": projection_plan,
                "input_shape": [None, expert_dim],
                "output_shape": [None, router_dim],
            }
            if projection_plan.get("compatible"):
                status = CompatibilityStatus.ADAPTER_REQUIRED
                summary = "Router and expert hidden dimensions differ; projection adapter is required."
            else:
                status = CompatibilityStatus.UNSUPPORTED
                issues.append(
                    CompatibilityIssue(
                        code="adapter-roundtrip-failed",
                        severity="error",
                        message="ExpertAdapter could not validate a router-to-expert-to-router roundtrip.",
                    )
                )
                summary = "Adapter validation failed; attachment is unsupported."
        else:
            status = CompatibilityStatus.UNVERIFIED
            summary = "Compatibility cannot be verified from the supplied metadata."

        plan_payload = {
            "status": status.value,
            "summary": summary,
            "issues": [issue.model_dump(mode="json") for issue in issues],
            "model_name": payload.get("model_name") or payload.get("model_id") or payload.get("name"),
            "model_family": payload.get("model_family") or payload.get("architecture"),
            "router_hidden_dim": router_dim,
            "expert_hidden_dim": expert_dim,
            "vocab_size": vocab_size,
            "dtype": payload.get("dtype"),
            "device": payload.get("device"),
            "parameter_count": parameter_count,
            "adapter_recommendation": adapter_recommendation,
        }
        return CompatibilityPlan(
            compatibility_plan_id=self._plan_id(plan_payload),
            status=status,
            ok_for_product_attach=status in {CompatibilityStatus.COMPATIBLE, CompatibilityStatus.ADAPTER_REQUIRED},
            summary=summary,
            issues=issues,
            model_name=plan_payload["model_name"],
            model_family=plan_payload["model_family"],
            router_hidden_dim=router_dim,
            expert_hidden_dim=expert_dim,
            vocab_size=vocab_size,
            dtype=payload.get("dtype"),
            device=payload.get("device"),
            parameter_count=parameter_count,
            adapter_recommendation=adapter_recommendation,
            metadata=payload,
        )

    def _int_value(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _plan_id(self, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return f"attach_compat_{hashlib.sha1(canonical.encode('utf-8')).hexdigest()[:12]}"
