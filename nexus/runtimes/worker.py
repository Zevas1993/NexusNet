from __future__ import annotations

from collections.abc import Mapping
import hashlib
import re
from typing import Any

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, RuntimePackManifest
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError

from ..schemas import Message
from .base import RuntimeAdapter, prompt_from_messages


_SAFE_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
_SAFE_REASON = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_MAX_MODEL_ID_CHARACTERS = 1024 * 1024
_MAX_EXPERT_CHARACTERS = 256


def _safe_reason(reason_code: object, fallback: str) -> str:
    if type(reason_code) is str and _SAFE_REASON.fullmatch(reason_code):
        return reason_code
    return fallback


def _plain_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return value


class RuntimeExecutionError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = _safe_reason(reason_code, "runtime-execution-failed")
        super().__init__(self.reason_code)


class WorkerRuntimeAdapter(RuntimeAdapter):
    runtime_name = "accelerator-pack"
    backend_type = "managed-worker"

    def __init__(self, *, manifest: RuntimePackManifest, supervisor: WorkerSupervisor):
        super().__init__({"pack_id": manifest.pack_id, "pack_version": manifest.version})
        self.manifest = manifest
        self.supervisor = supervisor

    @staticmethod
    def _sanitized_model_ref(model_id: str) -> str:
        if type(model_id) is not str or not model_id or len(model_id) > _MAX_MODEL_ID_CHARACTERS:
            raise RuntimeExecutionError("model-id-invalid")
        try:
            digest = hashlib.sha256(model_id.encode("utf-8")).hexdigest()[:24]
        except UnicodeError:
            raise RuntimeExecutionError("model-id-invalid") from None
        return f"model::{digest}"

    def _execution_context(self, metadata: dict[str, Any] | None) -> tuple[ExecutionMode, str]:
        if metadata is None:
            admitted_metadata: dict[str, Any] = {}
        elif type(metadata) is dict:
            admitted_metadata = metadata
        else:
            raise RuntimeExecutionError("runtime-metadata-invalid")

        raw_mode = admitted_metadata.get("execution_mode", "auto")
        if isinstance(raw_mode, ExecutionMode):
            mode = raw_mode
        elif type(raw_mode) is str:
            normalized_mode = raw_mode.casefold()
            if normalized_mode == "both":
                normalized_mode = ExecutionMode.HYBRID.value
            try:
                mode = ExecutionMode(normalized_mode)
            except ValueError:
                raise RuntimeExecutionError("execution-mode-invalid") from None
        else:
            raise RuntimeExecutionError("execution-mode-invalid")

        if mode is not ExecutionMode.AUTO and mode not in self.manifest.execution_modes:
            raise RuntimeExecutionError("execution-mode-unsupported")

        policy_receipt_ref = admitted_metadata.get(
            "policy_receipt_ref",
            "receipt::runtime-generate",
        )
        if type(policy_receipt_ref) is not str or not _SAFE_REFERENCE.fullmatch(policy_receipt_ref):
            raise RuntimeExecutionError("policy-receipt-ref-invalid")
        return mode, policy_receipt_ref

    def _unavailable_health(self, reason_code: object) -> dict[str, Any]:
        return {
            "available": False,
            "pack_id": self.manifest.pack_id,
            "pack_version": self.manifest.version,
            "reason_codes": [_safe_reason(reason_code, "worker-health-failed")],
            "capabilities": {},
            "metrics": {},
        }

    def health(self) -> dict[str, Any]:
        try:
            frames = self.supervisor.request(
                WorkerOperation.HEALTH,
                sanitized_model_ref="model::none",
                execution_mode=ExecutionMode.AUTO,
                policy_receipt_ref="receipt::runtime-health",
            )
        except WorkerSupervisorError as error:
            return self._unavailable_health(error.reason_code)

        if not frames:
            return self._unavailable_health("worker-health-invalid")
        result = frames[-1]
        if result.event == "error":
            return self._unavailable_health(result.reason_code)
        available = result.payload.get("available", False)
        reported_capabilities = result.payload.get("capabilities", {})
        if type(available) is not bool or not isinstance(reported_capabilities, Mapping):
            return self._unavailable_health("worker-health-invalid")
        return {
            "available": available,
            "pack_id": self.manifest.pack_id,
            "pack_version": self.manifest.version,
            "reason_codes": [],
            "capabilities": {
                "declared": list(self.manifest.capabilities),
                "reported": _plain_json(reported_capabilities),
            },
            "metrics": {},
        }

    def generate(
        self,
        *,
        prompt: str | None,
        messages: list[Message],
        model_id: str,
        expert: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        mode, policy_receipt_ref = self._execution_context(metadata)
        sanitized_model_ref = self._sanitized_model_ref(model_id)
        if expert is not None and (type(expert) is not str or len(expert) > _MAX_EXPERT_CHARACTERS):
            raise RuntimeExecutionError("expert-invalid")
        try:
            admitted_prompt = prompt_from_messages(messages, prompt)
            payload: dict[str, object] = {"prompt": admitted_prompt}
            if expert is not None:
                payload["expert"] = expert
            frames = self.supervisor.request(
                WorkerOperation.INFER,
                sanitized_model_ref=sanitized_model_ref,
                execution_mode=mode,
                policy_receipt_ref=policy_receipt_ref,
                payload=payload,
            )
        except WorkerSupervisorError as error:
            raise RuntimeExecutionError(_safe_reason(error.reason_code, "worker-inference-failed")) from None
        except RuntimeExecutionError:
            raise
        except Exception:
            raise RuntimeExecutionError("worker-request-invalid") from None

        if not frames:
            raise RuntimeExecutionError("worker-result-invalid")
        result = frames[-1]
        if result.event == "error":
            raise RuntimeExecutionError(_safe_reason(result.reason_code, "worker-inference-failed"))
        text = result.payload.get("text")
        if type(text) is not str:
            raise RuntimeExecutionError("worker-result-invalid")
        return text
