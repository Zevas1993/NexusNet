from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

from nexus.config import build_paths, ensure_paths
from nexus.runtimes import RuntimeRegistry
from nexus.runtimes.base import RuntimeAdapter
from nexus.storage import NexusStore
from nexusnet.runtime.accelerator_packs.route_selection import RouteEvidence, RouteUnavailableError
from nexusnet.runtime.accelerator_packs.calibration import CalibrationKey, CalibrationRecord


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


def test_runtime_registry_reconciles_exact_calibration_and_sanitizes_status(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    key = CalibrationKey(
        route_id="cuda",
        pack_id="org.nexusnet.cuda",
        pack_version="1.0.0",
        worker_version="1.0.0",
        device_fingerprint="device::" + "1" * 32,
        driver_version="driver-1.0",
        model_hash="a" * 64,
        workload="llm-generate",
        workload_profile_hash="b" * 64,
    )
    now = datetime.now(timezone.utc)
    record = CalibrationRecord(
        key=key,
        outcome="passed",
        correctness_passed=True,
        health_passed=True,
        score=8.0,
        latency_ms=5.0,
        throughput_units_per_s=200.0,
        peak_memory_bytes=1024,
        measured_at=now,
        valid_until=now + timedelta(days=1),
        evidence_refs=("receipt::calibration",),
    )
    evidence = RouteEvidence(
        route_id="cuda",
        pack_id="org.nexusnet.cuda",
        pack_version="1.0.0",
        device_node_id="PCI\\VEN_10DE&DEV_PRIVATE",
        device_kind="gpu",
        execution_modes=("gpu",),
        verified=True,
        healthy=True,
        correctness_passed=True,
        calibration_key=key,
        evidence_refs=("receipt::cuda",),
    )
    adapter = _PackAdapter({})

    registry.record_accelerator_calibration(record)
    registry.register_accelerator_route(evidence, adapter)

    assert registry.choose_execution_route(
        "Auto",
        model_hash="a" * 64,
        workload_profile_hash="b" * 64,
    ) is adapter
    status = registry.accelerator_status()
    route = status["routes"][0]
    assert route["calibration_verified"] is True
    assert "device_node_id" not in route
    assert route["device_ref"].startswith("device::")
    assert "VEN_10DE" not in str(status)
    assert set(status) == {
        "status_label",
        "mode",
        "routes",
        "active_decision",
        "calibration",
        "circuits",
        "certification",
    }


def test_runtime_registry_opens_route_circuit_without_silent_fallback(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    key = CalibrationKey(
        route_id="cuda",
        pack_id="org.nexusnet.cuda",
        pack_version="1.0.0",
        worker_version="1.0.0",
        device_fingerprint="device::" + "1" * 32,
        driver_version="driver-1.0",
        model_hash="a" * 64,
        workload="llm-generate",
        workload_profile_hash="b" * 64,
    )
    evidence = RouteEvidence(
        route_id="cuda",
        pack_id=key.pack_id,
        pack_version=key.pack_version,
        device_node_id="gpu:0",
        device_kind="gpu",
        execution_modes=("gpu",),
        verified=True,
        healthy=True,
        correctness_passed=True,
        calibration_key=key,
        evidence_refs=("receipt::cuda",),
    )
    registry.register_accelerator_route(evidence, _PackAdapter({}))

    for _ in range(3):
        registry.record_accelerator_failure("cuda", reason_code="worker-crashed")

    assert registry.accelerator_status()["circuits"]["open_count"] == 1
    assert registry.accelerator_status()["routes"][0]["quarantined"] is True
    with pytest.raises(RouteUnavailableError, match="accelerator-route-unavailable"):
        registry.choose_execution_route("GPU")
