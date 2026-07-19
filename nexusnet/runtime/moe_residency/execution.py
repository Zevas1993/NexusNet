from __future__ import annotations

from concurrent.futures import Future
from contextvars import ContextVar
import hashlib
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Protocol

import torch
import torch.nn as nn
import torch.nn.functional as F

from .heat import ExpertHeatPolicy
from .evidence import ExpertResidencyEvidence
from .manifest import ExpertTensorManifest, package_swiglu_experts
from .prefetch import RouteTransitionPrefetcher
from .schemas import MoEResidencyPlan
from .store import TieredExpertStore


class ExpertExecutionBackend(Protocol):
    def execute(self, expert_id: int, inputs: torch.Tensor) -> torch.Tensor: ...


def compute_model_identity(model: nn.Module) -> str:
    """Return a stable identity over parameters and model-defining configuration."""
    digest = hashlib.sha256()
    digest.update(f"{type(model).__module__}.{type(model).__qualname__}\0".encode("utf-8"))
    config_fields = {
        "d_model", "n_heads", "n_kv_heads", "head_dim", "full_features",
        "use_ebt", "num_experts", "top_k", "router_lr", "causal", "steps",
        "max_steps", "num_planes", "in_features", "out_features",
        "num_embeddings", "embedding_dim",
    }
    for module_name, module in model.named_modules():
        module_type = f"{type(module).__module__}.{type(module).__qualname__}"
        digest.update(f"module:{module_name}:{module_type}\0".encode("utf-8"))
        for field in sorted(config_fields):
            value = getattr(module, field, None)
            if isinstance(value, (str, int, float, bool)):
                digest.update(f"config:{module_name}:{field}:{value!r}\0".encode("utf-8"))
    for name, parameter in sorted(model.named_parameters()):
        value = parameter.detach().cpu().contiguous()
        digest.update(f"parameter:{name}".encode("utf-8") + b"\0")
        digest.update(str(value.dtype).encode("ascii") + b"\0")
        digest.update(str(tuple(value.shape)).encode("ascii") + b"\0")
        digest.update(value.view(torch.uint8).numpy().tobytes())
    for module_name, module in model.named_modules():
        for local_name, buffer in sorted(module._buffers.items()):
            if (
                buffer is None
                or local_name in module._non_persistent_buffers_set
                or local_name == "last_load"
            ):
                continue
            name = f"{module_name}.{local_name}" if module_name else local_name
            value = buffer.detach().cpu().contiguous()
            digest.update(f"buffer:{name}".encode("utf-8") + b"\0")
            digest.update(str(value.dtype).encode("ascii") + b"\0")
            digest.update(str(tuple(value.shape)).encode("ascii") + b"\0")
            digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


class _OffloadedExpertStub(nn.Module):
    def __init__(
        self,
        expert_id: int,
        store: TieredExpertStore,
        anchor: torch.Tensor,
    ) -> None:
        super().__init__()
        self.expert_id = expert_id
        self.store = store
        self.register_buffer(
            "_tiered_anchor",
            torch.empty(0, device=anchor.device, dtype=anchor.dtype),
            persistent=False,
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raise RuntimeError(
            f"expert {self.expert_id} is storage-backed; attach its tiered execution backend"
        )

    def _save_to_state_dict(self, destination, prefix, keep_vars) -> None:
        with self.store.lease(
            self.expert_id,
            self._tiered_anchor.device,
            self._tiered_anchor.dtype,
        ) as tensors:
            for name, tensor in tensors.items():
                destination[prefix + name] = tensor if keep_vars else tensor.detach()

    def _load_from_state_dict(self, *args, **kwargs) -> None:
        raise RuntimeError("restore resident experts before loading a checkpoint")

    def __deepcopy__(self, memo):
        raise RuntimeError("restore resident experts before copying the model")


class TieredSwiGLUExecutionBackend:
    """Inference-only functional SwiGLU execution backed by tiered tensors."""

    def __init__(
        self,
        store: TieredExpertStore,
        *,
        heat_policy: ExpertHeatPolicy,
        expert_device: str | torch.device | None = None,
    ) -> None:
        self.store = store
        self.heat_policy = heat_policy
        self.expert_device = torch.device(expert_device) if expert_device is not None else None
        self._resident_released = False
        self._route_callback: (
            Callable[[tuple[int, ...], torch.device, torch.dtype], None] | None
        ) = None
        self._last_device: torch.device | None = None
        self._last_dtype: torch.dtype | None = None
        self._requires_grad: dict[int, dict[str, bool]] = {}

    @classmethod
    def from_layer(
        cls,
        layer: Any,
        output_dir: str | Path,
        *,
        model_ref: str,
        model_digest: str | None = None,
        layer_id: str,
        ram_slots: int,
        hot_slots: int,
        release_resident: bool = False,
        expert_device: str | torch.device | None = None,
    ) -> "TieredSwiGLUExecutionBackend":
        if layer.training:
            raise RuntimeError("tiered expert packaging is inference-only")
        manifest = package_swiglu_experts(
            layer.experts,
            output_dir,
            model_ref=model_ref,
            model_digest=model_digest or compute_model_identity(layer),
            layer_id=layer_id,
        )
        backend = cls(
            TieredExpertStore(manifest, ram_slots=ram_slots, hot_slots=hot_slots),
            heat_policy=ExpertHeatPolicy(slot_count=hot_slots),
            expert_device=expert_device,
        )
        if release_resident:
            backend.release_resident(layer)
        return backend

    @classmethod
    def from_manifest(
        cls,
        layer: Any,
        manifest_path: str | Path,
        *,
        model_ref: str,
        model_digest: str | None = None,
        layer_id: str,
        ram_slots: int,
        hot_slots: int,
        release_resident: bool = False,
        expert_device: str | torch.device | None = None,
    ) -> "TieredSwiGLUExecutionBackend":
        if layer.training:
            raise RuntimeError("tiered expert attachment is inference-only")
        manifest = ExpertTensorManifest.read_json(
            manifest_path,
            expected_model_ref=model_ref,
            expected_model_digest=model_digest or compute_model_identity(layer),
            expected_layer_id=layer_id,
            expected_expert_count=len(layer.experts),
        )
        backend = cls(
            TieredExpertStore(manifest, ram_slots=ram_slots, hot_slots=hot_slots),
            heat_policy=ExpertHeatPolicy(slot_count=hot_slots),
            expert_device=expert_device,
        )
        if release_resident:
            backend.release_resident(layer)
        return backend

    def execute(self, expert_id: int, inputs: torch.Tensor) -> torch.Tensor:
        caller_device = inputs.device
        execution_device = self.expert_device or caller_device
        execution_inputs = inputs.to(execution_device)
        self._last_device = execution_device
        self._last_dtype = inputs.dtype
        self.heat_policy.touch(
            f"{self.store.manifest.layer_id}:expert{expert_id}",
            count=max(1, int(inputs.shape[0])),
        )
        with self.store.lease(expert_id, execution_device, inputs.dtype) as tensors:
            gate = F.linear(execution_inputs, tensors["w_gate.weight"], tensors.get("w_gate.bias"))
            value = F.linear(execution_inputs, tensors["w_value.weight"], tensors.get("w_value.bias"))
            hidden = F.silu(gate) * value
            output = F.linear(hidden, tensors["w_out.weight"], tensors.get("w_out.bias"))
        return output.to(caller_device)

    def set_route_callback(
        self,
        callback: Callable[[tuple[int, ...], torch.device, torch.dtype], None] | None,
    ) -> None:
        self._route_callback = callback

    def begin_route(
        self,
        selected_experts: tuple[int, ...],
        device: torch.device,
        dtype: torch.dtype,
    ) -> None:
        if self._route_callback is not None:
            self._route_callback(selected_experts, self.expert_device or device, dtype)

    def repin(self) -> tuple[str, ...]:
        pinned = self.heat_policy.repin()
        if self._last_device is not None:
            expert_ids = tuple(int(ref.rsplit("expert", 1)[1]) for ref in pinned)
            self.store.pin(expert_ids, self._last_device, self._last_dtype)
        return pinned

    @property
    def resident_experts_released(self) -> bool:
        return self._resident_released

    def release_resident(self, layer: Any) -> None:
        if layer.training:
            raise RuntimeError("resident expert release is inference-only")
        if len(layer.experts) != len(self.store.manifest.experts):
            raise ValueError("layer expert count does not match tiered manifest")
        for expert_id, expert in enumerate(layer.experts):
            if expert._forward_hooks or expert._forward_pre_hooks or expert._backward_hooks:
                raise RuntimeError("resident expert release does not support module hooks")
            if any(parameter._backward_hooks for parameter in expert.parameters()):
                raise RuntimeError("resident expert release does not support parameter hooks")
            self._requires_grad[expert_id] = {
                name: parameter.requires_grad for name, parameter in expert.named_parameters()
            }
        layer.experts = nn.ModuleList(
            [
                _OffloadedExpertStub(record.expert_id, self.store, layer.gate.weight)
                for record in self.store.manifest.experts
            ]
        )
        layer._tiered_parameter_identity_changed = True
        self._resident_released = True

    def restore_resident(self, layer: Any) -> None:
        if not self._resident_released:
            return
        from nexusnet.hive.net.model import SwiGLUExpert

        device = layer.gate.weight.device
        dtype = layer.gate.weight.dtype
        restored: list[nn.Module] = []
        for record in self.store.manifest.experts:
            with self.store.lease(record.expert_id, device, dtype) as tensors:
                d_hidden, d_model = tensors["w_gate.weight"].shape
                expert = SwiGLUExpert(d_model=d_model, d_hidden=d_hidden).to(
                    device=device,
                    dtype=dtype,
                )
                expert.load_state_dict(tensors, strict=True)
            for name, parameter in expert.named_parameters():
                parameter.requires_grad_(self._requires_grad[record.expert_id][name])
            expert.train(layer.training)
            restored.append(expert)
        layer.experts = nn.ModuleList(restored)
        self._resident_released = False

    def evidence(self) -> dict[str, int | str | tuple[str, ...]]:
        return {
            **self.store.evidence(),
            "pinned_experts": self.heat_policy.pinned,
            "resident_experts_released": self._resident_released,
        }


class TieredMoERuntimeAttachment:
    def __init__(
        self,
        bindings: list[tuple[Any, TieredSwiGLUExecutionBackend]],
        *,
        plan: MoEResidencyPlan,
        coordinator: "_RoutePrefetchCoordinator | None" = None,
    ) -> None:
        self._bindings = bindings
        self.plan = plan
        self._coordinator = coordinator
        self._restored = False
        self._evidence_lock = Lock()
        self._evidence_baselines = [self._counter_snapshot(backend) for backend in self.backends]

    @property
    def backends(self) -> tuple[TieredSwiGLUExecutionBackend, ...]:
        return tuple(backend for _, backend in self._bindings)

    @property
    def pending_prefetch_count(self) -> int:
        return self._coordinator.pending_count if self._coordinator is not None else 0

    def evidence(self) -> list[dict[str, int | str | tuple[str, ...]]]:
        return [backend.evidence() for backend in self.backends]

    def runtime_evidence(self) -> dict[str, object]:
        with self._evidence_lock:
            return self._runtime_evidence_snapshot()

    def _runtime_evidence_snapshot(self) -> dict[str, object]:
        layers: list[dict[str, object]] = []
        for index, backend in enumerate(self.backends):
            current = self._counter_snapshot(backend)
            baseline = self._evidence_baselines[index]
            delta = {
                key: value - baseline.get(key, 0)
                for key, value in current.items()
                if value - baseline.get(key, 0) > 0
            }
            self._evidence_baselines[index] = current
            evidence = ExpertResidencyEvidence(
                plan_ref=self.plan.plan_id,
                manifest_ref=backend.store.manifest.manifest_id,
            )
            evidence.record_store_metrics(delta)
            layers.append(evidence.snapshot())
        states = {layer["runtime_state"] for layer in layers}
        if "tiered-degraded" in states:
            runtime_state = "tiered-degraded"
        elif "tiered-warm" in states:
            runtime_state = "tiered-warm"
        elif "tiered-cold" in states:
            runtime_state = "tiered-cold"
        else:
            runtime_state = "tiered-warming"
        return {
            "schema_version": "tiered_moe_runtime_evidence.v0.1",
            "authority": "NexusBrain",
            "plan_ref": self.plan.plan_id,
            "manifest_refs": [backend.store.manifest.manifest_id for backend in self.backends],
            "runtime_state": runtime_state,
            "layers": layers,
            "privacy_boundary": "numeric-runtime-metrics-and-sanitized-references-only",
        }

    @staticmethod
    def _counter_snapshot(backend: TieredSwiGLUExecutionBackend) -> dict[str, int | float]:
        gauges = {
            "ram_occupancy", "hot_occupancy", "active_leases", "inflight_prefetches",
        }
        return {
            key: value
            for key, value in backend.store.evidence().items()
            if key not in gauges
            and key not in {"manifest_ref", "pinned_hot_experts"}
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
        }

    def restore(self) -> None:
        if self._restored:
            return
        self.wait_for_prefetch()
        for layer, backend in self._bindings:
            backend.set_route_callback(None)
            backend.restore_resident(layer)
            layer.set_execution_backend(None)
            backend.store.close()
        self._restored = True

    def wait_for_prefetch(self) -> None:
        if self._coordinator is not None:
            self._coordinator.wait()


class _RoutePrefetchCoordinator:
    def __init__(
        self,
        bindings: list[tuple[Any, TieredSwiGLUExecutionBackend]],
        layer_ids: list[str],
    ) -> None:
        self.bindings = bindings
        self.layer_ids = layer_ids
        self.predictor = RouteTransitionPrefetcher(max_candidates=2)
        self._current_routes: ContextVar[dict[int, tuple[int, ...]] | None] = ContextVar(
            "nexus_moe_current_routes",
            default=None,
        )
        self._futures: set[Future[dict[str, torch.Tensor]]] = set()
        self._lock = Lock()

    @property
    def pending_count(self) -> int:
        with self._lock:
            return len(self._futures)

    def observe(
        self,
        layer_index: int,
        selected: tuple[int, ...],
        device: torch.device,
        dtype: torch.dtype,
    ) -> None:
        if layer_index == 0:
            for _, backend in self.bindings:
                backend.repin()
            routes: dict[int, tuple[int, ...]] = {}
            self._current_routes.set(routes)
        else:
            routes = self._current_routes.get() or {}
        if layer_index > 0 and layer_index - 1 in routes:
            with self._lock:
                self.predictor.observe(
                    self.layer_ids[layer_index - 1],
                    routes[layer_index - 1],
                    self.layer_ids[layer_index],
                    selected,
                )
        routes[layer_index] = selected
        if layer_index + 1 >= len(self.bindings):
            return
        with self._lock:
            candidates = self.predictor.candidates(
                self.layer_ids[layer_index],
                selected,
                self.layer_ids[layer_index + 1],
            )
        next_store = self.bindings[layer_index + 1][1].store
        for expert_id in candidates:
            future = next_store.prefetch(expert_id, device, dtype)
            with self._lock:
                self._futures.add(future)
            future.add_done_callback(self._reap)

    def _reap(self, future: Future[dict[str, torch.Tensor]]) -> None:
        with self._lock:
            self._futures.discard(future)
        if not future.cancelled():
            future.exception()

    def wait(self) -> None:
        with self._lock:
            futures = tuple(self._futures)
        for future in futures:
            if not future.cancelled():
                future.exception()


def attach_tiered_moe_runtime(
    model: nn.Module,
    output_dir: str | Path,
    *,
    plan: MoEResidencyPlan,
    model_ref: str,
    release_resident: bool = True,
) -> TieredMoERuntimeAttachment:
    """Attach storage-backed execution to every native SwiGLU MoE layer."""
    if model_ref != plan.model_ref:
        raise RuntimeError("model_ref does not match residency plan")
    if plan.admission_state != "admitted":
        raise RuntimeError(f"residency plan is blocked: {', '.join(plan.blockers)}")
    expert_device: torch.device | None = None
    if plan.gpu_acceleration_enabled:
        expert_device = torch.device(plan.expert_device)
        if expert_device.type != "cuda":
            raise RuntimeError("gpu acceleration requires a CUDA expert device")
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA execution is unavailable in the active PyTorch runtime")
        if expert_device.index is not None and expert_device.index >= torch.cuda.device_count():
            raise RuntimeError("configured CUDA expert device is unavailable")
    elif plan.gpu_mode == "on":
        raise RuntimeError("gpu acceleration was forced on but is not enabled by the plan")
    if model.training:
        raise RuntimeError("tiered model attachment is inference-only")
    if plan.model_digest is None:
        raise RuntimeError("residency plan is not bound to a model identity")
    if compute_model_identity(model) != plan.model_digest:
        raise RuntimeError("model identity does not match residency plan")

    from nexusnet.hive.net.model import MoECapsuleLayer

    layers = [
        (name, module)
        for name, module in model.named_modules()
        if isinstance(module, MoECapsuleLayer)
    ]
    if not layers:
        raise ValueError("model does not contain native MoECapsuleLayer modules")
    total_experts = sum(layer.num_experts for _, layer in layers)
    largest_expert_bytes = max(
        sum(parameter.numel() * parameter.element_size() for parameter in expert.parameters())
        for _, layer in layers
        for expert in layer.experts
    )
    if plan.expert_count != total_experts:
        raise RuntimeError("residency plan expert count does not match model topology")
    if plan.expert_bytes < largest_expert_bytes:
        raise RuntimeError("residency plan expert size is smaller than model expert tensors")
    hot_slots = plan.gpu_expert_slots // len(layers)
    ram_slots = plan.ram_expert_slots // len(layers)
    root = Path(output_dir)
    bindings: list[tuple[Any, TieredSwiGLUExecutionBackend]] = []
    layer_ids: list[str] = []
    try:
        for layer_index, (name, layer) in enumerate(layers):
            safe_name = name.replace(".", "-") or f"layer-{layer_index}"
            backend = TieredSwiGLUExecutionBackend.from_layer(
                layer,
                root / safe_name,
                model_ref=plan.model_ref,
                model_digest=plan.model_digest,
                layer_id=name or str(layer_index),
                ram_slots=ram_slots,
                hot_slots=hot_slots,
                release_resident=release_resident,
                expert_device=expert_device,
            )
            layer.set_execution_backend(backend)
            bindings.append((layer, backend))
            layer_ids.append(name or str(layer_index))
    except Exception:
        for layer, backend in bindings:
            backend.restore_resident(layer)
            layer.set_execution_backend(None)
            backend.store.close()
        raise
    coordinator = _RoutePrefetchCoordinator(bindings, layer_ids)
    for layer_index, (_, backend) in enumerate(bindings):
        backend.set_route_callback(
            lambda selected, device, dtype, index=layer_index: coordinator.observe(
                index, selected, device, dtype
            )
        )
    return TieredMoERuntimeAttachment(bindings, plan=plan, coordinator=coordinator)
