from __future__ import annotations

from abc import ABC, abstractmethod
from contextvars import ContextVar
import hashlib
import json
from typing import Any

from nexusnet.runtime.evolutionary_inference.schemas import (
    InferenceMethodRecord,
    RuntimeCapabilityProfile,
    RuntimeControlBinding,
    RuntimeControlReceipt,
)

from ..schemas import Message, RuntimeProfile


def prompt_from_messages(messages: list[Message], prompt: str | None = None) -> str:
    if prompt:
        return prompt
    if not messages:
        return ""
    parts = []
    for message in messages:
        parts.append(f"{message.role.upper()}: {message.content}")
    return "\n".join(parts)


class RuntimeAdapter(ABC):
    runtime_name = "runtime"
    backend_type = "abstract"
    supported_runtime_controls: frozenset[str] = frozenset()
    observable_runtime_controls: frozenset[str] = frozenset()

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._control_binding_context: ContextVar[RuntimeControlReceipt | None] = ContextVar(
            f"runtime-control-binding::{self.runtime_name}::{id(self)}",
            default=None,
        )

    @abstractmethod
    def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str | None,
        messages: list[Message],
        model_id: str,
        expert: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError

    def profile(self) -> RuntimeProfile:
        health = self.health()
        return RuntimeProfile(
            runtime_name=self.runtime_name,
            backend_type=self.backend_type,
            available=bool(health.get("available", False)),
            health=health,
            capabilities=health.get("capabilities", {}),
            metrics=health.get("metrics", {}),
        )

    def runtime_capability_profile(self) -> RuntimeCapabilityProfile:
        supported = sorted(self.supported_runtime_controls)
        observable = sorted(self.observable_runtime_controls)
        identity = json.dumps(
            {
                "adapter": f"{self.__class__.__module__}.{self.__class__.__qualname__}",
                "runtime_name": self.runtime_name,
                "supported_controls": supported,
                "observable_controls": observable,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return RuntimeCapabilityProfile(
            runtime_name=self.runtime_name,
            runtime_version=str(self.config.get("runtime_version") or "adapter-contract-v1"),
            implementation_digest=f"sha256:{hashlib.sha256(identity.encode('utf-8')).hexdigest()}",
            capability_state="verified",
            supported_controls=supported,
            observable_controls=observable,
        )

    def inference_method_record(self) -> InferenceMethodRecord:
        capability_profile = self.runtime_capability_profile()
        configured_rights = self.config.get("rights")
        rights = (
            dict(configured_rights)
            if isinstance(configured_rights, dict)
            else {
                "inference": "allowed",
                "evaluation": "allowed",
                "derivative": "unknown",
                "redistribution": "unknown",
            }
        )
        return InferenceMethodRecord(
            method_id=f"runtime::{self.runtime_name}",
            version=capability_profile.runtime_version,
            source_kind="external-engine",
            source_digest=capability_profile.implementation_digest,
            rights=rights,
            supported_model_families=[str(item) for item in self.config.get("model_families", [])],
            supported_operator_families=[str(item) for item in self.config.get("operator_families", [])],
            supported_formats=[str(item) for item in self.config.get("formats", [])],
            supported_precisions=[str(item) for item in self.config.get("precisions", [])],
            supported_hardware=[str(item) for item in self.config.get("hardware", [])],
            tunable_controls=capability_profile.supported_controls,
            maturity="adapted",
            assimilation_paths=["whole-engine"],
        )

    def bind_runtime_controls(self, metadata: dict[str, Any] | None) -> RuntimeControlReceipt:
        selection = (metadata or {}).get("evolutionary_inference")
        if not isinstance(selection, dict):
            return self._store_control_binding(
                plan_id="plan::runtime-default",
                decision="admitted",
                bound_parameters={},
                bindings=[],
                reason_codes=["runtime-default-controls"],
            )
        plan_id = str(selection.get("plan_id") or "plan::runtime-default")
        fit_receipts = selection.get("execution_fit_receipts")
        fit_receipt = (
            fit_receipts.get(self.runtime_name)
            if isinstance(fit_receipts, dict)
            else selection.get("execution_fit_receipt")
        )
        if selection.get("fit_required") is True and not isinstance(fit_receipt, dict):
            return self._store_control_binding(
                plan_id=plan_id,
                decision="rejected",
                bound_parameters={},
                bindings=[],
                reason_codes=["execution-fit-receipt-missing"],
            )
        fit_degraded = False
        if isinstance(fit_receipt, dict):
            fit_plan_id = str(fit_receipt.get("plan_id") or "")
            fit_decision = str(fit_receipt.get("decision") or "")
            if fit_plan_id != plan_id:
                return self._store_control_binding(
                    plan_id=plan_id,
                    decision="rejected",
                    bound_parameters={},
                    bindings=[],
                    reason_codes=["execution-fit-plan-mismatch"],
                )
            fit_runtime_name = str(fit_receipt.get("runtime_name") or "")
            if fit_runtime_name and fit_runtime_name != self.runtime_name:
                return self._store_control_binding(
                    plan_id=plan_id,
                    decision="rejected",
                    bound_parameters={},
                    bindings=[],
                    reason_codes=["execution-fit-runtime-mismatch"],
                )
            if fit_decision == "rejected":
                return self._store_control_binding(
                    plan_id=plan_id,
                    decision="rejected",
                    bound_parameters={},
                    bindings=[],
                    reason_codes=["execution-fit-rejected"],
                )
            fit_degraded = fit_decision == "degraded"
        if selection.get("verified") is not True:
            return self._store_control_binding(
                plan_id=plan_id,
                decision="degraded",
                bound_parameters={},
                bindings=[],
                reason_codes=["plan-unverified"],
            )

        raw_parameters = selection.get("parameters")
        parameters = dict(raw_parameters) if isinstance(raw_parameters, dict) else {}
        if isinstance(fit_receipt, dict) and isinstance(fit_receipt.get("control_bindings"), list):
            fitted_values: dict[str, int | float | str | bool] = {}
            fitted_controls = {
                str(binding.get("control"))
                for binding in fit_receipt["control_bindings"]
                if isinstance(binding, dict) and binding.get("control")
            }
            for binding in fit_receipt["control_bindings"]:
                if not isinstance(binding, dict) or not binding.get("control"):
                    continue
                applied_value = binding.get("applied_value")
                if isinstance(applied_value, (bool, int, float, str)):
                    fitted_values[str(binding["control"])] = applied_value
            parameters = {
                control: fitted_values.get(control, value)
                for control, value in parameters.items()
                if control in fitted_controls
            }
        required_controls = {
            str(control) for control in selection.get("required_controls", []) if str(control)
        }
        bindings: list[RuntimeControlBinding] = []
        bound_parameters: dict[str, int | float | str | bool] = {}
        required_unsupported = False
        optional_unsupported = False
        unverified_binding = False

        for control, raw_value in sorted(parameters.items()):
            if not isinstance(raw_value, (bool, int, float, str)):
                status = "rejected" if control in required_controls else "unsupported"
                reason_code = "runtime-control-value-invalid"
                value: int | float | str | bool = str(type(raw_value).__name__)
                if control in required_controls:
                    required_unsupported = True
                else:
                    optional_unsupported = True
                applied_value = None
            elif control not in self.supported_runtime_controls:
                status = "rejected" if control in required_controls else "unsupported"
                reason_code = "runtime-control-unsupported"
                value = raw_value
                if control in required_controls:
                    required_unsupported = True
                else:
                    optional_unsupported = True
                applied_value = None
            elif control not in self.observable_runtime_controls:
                status = "degraded"
                reason_code = "runtime-control-binding-unverified"
                value = raw_value
                applied_value = raw_value
                bound_parameters[control] = raw_value
                unverified_binding = True
            else:
                status = "applied"
                reason_code = "runtime-control-binding-verified"
                value = raw_value
                applied_value = raw_value
                bound_parameters[control] = raw_value
            bindings.append(
                RuntimeControlBinding(
                    control=control,
                    requested_value=value,
                    applied_value=applied_value,
                    status=status,
                    reason_code=reason_code,
                )
            )

        missing_required = required_controls - set(parameters)
        reason_codes: list[str] = []
        if required_unsupported or missing_required:
            decision = "rejected"
            reason_codes.append("required-control-unsupported")
        elif optional_unsupported or unverified_binding or fit_degraded:
            decision = "degraded"
            if optional_unsupported:
                reason_codes.append("optional-control-unsupported")
            if unverified_binding:
                reason_codes.append("control-binding-unverified")
            if fit_degraded:
                reason_codes.append("execution-fit-degraded")
        else:
            decision = "admitted"
            reason_codes.append("runtime-controls-bound")
        return self._store_control_binding(
            plan_id=plan_id,
            decision=decision,
            bound_parameters=bound_parameters,
            bindings=bindings,
            reason_codes=reason_codes,
        )

    def verified_runtime_parameters(self, metadata: dict[str, Any] | None) -> dict[str, Any]:
        receipt = self.bind_runtime_controls(metadata)
        if receipt.decision == "rejected":
            if "execution-fit-rejected" in receipt.reason_codes:
                raise RuntimeError("execution fit rejected")
            if "execution-fit-receipt-missing" in receipt.reason_codes:
                raise RuntimeError("execution fit receipt missing")
            if "execution-fit-plan-mismatch" in receipt.reason_codes:
                raise RuntimeError("execution fit plan mismatch")
            if "execution-fit-runtime-mismatch" in receipt.reason_codes:
                raise RuntimeError("execution fit runtime mismatch")
            raise RuntimeError("required runtime controls unsupported")
        return dict(receipt.bound_parameters)

    def control_binding_status(self) -> RuntimeControlReceipt | None:
        return self._control_binding_context.get()

    def _store_control_binding(
        self,
        *,
        plan_id: str,
        decision: str,
        bound_parameters: dict[str, int | float | str | bool],
        bindings: list[RuntimeControlBinding],
        reason_codes: list[str],
    ) -> RuntimeControlReceipt:
        payload = {
            "runtime_name": self.runtime_name,
            "plan_id": plan_id,
            "decision": decision,
            "bound_parameters": bound_parameters,
            "bindings": [binding.model_dump(mode="json") for binding in bindings],
            "reason_codes": reason_codes,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:24]
        receipt = RuntimeControlReceipt(
            binding_id=f"runtime-binding::{digest}",
            runtime_name=self.runtime_name,
            plan_id=plan_id,
            decision=decision,
            bound_parameters=bound_parameters,
            bindings=bindings,
            reason_codes=reason_codes,
        )
        self._control_binding_context.set(receipt)
        return receipt

