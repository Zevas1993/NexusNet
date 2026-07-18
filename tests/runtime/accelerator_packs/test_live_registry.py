from __future__ import annotations

from pathlib import Path

import pytest

from nexus.config import build_paths, ensure_paths
from nexus.runtimes import RuntimeRegistry
from nexus.runtimes.base import RuntimeAdapter
from nexus.storage import NexusStore
from nexusnet.runtime.accelerator_packs.route_selection import RouteEvidence, RouteUnavailableError


class _PackAdapter(RuntimeAdapter):
    runtime_name = "test-pack"
    backend_type = "isolated-worker"

    def health(self) -> dict:
        return {"available": True}

    def generate(self, **kwargs) -> str:
        return "pack-output"


def _registry(tmp_path: Path) -> RuntimeRegistry:
    paths = ensure_paths(build_paths(tmp_path / "workspace"))
    return RuntimeRegistry(paths, NexusStore(paths), {"inference": {}})


def _evidence(route_id: str, *, mode: str, verified: bool = True) -> RouteEvidence:
    return RouteEvidence(
        route_id=route_id,
        pack_id=f"org.nexusnet.{route_id}",
        pack_version="1.0.0",
        device_node_id=f"{mode}:0",
        device_kind="cpu" if mode == "cpu" else "gpu",
        execution_modes=(mode,),
        verified=verified,
        healthy=True,
        correctness_passed=True,
        evidence_refs=(f"receipt::{route_id}",),
    )


def test_runtime_registry_adds_verified_pack_path_without_changing_legacy_choose(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    legacy = registry.choose()
    adapter = _PackAdapter({})

    registry.register_accelerator_route(_evidence("cpu-reference", mode="cpu"), adapter)

    assert registry.choose() is legacy
    assert registry.choose_execution_route("CPU") is adapter
    assert registry.accelerator_status()["active_decision"]["route_id"] == "cpu-reference"


def test_runtime_registry_rejects_unverified_registration_and_forced_gpu_fallback(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    with pytest.raises(ValueError, match="verified"):
        registry.register_accelerator_route(_evidence("cuda", mode="gpu", verified=False), _PackAdapter({}))
    with pytest.raises(RouteUnavailableError, match="accelerator-route-unavailable"):
        registry.choose_execution_route("GPU")


def test_runtime_registry_operator_mode_survives_restart(tmp_path: Path) -> None:
    first = _registry(tmp_path)
    first.set_execution_mode("Both")

    second = _registry(tmp_path)

    assert second.accelerator_status()["mode"]["requested_mode"] == "Both"
    with pytest.raises(RouteUnavailableError, match="hybrid-route-unverified"):
        second.choose_execution_route()
