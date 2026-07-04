from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nexus.config import NexusPaths

from ..memory import MemoryNode
from ..runtime import AdaptiveSystemProfiler, HardwareScanner
from .brain import NexusBrain
from .compatibility_planner import BaseModelCompatibilityPlanner, CompatibilityPlan
from .compatibility_provenance import normalize_compatibility_provenance
from .execution_trace import CoreExecutionTraceRecorder, ExecutionTraceLogger


@dataclass
class BaseModelHandle:
    model: Any | None = None
    tokenizer: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    introspection: dict[str, Any] = field(default_factory=dict)
    mode: str = "dev"
    compatibility_plan: dict[str, Any] = field(default_factory=dict)
    product_evidence: bool = False


class NexusNetCore:
    """Canonical brain-core seam over the existing NexusBrain implementation."""

    def __init__(
        self,
        *,
        paths: NexusPaths,
        brain: NexusBrain | None = None,
        hardware_scanner: HardwareScanner | None = None,
        system_profiler: AdaptiveSystemProfiler | None = None,
        memory_node: MemoryNode | None = None,
        trace_logger: ExecutionTraceLogger | None = None,
        compatibility_planner: BaseModelCompatibilityPlanner | None = None,
    ):
        self.paths = paths
        self.brain = brain
        self.hardware_scanner = hardware_scanner or HardwareScanner({})
        self.system_profiler = system_profiler
        self.memory_node = memory_node
        self.trace_logger = trace_logger or ExecutionTraceLogger(Path(paths.project_root) / "logs" / "execution_trace.jsonl")
        self.compatibility_planner = compatibility_planner or BaseModelCompatibilityPlanner()
        self.awake = False
        self.wake_state: dict[str, Any] | None = None
        self.base_model_handle: BaseModelHandle | None = None

    def wake(self) -> dict[str, Any]:
        recorder = CoreExecutionTraceRecorder(trace_name="nexusnet-core-wake")
        recorder.record("core-wake-start", {"brain_first": True})
        hardware_profile = self.hardware_scanner.scan()
        hardware_payload = hardware_profile.model_dump(mode="json") if hasattr(hardware_profile, "model_dump") else dict(hardware_profile)
        recorder.record("hardware-scan", hardware_payload)
        if self.system_profiler is not None and hasattr(self.system_profiler, "configure"):
            adaptive_runtime_config = self.system_profiler.configure(hardware_profile)
        elif self.system_profiler is not None and hasattr(self.system_profiler, "execution_plan"):
            execution_plan = self.system_profiler.execution_plan(model_hint="mock/default")
            long_context = execution_plan.get("long_context_profile") or hardware_payload.get("long_context_profile") or {}
            adaptive_runtime_config = {
                "local_first": bool(hardware_payload.get("local_first", True)),
                "target_min_context_tokens": int(long_context.get("ambition_tokens") or 1_000_000),
                "actual_context_budget_tokens": int(hardware_payload.get("max_context_tokens", 32768)),
                "allocates_target_context_buffer": bool(
                    hardware_payload.get("max_context_tokens", 32768) >= int(long_context.get("ambition_tokens") or 1_000_000)
                ),
                "execution_plan": execution_plan,
            }
        else:
            adaptive_runtime_config = {
                "local_first": True,
                "target_min_context_tokens": 1_000_000,
                "actual_context_budget_tokens": int(hardware_payload.get("max_context_tokens", 32768)),
                "allocates_target_context_buffer": False,
            }
        recorder.record("adaptive-profile", adaptive_runtime_config)
        memory_summary = self.memory_node.summary() if self.memory_node is not None else {"plane_count": 0, "planes": []}
        recorder.record(
            "memory-node-config",
            {
                "plane_count": memory_summary.get("plane_count", 0),
                "config_path": memory_summary.get("config_path"),
            },
        )
        self.awake = True
        payload = {
            "awake": True,
            "brain_first": True,
            "hardware_scan": hardware_payload,
            "adaptive_runtime_config": adaptive_runtime_config,
            "memory_node": memory_summary,
            "execution_trace": {
                "trace_name": recorder.trace_name,
                "stage_names": recorder.stage_names(),
                "stages": recorder.snapshot(),
            },
        }
        event = self.trace_logger.write(
            event="core.wake",
            component="NexusNetCore",
            status="ok",
            metadata={
                "brain_first": True,
                "cpu_count": hardware_payload.get("cpu_count"),
                "actual_context_budget_tokens": adaptive_runtime_config.get("actual_context_budget_tokens"),
                "target_min_context_tokens": adaptive_runtime_config.get("target_min_context_tokens"),
                "memory_plane_count": memory_summary.get("plane_count", 0),
            },
        )
        payload["log_path"] = str(self.trace_logger.path)
        payload["trace_event"] = event
        self.wake_state = payload
        return payload

    def attach_base_model(
        self,
        model: Any | None = None,
        tokenizer: Any | None = None,
        *,
        metadata: dict[str, Any] | None = None,
        model_hint: str | None = None,
        role: str = "teacher",
        mode: str = "dev",
        compatibility_plan: CompatibilityPlan | dict[str, Any] | None = None,
        product_evidence: bool | None = None,
    ) -> dict[str, Any]:
        if not self.awake:
            self.wake()
        metadata = dict(metadata or {})
        plan_payload = self._compatibility_plan_payload(compatibility_plan)
        product_evidence = bool(product_evidence) if product_evidence is not None else mode == "product"
        is_mock = mode == "mock" or str(metadata.get("model_id") or metadata.get("model_ref") or model_hint or "").startswith("mock/")
        if model is None and model_hint and self.brain is not None:
            adapter = self.brain.attach_base_model(model_hint, role=role)
            introspection = {
                "model_class": type(adapter).__name__,
                "model_id": adapter.model_id,
                "runtime_name": adapter.runtime_backend.runtime_name,
                "capability_profile": adapter.capability_profile().model_dump(mode="json"),
            }
            self.base_model_handle = BaseModelHandle(
                model=adapter,
                tokenizer=tokenizer,
                metadata=metadata,
                introspection=introspection,
                mode=mode,
                compatibility_plan=plan_payload,
                product_evidence=product_evidence,
            )
        else:
            introspection = self._introspect_base_model(model=model, tokenizer=tokenizer, metadata=metadata)
            self.base_model_handle = BaseModelHandle(
                model=model,
                tokenizer=tokenizer,
                metadata=metadata,
                introspection=introspection,
                mode=mode,
                compatibility_plan=plan_payload,
                product_evidence=product_evidence,
            )
        payload = {
            "status": "attached",
            "component": "NexusNetCore",
            "role": role,
            "mode": mode,
            "product_evidence": product_evidence,
            "metadata": metadata,
            "introspection": introspection,
            "compatibility_plan": plan_payload,
            "download_required": False,
        }
        event = self.trace_logger.write(
            event="base_model.attach",
            component="NexusNetCore",
            status="ok",
            metadata={
                "role": role,
                "mode": mode,
                "is_mock": is_mock,
                "product_evidence": product_evidence,
                "model_id": metadata.get("model_id") or introspection.get("model_id"),
                "model_class": introspection.get("model_class"),
                "hidden_size": introspection.get("config", {}).get("hidden_size") if isinstance(introspection.get("config"), dict) else None,
                "compatibility_status": plan_payload.get("status"),
                "compatibility_plan_id": plan_payload.get("compatibility_plan_id"),
            },
        )
        payload["trace_event"] = event
        return payload

    def generate(self, prompt: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.awake:
            self.wake()
        metadata = dict(metadata or {})
        fallback_used = True
        if self.base_model_handle is not None and hasattr(self.base_model_handle.model, "generate"):
            try:
                output = self.base_model_handle.model.generate(prompt)  # type: ignore[call-arg]
                fallback_used = False
            except Exception as exc:
                output = f"[nexusnet:fallback] brain-first local fallback after model generate error: {exc}. prompt={prompt[:240]}"
        else:
            output = f"[nexusnet:fallback] brain-first local fallback response: {prompt[:240]}"
        payload = {
            "status": "ok",
            "output": str(output),
            "fallback_used": fallback_used,
            "metadata": metadata,
        }
        payload["trace_event"] = self.trace_logger.write(
            event="core.generate",
            component="NexusNetCore",
            status="ok",
            metadata={"fallback_used": fallback_used, "prompt_preview": prompt[:120], **metadata},
        )
        return payload

    def attachment_provenance(self) -> dict[str, Any]:
        if self.base_model_handle is None:
            return {}
        provenance = normalize_compatibility_provenance(
            {
                "attachment_mode": self.base_model_handle.mode,
                "product_evidence": self.base_model_handle.product_evidence,
                "compatibility_plan": self.base_model_handle.compatibility_plan,
            }
        )
        model_id = (
            self.base_model_handle.metadata.get("model_id")
            or self.base_model_handle.metadata.get("model_ref")
            or self.base_model_handle.introspection.get("model_id")
        )
        if model_id:
            provenance["attached_model_id"] = model_id
        return provenance

    def _introspect_base_model(self, *, model: Any | None, tokenizer: Any | None, metadata: dict[str, Any]) -> dict[str, Any]:
        config = self._config_payload(getattr(model, "config", None))
        vocab_size = self._vocab_size(model=model, tokenizer=tokenizer, config=config)
        payload = {
            "model_id": metadata.get("model_id")
            or metadata.get("model_ref")
            or getattr(model, "name_or_path", None)
            or type(model).__name__
            if model is not None
            else metadata.get("model_id") or metadata.get("model_ref") or "mock/local",
            "model_class": type(model).__name__ if model is not None else "None",
            "tokenizer_class": type(tokenizer).__name__ if tokenizer is not None else None,
            "config": {**config, **({"hidden_size": metadata.get("hidden_size")} if metadata.get("hidden_size") is not None else {})},
            "vocab_size": vocab_size or self._int_metadata(metadata.get("vocab_size")),
            "parameter_count": self._parameter_count(model) if model is not None else self._int_metadata(metadata.get("parameter_count")),
            "dtype": str(getattr(model, "dtype", "")) or metadata.get("dtype"),
            "device": str(getattr(model, "device", "")) or metadata.get("device"),
            "runtime_name": metadata.get("runtime_name", "in-memory"),
        }
        return payload

    def _compatibility_plan_payload(self, compatibility_plan: CompatibilityPlan | dict[str, Any] | None) -> dict[str, Any]:
        if compatibility_plan is None:
            return {}
        if hasattr(compatibility_plan, "model_dump"):
            return compatibility_plan.model_dump(mode="json")
        return dict(compatibility_plan)

    def _int_metadata(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _config_payload(self, config: Any | None) -> dict[str, Any]:
        if config is None:
            return {}
        if hasattr(config, "to_dict"):
            try:
                return dict(config.to_dict())
            except Exception:
                pass
        return {
            key: value
            for key, value in vars(config).items()
            if not key.startswith("_") and isinstance(value, (str, int, float, bool, list, dict, type(None)))
        }

    def _vocab_size(self, *, model: Any | None, tokenizer: Any | None, config: dict[str, Any]) -> int | None:
        for candidate in (
            config.get("vocab_size"),
            getattr(tokenizer, "vocab_size", None),
            getattr(model, "vocab_size", None),
        ):
            if candidate is not None:
                try:
                    return int(candidate)
                except Exception:
                    continue
        if tokenizer is not None:
            try:
                return int(len(tokenizer))
            except Exception:
                return None
        return None

    def _parameter_count(self, model: Any | None) -> int | None:
        if model is None or not hasattr(model, "parameters"):
            return None
        try:
            return int(sum(int(parameter.numel()) for parameter in model.parameters()))
        except Exception:
            return None
