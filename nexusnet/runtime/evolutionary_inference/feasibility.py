from __future__ import annotations

import hashlib
import json

from .primitives import InferencePrimitiveRegistry
from .schemas import (
    CandidateFeasibility,
    ExecutionFitReconciliation,
    ExecutionFitReceipt,
    ExecutionFitRequest,
    FeasibilityCandidate,
    HardwareCapabilityGraph,
    ModelExecutionFingerprint,
    RuntimeControlBinding,
    RuntimeObservation,
)


class ExecutionFitEstimator:
    def evaluate(self, request: ExecutionFitRequest) -> ExecutionFitReceipt:
        fingerprint = request.model_fingerprint
        control_bindings = self._bind_controls(request)
        ram_bytes = max(
            (node.memory_bytes or 0 for node in request.hardware.nodes if node.kind == "system-ram"),
            default=0,
        )
        vram_bytes = self._usable_vram_bytes(request, control_bindings)
        expert_weight_bytes = sum(
            group.bytes for group in fingerprint.tensor_groups if "expert" in group.group_id.lower()
        )
        dense_weight_bytes = max(0, fingerprint.tensor_bytes - expert_weight_bytes)
        active_expert_bytes = 0
        if fingerprint.expert_count > 0 and fingerprint.experts_per_token > 0:
            active_expert_bytes = int(
                expert_weight_bytes * fingerprint.experts_per_token / fingerprint.expert_count
            )

        kv_bytes_per_token = int(fingerprint.state_and_kv_contract.get("bytes_per_token", 0) or 0)
        requested_total_tokens = request.requested_context_tokens
        kv_multiplier = request.batch_size * request.concurrent_requests
        kv_cache_bytes = requested_total_tokens * kv_bytes_per_token * kv_multiplier
        requested_working_bytes = fingerprint.tensor_bytes + kv_cache_bytes + request.runtime_buffer_bytes
        headroom_bytes = int(requested_working_bytes * request.safety_headroom_ratio)

        reason_codes: list[str] = []
        unsupported_required = sorted(
            binding.control
            for binding in control_bindings
            if binding.control in request.required_controls and binding.status != "applied"
        )
        missing_required = sorted(
            binding.control
            for binding in control_bindings
            if binding.reason_code == "runtime-control-required-value-missing"
        )
        unsupported_optional = sorted(
            binding.control
            for binding in control_bindings
            if binding.control not in request.required_controls and binding.status != "applied"
        )
        if missing_required:
            reason_codes.append("required-control-missing")
        if set(unsupported_required) - set(missing_required):
            reason_codes.append("required-control-unsupported")
        if unsupported_optional:
            reason_codes.append("optional-control-unsupported")

        placement: dict[str, str] = {
            "dense": "unplaced",
            "experts": "unplaced" if expert_weight_bytes else "ram",
            "kv-cache": "unplaced",
            "runtime-buffers": "unplaced",
        }
        peak_ram_bytes = 0
        peak_vram_bytes = 0
        safe_context_tokens = 0
        capacity_reason: str | None = None

        if kv_bytes_per_token <= 0:
            capacity_reason = "kv-metadata-missing"
        elif requested_working_bytes + headroom_bytes <= vram_bytes:
            placement.update({"dense": "gpu", "experts": "gpu", "kv-cache": "gpu", "runtime-buffers": "gpu"})
            peak_vram_bytes = requested_working_bytes + headroom_bytes
            safe_context_tokens = min(
                fingerprint.context_length,
                self._safe_context(
                    capacity_bytes=vram_bytes,
                    fixed_bytes=fingerprint.tensor_bytes + request.runtime_buffer_bytes,
                    request=request,
                    kv_bytes_per_token=kv_bytes_per_token,
                ),
            )
        elif dense_weight_bytes + request.runtime_buffer_bytes <= int(vram_bytes * 0.9) and (
            expert_weight_bytes + kv_cache_bytes + headroom_bytes <= ram_bytes
        ):
            placement.update(
                {"dense": "gpu", "experts": "ram", "kv-cache": "ram", "runtime-buffers": "gpu"}
            )
            peak_vram_bytes = dense_weight_bytes + request.runtime_buffer_bytes
            peak_ram_bytes = expert_weight_bytes + kv_cache_bytes + headroom_bytes
            safe_context_tokens = min(
                fingerprint.context_length,
                self._safe_context(
                    capacity_bytes=ram_bytes,
                    fixed_bytes=expert_weight_bytes,
                    request=request,
                    kv_bytes_per_token=kv_bytes_per_token,
                ),
            )
        elif requested_working_bytes + headroom_bytes <= ram_bytes:
            placement.update({"dense": "ram", "experts": "ram", "kv-cache": "ram", "runtime-buffers": "ram"})
            peak_ram_bytes = requested_working_bytes + headroom_bytes
            safe_context_tokens = min(
                fingerprint.context_length,
                self._safe_context(
                    capacity_bytes=ram_bytes,
                    fixed_bytes=fingerprint.tensor_bytes + request.runtime_buffer_bytes,
                    request=request,
                    kv_bytes_per_token=kv_bytes_per_token,
                ),
            )
        else:
            capacity_reason = "insufficient-memory-for-requested-context"
            fixed_bytes = fingerprint.tensor_bytes + request.runtime_buffer_bytes
            safe_context_tokens = min(
                fingerprint.context_length,
                self._safe_context(
                    capacity_bytes=ram_bytes,
                    fixed_bytes=fixed_bytes,
                    request=request,
                    kv_bytes_per_token=kv_bytes_per_token,
                ),
            )

        if capacity_reason:
            reason_codes.append(capacity_reason)

        selected_context_tokens = min(request.requested_context_tokens, safe_context_tokens)
        context_reduction_unbound = False
        if selected_context_tokens < request.requested_context_tokens:
            reason_codes.append("context-reduced-for-fit")
            control_bindings = self._apply_selected_context(
                control_bindings,
                selected_context_tokens=selected_context_tokens,
            )
            context_reduction_unbound = not any(
                binding.control == "context_tokens"
                and binding.applied_value == selected_context_tokens
                for binding in control_bindings
            )
            if context_reduction_unbound:
                reason_codes.append("context-reduction-unbound")
        insufficient_output_context = selected_context_tokens <= request.max_new_tokens
        if insufficient_output_context:
            reason_codes.append("insufficient-context-for-output")
        if (
            unsupported_required
            or capacity_reason == "kv-metadata-missing"
            or safe_context_tokens <= 0
            or insufficient_output_context
            or context_reduction_unbound
        ):
            decision = "rejected"
        elif capacity_reason or unsupported_optional or selected_context_tokens < request.requested_context_tokens:
            decision = "degraded"
        else:
            decision = "admitted"

        predicted_bottleneck = "none"
        if unsupported_required or unsupported_optional:
            predicted_bottleneck = "runtime-capability"
        elif capacity_reason == "kv-metadata-missing" or selected_context_tokens < request.requested_context_tokens:
            predicted_bottleneck = "kv-cache"
        elif peak_ram_bytes and peak_ram_bytes >= peak_vram_bytes:
            predicted_bottleneck = "ram"
        elif peak_vram_bytes:
            predicted_bottleneck = "vram"

        receipt_payload = {
            "request": request.model_dump(mode="json"),
            "decision": decision,
            "placement": placement,
            "reason_codes": sorted(reason_codes),
        }
        receipt_id = f"execution-fit::{hashlib.sha256(json.dumps(receipt_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()[:24]}"
        return ExecutionFitReceipt(
            receipt_id=receipt_id,
            request_id=request.request_id,
            plan_id=request.plan_id,
            model_fingerprint_id=fingerprint.fingerprint_id,
            hardware_fingerprint=request.hardware.host_fingerprint,
            runtime_name=request.runtime_capabilities.runtime_name,
            decision=decision,
            requested_context_tokens=request.requested_context_tokens,
            selected_context_tokens=selected_context_tokens,
            safe_context_tokens=safe_context_tokens,
            dense_weight_bytes=dense_weight_bytes,
            expert_weight_bytes=expert_weight_bytes,
            active_expert_bytes=active_expert_bytes,
            kv_cache_bytes=kv_cache_bytes,
            runtime_buffer_bytes=request.runtime_buffer_bytes,
            headroom_bytes=headroom_bytes,
            estimated_peak_ram_bytes=peak_ram_bytes,
            estimated_peak_vram_bytes=peak_vram_bytes,
            placement=placement,
            predicted_bottleneck=predicted_bottleneck,
            confidence=1.0 if request.runtime_capabilities.capability_state == "verified" else 0.5,
            control_bindings=control_bindings,
            reason_codes=sorted(reason_codes),
        )

    @staticmethod
    def _apply_selected_context(
        control_bindings: list[RuntimeControlBinding],
        *,
        selected_context_tokens: int,
    ) -> list[RuntimeControlBinding]:
        return [
            binding.model_copy(
                update={
                    "applied_value": selected_context_tokens,
                    "status": "degraded",
                    "reason_code": "runtime-control-value-reduced-for-fit",
                }
            )
            if binding.control == "context_tokens" and binding.applied_value is not None
            else binding
            for binding in control_bindings
        ]

    @staticmethod
    def _usable_vram_bytes(
        request: ExecutionFitRequest,
        control_bindings: list[RuntimeControlBinding],
    ) -> int:
        gpu_memory = [
            node.memory_bytes or 0 for node in request.hardware.nodes if node.kind == "gpu"
        ]
        if not gpu_memory:
            return 0
        if len(gpu_memory) == 1:
            return gpu_memory[0]
        split_binding = next(
            (binding for binding in control_bindings if binding.control == "tensor_split"),
            None,
        )
        requested_split = request.requested_controls.get("tensor_split")
        if split_binding is not None and split_binding.status == "applied" and bool(requested_split):
            return sum(gpu_memory)
        return max(gpu_memory)

    @staticmethod
    def _bind_controls(request: ExecutionFitRequest) -> list[RuntimeControlBinding]:
        supported = set(request.runtime_capabilities.supported_controls)
        observable = set(request.runtime_capabilities.observable_controls)
        bindings: list[RuntimeControlBinding] = []
        for control, value in sorted(request.requested_controls.items()):
            if control not in supported:
                status = "unsupported"
                applied_value = None
                reason_code = "runtime-control-unsupported"
            elif control not in observable or request.runtime_capabilities.capability_state != "verified":
                status = "degraded"
                applied_value = value
                reason_code = "runtime-control-binding-unverified"
            else:
                status = "applied"
                applied_value = value
                reason_code = "runtime-control-binding-verified"
            bindings.append(
                RuntimeControlBinding(
                    control=control,
                    requested_value=value,
                    applied_value=applied_value,
                    status=status,
                    reason_code=reason_code,
                )
            )
        for control in sorted(set(request.required_controls) - set(request.requested_controls)):
            bindings.append(
                RuntimeControlBinding(
                    control=control,
                    requested_value="missing",
                    status="rejected",
                    reason_code="runtime-control-required-value-missing",
                )
            )
        bindings.sort(key=lambda binding: binding.control)
        return bindings

    @staticmethod
    def _safe_context(
        *,
        capacity_bytes: int,
        fixed_bytes: int,
        request: ExecutionFitRequest,
        kv_bytes_per_token: int,
    ) -> int:
        if capacity_bytes <= 0 or kv_bytes_per_token <= 0:
            return 0
        available = int(capacity_bytes / (1 + request.safety_headroom_ratio)) - fixed_bytes
        if available <= 0:
            return 0
        per_token = kv_bytes_per_token * request.batch_size * request.concurrent_requests
        return max(0, available // per_token)


class ExecutionFitReconciler:
    def __init__(self, *, max_memory_regression_ratio: float = 0.05) -> None:
        if not 0 <= max_memory_regression_ratio < 1:
            raise ValueError("max_memory_regression_ratio must be in [0, 1)")
        self._max_memory_regression_ratio = max_memory_regression_ratio

    def reconcile(
        self,
        receipt: ExecutionFitReceipt,
        observation: RuntimeObservation,
    ) -> ExecutionFitReconciliation:
        if observation.plan_id != receipt.plan_id:
            return self._result(
                receipt,
                status="rejected",
                reason_codes=["fit-observation-plan-mismatch"],
            )
        if receipt.decision == "rejected":
            return self._result(
                receipt,
                status="rejected",
                reason_codes=["fit-receipt-rejected"],
            )
        if not observation.quality_equivalent:
            return self._result(
                receipt,
                status="rollback-required",
                reason_codes=["quality-regression"],
            )
        if not observation.stable:
            return self._result(
                receipt,
                status="rollback-required",
                reason_codes=["runtime-instability"],
            )

        ram_error_ratio = self._error_ratio(
            actual=observation.peak_ram_bytes,
            estimated=receipt.estimated_peak_ram_bytes,
        )
        vram_error_ratio = self._error_ratio(
            actual=observation.peak_vram_bytes,
            estimated=receipt.estimated_peak_vram_bytes,
        )
        if observation.peak_ram_bytes is None or observation.peak_vram_bytes is None:
            return self._result(
                receipt,
                status="degraded",
                ram_error_ratio=ram_error_ratio,
                vram_error_ratio=vram_error_ratio,
                reason_codes=["runtime-memory-observation-missing"],
            )

        reasons: list[str] = []
        if self._exceeds_bound(
            actual=observation.peak_ram_bytes,
            estimated=receipt.estimated_peak_ram_bytes,
        ):
            reasons.append("peak-ram-exceeded-fit-receipt")
        if self._exceeds_bound(
            actual=observation.peak_vram_bytes,
            estimated=receipt.estimated_peak_vram_bytes,
        ):
            reasons.append("peak-vram-exceeded-fit-receipt")
        if reasons:
            return self._result(
                receipt,
                status="rollback-required",
                ram_error_ratio=ram_error_ratio,
                vram_error_ratio=vram_error_ratio,
                reason_codes=reasons,
            )
        return self._result(
            receipt,
            status="healthy",
            ram_error_ratio=ram_error_ratio,
            vram_error_ratio=vram_error_ratio,
            reason_codes=["fit-observation-within-bounds"],
        )

    def _exceeds_bound(self, *, actual: int, estimated: int) -> bool:
        return actual > estimated * (1 + self._max_memory_regression_ratio)

    @staticmethod
    def _error_ratio(*, actual: int | None, estimated: int) -> float | None:
        if actual is None:
            return None
        return (actual - estimated) / max(estimated, 1)

    @staticmethod
    def _result(
        receipt: ExecutionFitReceipt,
        *,
        status: str,
        reason_codes: list[str],
        ram_error_ratio: float | None = None,
        vram_error_ratio: float | None = None,
    ) -> ExecutionFitReconciliation:
        return ExecutionFitReconciliation(
            receipt_id=receipt.receipt_id,
            plan_id=receipt.plan_id,
            status=status,
            ram_error_ratio=ram_error_ratio,
            vram_error_ratio=vram_error_ratio,
            reason_codes=reason_codes,
        )


class CandidateFeasibilityEvaluator:
    def evaluate(
        self,
        *,
        graph: HardwareCapabilityGraph,
        fingerprint: ModelExecutionFingerprint,
        registry: InferencePrimitiveRegistry,
    ) -> CandidateFeasibility:
        ram_bytes = max(
            (node.memory_bytes or 0 for node in graph.nodes if node.kind == "system-ram"),
            default=0,
        )
        gpu_bytes = max(
            (node.memory_bytes or 0 for node in graph.nodes if node.kind == "gpu"),
            default=0,
        )
        is_moe = fingerprint.expert_count > 0 and fingerprint.experts_per_token > 0
        candidates: list[FeasibilityCandidate] = []

        portable = registry.get("portable.cpu-reference")
        portable_fits = portable.implementation_state == "available" and fingerprint.tensor_bytes <= ram_bytes * 0.85
        candidates.append(
            FeasibilityCandidate(
                primitive_id=portable.primitive_id,
                feasible=portable_fits,
                score=0.45 if is_moe else 0.75,
                reason_codes=["portable-system-memory-fit"] if portable_fits else ["insufficient-system-memory"],
            )
        )

        moe = registry.get("moe.selective-residency")
        expert_working_set = (
            fingerprint.tensor_bytes * fingerprint.experts_per_token / fingerprint.expert_count if is_moe else 0
        )
        moe_fits = (
            is_moe
            and moe.implementation_state == "available"
            and gpu_bytes > 0
            and fingerprint.tensor_bytes <= ram_bytes * 0.9
            and expert_working_set <= gpu_bytes * 0.9
        )
        moe_reasons = ["limited-vram-tiered-residency"] if moe_fits and gpu_bytes < fingerprint.tensor_bytes else []
        if not moe_fits:
            if not is_moe:
                moe_reasons.append("model-is-not-moe")
            elif gpu_bytes <= 0:
                moe_reasons.append("accelerator-unavailable")
            elif fingerprint.tensor_bytes > ram_bytes * 0.9:
                moe_reasons.append("insufficient-system-memory")
            elif expert_working_set > gpu_bytes * 0.9:
                moe_reasons.append("expert-working-set-exceeds-vram")
            else:
                moe_reasons.append("primitive-unavailable")
        candidates.append(
            FeasibilityCandidate(
                primitive_id=moe.primitive_id,
                feasible=moe_fits,
                score=0.9 if moe_fits else 0,
                reason_codes=moe_reasons,
            )
        )

        feasible = sorted(
            (candidate for candidate in candidates if candidate.feasible),
            key=lambda candidate: (-candidate.score, candidate.primitive_id),
        )
        if not feasible:
            blockers = sorted(
                {
                    reason
                    for candidate in candidates
                    for reason in candidate.reason_codes
                    if reason in {"insufficient-system-memory", "expert-working-set-exceeds-vram", "accelerator-unavailable"}
                }
            )
            return CandidateFeasibility(
                status="blocked",
                selected_primitive_id=None,
                candidates=candidates,
                reason_codes=["no-feasible-inference-primitive"],
                blockers=blockers or ["no-available-primitive"],
                confidence=0,
            )

        selected = feasible[0]
        return CandidateFeasibility(
            status="shadow-feasible",
            selected_primitive_id=selected.primitive_id,
            candidates=candidates,
            reason_codes=selected.reason_codes,
            blockers=[],
            confidence=selected.score,
        )
