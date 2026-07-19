from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_ref(value: Any, *, prefix: str) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    if (
        raw
        and len(raw) <= 160
        and ".." not in raw
        and ":/" not in raw
        and not raw.startswith("/")
        and all(char.isalnum() or char in "-_:/.@" for char in raw)
    ):
        return raw
    return f"{prefix}::{_digest(raw)[:16]}"


class ModelAttachInferenceHarness:
    """Evidence-gated model attachment and inference receipts for Layer 11."""

    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        root = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = root / "runtime" / "model-attach-inference-harness" if root is not None else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._routes: dict[str, dict[str, Any]] = {}
        self._attachments: dict[str, dict[str, Any]] = {}
        self._attempts: dict[str, list[dict[str, Any]]] = {}
        self._outputs: dict[str, dict[str, Any]] = {}

    def open_route(
        self,
        *,
        trace_id: str,
        session_id: str,
        registration: Any,
        requested_runtime: str,
        runtime_ladder: list[str],
        task_type: str,
        hardware_posture: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_trace_id = _safe_ref(trace_id, prefix="trace")
        model_id = _safe_ref(registration.model_id, prefix="model")
        route = {
            "route_id": f"model-route::{_digest(f'{safe_trace_id}:{model_id}:{requested_runtime}')[:20]}",
            "trace_id": safe_trace_id,
            "session_ref": f"session::{_digest(str(session_id))[:16]}",
            "authority": "NexusBrain",
            "status": "open-inference-route",
            "requested_model_id": model_id,
            "requested_runtime": _safe_ref(requested_runtime, prefix="runtime"),
            "runtime_ladder": [_safe_ref(item, prefix="runtime") for item in runtime_ladder],
            "task_type": _safe_ref(task_type, prefix="task"),
            "context_hardware_posture_ref": self._hardware_posture(hardware_posture or {}),
            "raw_content_included": False,
            "opened_at": _utcnow_iso(),
        }
        self._routes[safe_trace_id] = route
        self._persist(safe_trace_id)
        return dict(route)

    def authorize_attach(
        self,
        *,
        trace_id: str,
        registration: Any,
        runtime_name: str,
        requested_role: str,
        runtime_ladder: list[str],
        runtime_profile: Any,
        hardware_posture: dict[str, Any] | None = None,
        runtime_decision: dict[str, Any] | None = None,
        compatibility_provenance: dict[str, Any] | None = None,
        usage_intent: str = "inference",
        teacher_rights_attestation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_trace_id = _safe_ref(trace_id, prefix="trace")
        metadata = dict(registration.metadata or {})
        license_status = str(metadata.get("license_status") or "needs-review").lower().replace("_", "-")
        inference_allowed = bool(metadata.get("inference_use_authorized", license_status != "blocked"))
        rights_refs = [
            _safe_ref(item, prefix="rights")
            for item in metadata.get("rights_refs", [])
            if str(item).strip()
        ]
        training_allowed = bool(metadata.get("training_use_authorized")) and license_status == "approved" and bool(rights_refs)
        teacher_allowed = (
            bool(metadata.get("teacher_or_distillation_use_authorized"))
            and license_status == "approved"
            and bool(rights_refs)
        )
        attestation = dict(teacher_rights_attestation or {})
        attested_teacher_allowed = attestation.get("teacher_or_distillation_use_authorized") is True
        attested_rights_refs = [
            _safe_ref(item, prefix="rights")
            for item in attestation.get("rights_refs", [])
            if str(item).strip()
        ]
        teacher_allowed = teacher_allowed or (attested_teacher_allowed and bool(attested_rights_refs))
        effective_usage = "teacher-or-distillation" if usage_intent == "teacher-or-distillation" else "inference-tool"
        if not inference_allowed:
            raise PermissionError("model/provider attach blocked because inference rights are not authorized")
        if usage_intent == "teacher-or-distillation" and not teacher_allowed:
            raise PermissionError("model/provider attach blocked because teacher or distillation rights are not authorized")

        capability = registration.capability_card.model_dump(mode="json")
        profile = runtime_profile.model_dump(mode="json") if hasattr(runtime_profile, "model_dump") else dict(runtime_profile or {})
        context_tokens = int(capability.get("context_window") or 0)
        quantizations = [str(item) for item in capability.get("quantization", []) if str(item).strip()]
        model_id = _safe_ref(registration.model_id, prefix="model")
        safe_runtime = _safe_ref(runtime_name, prefix="runtime")
        route = self._routes.get(safe_trace_id)
        if route is None:
            route = {
                "route_id": f"model-route::{_digest(f'{safe_trace_id}:{model_id}:{safe_runtime}')[:20]}",
                "trace_id": safe_trace_id,
                "authority": "NexusBrain",
                "status": "implicit-attach-route",
                "requested_model_id": model_id,
                "requested_runtime": safe_runtime,
                "runtime_ladder": [_safe_ref(item, prefix="runtime") for item in runtime_ladder],
                "raw_content_included": False,
                "opened_at": _utcnow_iso(),
            }
            self._routes[safe_trace_id] = route

        hardware = self._hardware_posture(
            hardware_posture or (runtime_decision or {}).get("hardware_profile") or {}
        )
        contract = {
            "contract_id": f"model-attach::{_digest(f'{safe_trace_id}:{model_id}:{safe_runtime}')[:20]}",
            "route_id": route["route_id"],
            "trace_id": safe_trace_id,
            "authority": "NexusBrain",
            "status": (
                "authorized-teacher-or-distillation"
                if usage_intent == "teacher-or-distillation"
                else "authorized-inference-only"
            ),
            "model_provider_contract": {
                "model_id": model_id,
                "runtime_name": safe_runtime,
                "requested_role": _safe_ref(requested_role, prefix="role"),
                "effective_usage": effective_usage,
                "brain_replacement_allowed": False,
            },
            "provider_capability_passport": {
                "passport_id": f"provider-passport::{_digest(safe_runtime)[:16]}",
                "runtime_name": safe_runtime,
                "backend_type": _safe_ref(profile.get("backend_type"), prefix="backend"),
                "available": bool(profile.get("available", True)),
                "capability_keys": sorted(str(key) for key in dict(profile.get("capabilities") or {}).keys()),
            },
            "runtime_ladder": [_safe_ref(item, prefix="runtime") for item in runtime_ladder],
            "model_passport": {
                "passport_id": f"model-passport::{_digest(model_id)[:16]}",
                "model_id": model_id,
                "model_family": _safe_ref(capability.get("model_family"), prefix="family"),
                "modalities": [_safe_ref(item, prefix="modality") for item in capability.get("modalities", [])],
                "context_tokens": context_tokens,
                "runtime_formats": [safe_runtime],
                "allowed_tasks": [_safe_ref(item, prefix="task") for item in capability.get("preferred_tasks", [])],
                "blocked_task_count": len(capability.get("known_weaknesses", [])),
                "license_status": license_status,
                "rights_refs": list(dict.fromkeys([*rights_refs, *attested_rights_refs])),
            },
            "quantization_profile": {
                "profile": quantizations[0] if quantizations else "unquantized-or-runtime-managed",
                "supported_profiles": quantizations,
                "runtime_managed": not bool(quantizations),
            },
            "context_hardware_posture": {
                **hardware,
                "context_tokens": context_tokens,
            },
            "rights_gate": {
                "license_status": license_status,
                "inference_use_authorized": True,
                "training_use_authorized": training_allowed,
                "teacher_or_distillation_use_authorized": teacher_allowed,
                "teacher_use_authorization_ref": _safe_ref(attestation.get("authorization_id"), prefix="authorization"),
                "boundary": "inference-only-no-training-or-teacher-use"
                if not training_allowed and not teacher_allowed
                else "explicit-rights-required-per-use",
            },
            "compatibility_evidence": {
                "plan_id": _safe_ref((compatibility_provenance or {}).get("compatibility_plan_id"), prefix="compatibility"),
                "status": _safe_ref((compatibility_provenance or {}).get("compatibility_status"), prefix="status"),
                "product_evidence": (compatibility_provenance or {}).get("product_evidence") is True,
            },
            "raw_content_included": False,
            "authorized_at": _utcnow_iso(),
        }
        self._attachments[safe_trace_id] = contract
        self._persist(safe_trace_id)
        return dict(contract)

    def record_attempt(
        self,
        *,
        trace_id: str,
        runtime_name: str,
        status: str,
        reason_code: str,
    ) -> dict[str, Any]:
        safe_trace_id = _safe_ref(trace_id, prefix="trace")
        receipt = {
            "attempt_id": f"runtime-attempt::{_digest(f'{safe_trace_id}:{runtime_name}:{len(self._attempts.get(safe_trace_id, []))}')[:20]}",
            "runtime_name": _safe_ref(runtime_name, prefix="runtime"),
            "status": _safe_ref(status, prefix="status"),
            "reason_code": _safe_ref(reason_code, prefix="reason"),
            "raw_error_included": False,
            "recorded_at": _utcnow_iso(),
        }
        self._attempts.setdefault(safe_trace_id, []).append(receipt)
        self._persist(safe_trace_id)
        return dict(receipt)

    def record_output(
        self,
        *,
        trace_id: str,
        output: str,
        latency_ms: int,
        requested_model_id: str,
        requested_runtime: str,
        served_model_id: str,
        served_runtime: str,
        fallback_used: bool,
        fallback_reason_code: str | None = None,
    ) -> dict[str, Any]:
        safe_trace_id = _safe_ref(trace_id, prefix="trace")
        packet = {
            "packet_id": f"model-output::{_digest(f'{safe_trace_id}:{served_model_id}:{served_runtime}:{len(output)}')[:20]}",
            "trace_id": safe_trace_id,
            "status": "served",
            "output_sha256": _digest(output),
            "output_chars": len(output),
            "latency_ms": max(0, int(latency_ms)),
            "raw_output_included": False,
            "attempt_receipts": list(self._attempts.get(safe_trace_id, [])),
            "fallback_containment": {
                "fallback_used": bool(fallback_used),
                "requested_model_id": _safe_ref(requested_model_id, prefix="model"),
                "requested_runtime": _safe_ref(requested_runtime, prefix="runtime"),
                "served_model_id": _safe_ref(served_model_id, prefix="model"),
                "served_runtime": _safe_ref(served_runtime, prefix="runtime"),
                "reason_code": _safe_ref(fallback_reason_code, prefix="fallback") if fallback_used else None,
                "contained": True,
                "promotion_authority_granted": False,
            },
            "recorded_at": _utcnow_iso(),
        }
        self._outputs[safe_trace_id] = packet
        self._persist(safe_trace_id)
        return dict(packet)

    def receipt(self, *, trace_id: str) -> dict[str, Any]:
        safe_trace_id = _safe_ref(trace_id, prefix="trace")
        output = self._outputs.get(safe_trace_id)
        return {
            "status": "evidence-recorded" if output is not None else "route-open",
            "authority": "NexusBrain",
            "surface_id": "model-attach-inference-harness",
            "route_envelope": dict(self._routes.get(safe_trace_id) or {}),
            "attach_contract": dict(self._attachments.get(safe_trace_id) or {}),
            "output_evidence": dict(output or {}),
            "mutation_boundary": "inference-evidence-only-no-training-no-promotion",
        }

    def summary(self, *, trace_id: str | None = None) -> dict[str, Any]:
        if trace_id is not None:
            return self.receipt(trace_id=trace_id)
        return {
            "status_label": "LIVE EVIDENCE",
            "authority": "NexusBrain",
            "surface_id": "model-attach-inference-harness",
            "route_count": len(self._routes),
            "attachment_count": len(self._attachments),
            "output_evidence_count": len(self._outputs),
            "latest_receipts": [self.receipt(trace_id=trace_id) for trace_id in list(self._routes)[-10:]],
            "mutation_boundary": "inference-evidence-only-no-training-no-promotion",
        }

    def _hardware_posture(self, payload: dict[str, Any]) -> dict[str, Any]:
        numeric_keys = (
            "max_context_tokens",
            "memory_budget_mb",
            "system_memory_gb",
            "gpu_memory_gb",
            "cpu_count",
        )
        posture = {
            key: payload[key]
            for key in numeric_keys
            if key in payload and isinstance(payload[key], (int, float))
        }
        posture["profile_ref"] = f"hardware::{_digest(json.dumps(posture, sort_keys=True))[:16]}"
        posture["raw_hardware_details_included"] = False
        return posture

    def _persist(self, trace_id: str) -> None:
        if self.records_dir is None:
            return
        name = _digest(trace_id)[:24]
        path = self.records_dir / f"trace_{name}.json"
        path.write_text(json.dumps(self.receipt(trace_id=trace_id), indent=2, sort_keys=True), encoding="utf-8")
