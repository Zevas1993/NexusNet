from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictStr, field_validator

from .contracts import ExecutionMode, ModelFormat, WorkloadKind


_PUBLIC_TO_EXECUTION_MODE = {
    "Auto": ExecutionMode.AUTO,
    "CPU": ExecutionMode.CPU,
    "GPU": ExecutionMode.GPU,
    "Both": ExecutionMode.HYBRID,
}
_EXECUTION_TO_PUBLIC_MODE = {value: key for key, value in _PUBLIC_TO_EXECUTION_MODE.items()}


class RouteUnavailableError(RuntimeError):
    """Raised when the requested execution mode has no verified live route."""


class RouteEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    route_id: StrictStr = Field(min_length=1)
    pack_id: StrictStr = Field(min_length=1)
    pack_version: StrictStr = Field(min_length=1)
    device_node_id: StrictStr = Field(min_length=1)
    device_kind: Literal["cpu", "gpu"]
    execution_modes: tuple[ExecutionMode, ...] = Field(min_length=1)
    verified: StrictBool
    healthy: StrictBool
    correctness_passed: StrictBool
    quarantined: StrictBool = False
    hybrid_offload_verified: StrictBool = False
    calibration_score: StrictFloat | None = None
    evidence_refs: tuple[StrictStr, ...] = Field(min_length=1)

    @field_validator("route_id", "pack_id", "pack_version", "device_node_id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if value != value.strip() or any(ord(character) < 32 for character in value):
            raise ValueError("route identifiers must be sanitized")
        return value

    @field_validator("evidence_refs")
    @classmethod
    def validate_evidence_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item or item != item.strip() or any(ord(character) < 32 for character in item) for item in value):
            raise ValueError("evidence references must be sanitized")
        return value


class RouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_mode: ExecutionMode = ExecutionMode.AUTO
    workload: WorkloadKind = WorkloadKind.LLM_GENERATE
    model_format: ModelFormat = ModelFormat.TORCH


class RouteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    route_id: StrictStr | None = None
    execution_mode: ExecutionMode
    available: StrictBool
    reason_codes: tuple[StrictStr, ...] = ()
    evidence_refs: tuple[StrictStr, ...] = ()


class VerifiedRouteSelector:
    """Select only routes backed by verification, correctness, and health evidence."""

    def __init__(self, evidence: list[RouteEvidence] | tuple[RouteEvidence, ...] = ()):
        self._lock = RLock()
        self._evidence: dict[str, RouteEvidence] = {}
        self.replace(evidence)

    def replace(self, evidence: list[RouteEvidence] | tuple[RouteEvidence, ...]) -> None:
        with self._lock:
            self._evidence = {item.route_id: item for item in evidence}

    def register(self, evidence: RouteEvidence) -> None:
        with self._lock:
            self._evidence[evidence.route_id] = evidence

    def routes(self) -> tuple[RouteEvidence, ...]:
        with self._lock:
            return tuple(sorted(self._evidence.values(), key=lambda item: item.route_id))

    def select(self, request: RouteRequest) -> RouteDecision:
        eligible = [
            item
            for item in self.routes()
            if item.verified and item.healthy and item.correctness_passed and not item.quarantined
        ]
        requested_mode = request.execution_mode
        if requested_mode is ExecutionMode.HYBRID:
            candidates = [
                item
                for item in eligible
                if ExecutionMode.HYBRID in item.execution_modes and item.hybrid_offload_verified
            ]
            return self._decision(candidates, requested_mode, "hybrid-route-verified", "hybrid-route-unverified")
        if requested_mode is ExecutionMode.CPU:
            candidates = [
                item for item in eligible if item.device_kind == "cpu" and ExecutionMode.CPU in item.execution_modes
            ]
            return self._decision(candidates, requested_mode, "cpu-route-verified", "cpu-route-unavailable")
        if requested_mode is ExecutionMode.GPU:
            candidates = [
                item for item in eligible if item.device_kind == "gpu" and ExecutionMode.GPU in item.execution_modes
            ]
            return self._decision(candidates, requested_mode, "accelerator-route-verified", "accelerator-route-unavailable")

        candidates = [
            item
            for item in eligible
            if (item.device_kind == "cpu" and ExecutionMode.CPU in item.execution_modes)
            or (item.device_kind == "gpu" and ExecutionMode.GPU in item.execution_modes)
        ]
        return self._decision(candidates, requested_mode, "auto-best-verified-route", "no-verified-route")

    @staticmethod
    def _decision(
        candidates: list[RouteEvidence],
        mode: ExecutionMode,
        available_reason: str,
        unavailable_reason: str,
    ) -> RouteDecision:
        if not candidates:
            return RouteDecision(execution_mode=mode, available=False, reason_codes=(unavailable_reason,))
        selected = max(
            candidates,
            key=lambda item: (
                item.calibration_score if item.calibration_score is not None else 0.0,
                item.device_kind == "cpu",
                item.route_id,
            ),
        )
        return RouteDecision(
            route_id=selected.route_id,
            execution_mode=mode,
            available=True,
            reason_codes=(available_reason,),
            evidence_refs=selected.evidence_refs,
        )


class RuntimeModeStore:
    """Persist the operator's Auto/CPU/GPU/Both preference with atomic replacement."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = RLock()

    def status(self) -> dict[str, str]:
        with self._lock:
            mode = "Auto"
            if self.path.exists():
                try:
                    payload = json.loads(self.path.read_text(encoding="utf-8"))
                    candidate = payload.get("requested_mode") if isinstance(payload, dict) else None
                    if candidate in _PUBLIC_TO_EXECUTION_MODE:
                        mode = candidate
                except (OSError, UnicodeError, json.JSONDecodeError):
                    mode = "Auto"
            return {"requested_mode": mode, "execution_mode": _PUBLIC_TO_EXECUTION_MODE[mode].value}

    def set_mode(self, requested_mode: str) -> dict[str, str]:
        if not isinstance(requested_mode, str) or requested_mode not in _PUBLIC_TO_EXECUTION_MODE:
            raise ValueError("mode must be one of Auto, CPU, GPU, or Both")
        payload = {
            "requested_mode": requested_mode,
            "execution_mode": _PUBLIC_TO_EXECUTION_MODE[requested_mode].value,
        }
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            try:
                temporary.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
                os.replace(temporary, self.path)
            finally:
                temporary.unlink(missing_ok=True)
        return payload


def normalize_execution_mode(value: str | ExecutionMode) -> ExecutionMode:
    if isinstance(value, ExecutionMode):
        return value
    if value in _PUBLIC_TO_EXECUTION_MODE:
        return _PUBLIC_TO_EXECUTION_MODE[value]
    try:
        return ExecutionMode(value.lower())
    except (AttributeError, ValueError) as exc:
        raise ValueError("mode must be one of Auto, CPU, GPU, or Both") from exc


def public_execution_mode(value: ExecutionMode) -> str:
    return _EXECUTION_TO_PUBLIC_MODE[value]
