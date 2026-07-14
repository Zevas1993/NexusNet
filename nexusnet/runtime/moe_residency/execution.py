from __future__ import annotations

from pathlib import Path
from concurrent.futures import Future
from typing import Any, Callable, Protocol

import torch
import torch.nn as nn
import torch.nn.functional as F

from .heat import ExpertHeatPolicy
from .manifest import package_swiglu_experts
from .prefetch import RouteTransitionPrefetcher
from .schemas import MoEResidencyPlan
from .store import TieredExpertStore


class ExpertExecutionBackend(Protocol):
    def execute(self, expert_id: int, inputs: torch.Tensor) -> torch.Tensor: ...


class _OffloadedExpertStub(nn.Module):
    def __init__(self, expert_id: int) -> None:
        super().__init__()
        self.expert_id = expert_id

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raise RuntimeError(
            f"expert {self.expert_id} is storage-backed; attach its tiered execution backend"
        )


class TieredSwiGLUExecutionBackend:
    """Inference-only functional SwiGLU execution backed by tiered tensors."""

    def __init__(self, store: TieredExpertStore, *, heat_policy: ExpertHeatPolicy) -> None:
        self.store = store
        self.heat_policy = heat_policy
        self._resident_released = False
        self._route_callback: Callable[[tuple[int, ...], torch.device], None] | None = None
        self._last_device: torch.device | None = None

    @classmethod
    def from_layer(
        cls,
        layer: Any,
        output_dir: str | Path,
        *,
        model_ref: str,
        layer_id: str,
        ram_slots: int,
        hot_slots: int,
        release_resident: bool = False,
    ) -> "TieredSwiGLUExecutionBackend":
        if layer.training:
            raise RuntimeError("tiered expert packaging is inference-only")
        manifest = package_swiglu_experts(
            layer.experts,
            output_dir,
            model_ref=model_ref,
            layer_id=layer_id,
        )
        backend = cls(
            TieredExpertStore(manifest, ram_slots=ram_slots, hot_slots=hot_slots),
            heat_policy=ExpertHeatPolicy(slot_count=hot_slots),
        )
        if release_resident:
            backend.release_resident(layer)
        return backend

    def execute(self, expert_id: int, inputs: torch.Tensor) -> torch.Tensor:
        self._last_device = inputs.device
        self.heat_policy.touch(
            f"{self.store.manifest.layer_id}:expert{expert_id}",
            count=max(1, int(inputs.shape[0])),
        )
        tensors = self.store.acquire(expert_id, inputs.device)
        gate = F.linear(inputs, tensors["w_gate.weight"], tensors.get("w_gate.bias"))
        value = F.linear(inputs, tensors["w_value.weight"], tensors.get("w_value.bias"))
        hidden = F.silu(gate) * value
        return F.linear(hidden, tensors["w_out.weight"], tensors.get("w_out.bias"))

    def set_route_callback(
        self,
        callback: Callable[[tuple[int, ...], torch.device], None] | None,
    ) -> None:
        self._route_callback = callback

    def begin_route(self, selected_experts: tuple[int, ...], device: torch.device) -> None:
        if self._route_callback is not None:
            self._route_callback(selected_experts, device)

    def repin(self) -> tuple[str, ...]:
        pinned = self.heat_policy.repin()
        if self._last_device is not None:
            expert_ids = tuple(int(ref.rsplit("expert", 1)[1]) for ref in pinned)
            self.store.pin(expert_ids, self._last_device)
        return pinned

    @property
    def resident_experts_released(self) -> bool:
        return self._resident_released

    def release_resident(self, layer: Any) -> None:
        if layer.training:
            raise RuntimeError("resident expert release is inference-only")
        if len(layer.experts) != len(self.store.manifest.experts):
            raise ValueError("layer expert count does not match tiered manifest")
        layer.experts = nn.ModuleList(
            [_OffloadedExpertStub(record.expert_id) for record in self.store.manifest.experts]
        )
        self._resident_released = True

    def restore_resident(self, layer: Any) -> None:
        if not self._resident_released:
            return
        from nexusnet.hive.net.model import SwiGLUExpert

        device = layer.gate.weight.device
        restored: list[nn.Module] = []
        for record in self.store.manifest.experts:
            tensors = self.store.acquire(record.expert_id, device)
            d_hidden, d_model = tensors["w_gate.weight"].shape
            expert = SwiGLUExpert(d_model=d_model, d_hidden=d_hidden).to(
                device=device,
                dtype=tensors["w_gate.weight"].dtype,
            )
            expert.load_state_dict(tensors, strict=True)
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

    @property
    def backends(self) -> tuple[TieredSwiGLUExecutionBackend, ...]:
        return tuple(backend for _, backend in self._bindings)

    def evidence(self) -> list[dict[str, int | str | tuple[str, ...]]]:
        return [backend.evidence() for backend in self.backends]

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
        self._current_routes: dict[int, tuple[int, ...]] = {}
        self._futures: list[Future[dict[str, torch.Tensor]]] = []

    def observe(self, layer_index: int, selected: tuple[int, ...], device: torch.device) -> None:
        if layer_index == 0:
            for _, backend in self.bindings:
                backend.repin()
            self._current_routes = {}
        if layer_index > 0 and layer_index - 1 in self._current_routes:
            self.predictor.observe(
                self.layer_ids[layer_index - 1],
                self._current_routes[layer_index - 1],
                self.layer_ids[layer_index],
                selected,
            )
        self._current_routes[layer_index] = selected
        if layer_index + 1 >= len(self.bindings):
            return
        candidates = self.predictor.candidates(
            self.layer_ids[layer_index],
            selected,
            self.layer_ids[layer_index + 1],
        )
        next_store = self.bindings[layer_index + 1][1].store
        self._futures.extend(next_store.prefetch(expert_id, device) for expert_id in candidates)

    def wait(self) -> None:
        futures, self._futures = self._futures, []
        for future in futures:
            future.result()


def attach_tiered_moe_runtime(
    model: nn.Module,
    output_dir: str | Path,
    *,
    plan: MoEResidencyPlan,
    release_resident: bool = True,
) -> TieredMoERuntimeAttachment:
    """Attach storage-backed execution to every native SwiGLU MoE layer."""
    if plan.admission_state != "admitted":
        raise RuntimeError(f"residency plan is blocked: {', '.join(plan.blockers)}")
    if model.training:
        raise RuntimeError("tiered model attachment is inference-only")

    from nexusnet.hive.net.model import MoECapsuleLayer

    layers = [
        (name, module)
        for name, module in model.named_modules()
        if isinstance(module, MoECapsuleLayer)
    ]
    if not layers:
        raise ValueError("model does not contain native MoECapsuleLayer modules")
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
                layer_id=name or str(layer_index),
                ram_slots=ram_slots,
                hot_slots=hot_slots,
                release_resident=release_resident,
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
            lambda selected, device, index=layer_index: coordinator.observe(index, selected, device)
        )
    return TieredMoERuntimeAttachment(bindings, plan=plan, coordinator=coordinator)
