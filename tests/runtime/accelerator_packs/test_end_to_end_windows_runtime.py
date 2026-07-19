from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import time

from nexusnet.runtime.accelerator_packs.acquisition import AcquisitionPolicy, ArtifactAcquirer
from nexusnet.runtime.accelerator_packs.calibration import CalibrationKey
from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.installer import PackInstaller, PackVerification
from nexusnet.runtime.accelerator_packs.lifecycle import PackCircuitBreaker, PackLifecycleManager
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation, WorkerRequest
from nexusnet.runtime.accelerator_packs.registry import RuntimePackRegistry
from nexusnet.runtime.accelerator_packs.route_selection import RouteEvidence, RouteRequest, VerifiedRouteSelector
from nexusnet.runtime.accelerator_packs.workers.reference_worker import ReferenceKernel


MODEL_HASH = "a" * 64
PROFILE_HASH = "b" * 64


def _request(operation: WorkerOperation, payload: dict | None = None) -> WorkerRequest:
    return WorkerRequest(
        request_id=f"e2e::{operation.value}",
        operation=operation,
        deadline_unix_ms=int(time.time() * 1000) + 30_000,
        sanitized_model_ref="numeric-proof-v1",
        workload_profile={"batch": 1},
        execution_mode="cpu",
        policy_receipt_ref="policy::e2e",
        payload=payload or {},
    )


def _key(route_id: str, *, version: str, device: str) -> CalibrationKey:
    return CalibrationKey(
        route_id=route_id,
        pack_id="org.nexusnet.test.cuda",
        pack_version=version,
        worker_version=version,
        device_fingerprint=device,
        driver_version="driver-1.0",
        model_hash=MODEL_HASH,
        workload="llm-generate",
        workload_profile_hash=PROFILE_HASH,
    )


def _route(key: CalibrationKey, *, kind: str, score: float) -> RouteEvidence:
    return RouteEvidence(
        route_id=key.route_id,
        pack_id=key.pack_id,
        pack_version=key.pack_version,
        device_node_id=f"{kind}:e2e",
        device_kind=kind,
        execution_modes=("cpu" if kind == "cpu" else "gpu",),
        verified=True,
        healthy=True,
        correctness_passed=True,
        calibration_key=key,
        calibration_verified=True,
        calibration_outcome="passed",
        calibration_score=score,
        evidence_refs=(f"receipt::{key.route_id}",),
    )


def test_governed_windows_runtime_end_to_end_acquire_infer_quarantine_rollback_uninstall(
    tmp_path, manifest_factory
) -> None:
    payloads = {
        "https://downloads.nexusnet.local/worker-v1.bin": b"reference-worker-v1",
        "https://downloads.nexusnet.local/worker-v2.bin": b"reference-worker-v2",
    }

    def manifest(version: str, *, previous: list[str], url: str):
        payload = payloads[url]
        return manifest_factory(
            version=version,
            artifacts=[{"url": url, "size_bytes": len(payload), "sha256": sha256(payload).hexdigest()}],
            rollback_compatible_from=previous,
        )

    discovered_plan = (
        manifest("1.0.0", previous=[], url="https://downloads.nexusnet.local/worker-v1.bin"),
        manifest("2.0.0", previous=["1.0.0"], url="https://downloads.nexusnet.local/worker-v2.bin"),
    )
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    acquirer = ArtifactAcquirer(
        root=tmp_path / "cache",
        policy=AcquisitionPolicy(allowed_hosts=frozenset({"downloads.nexusnet.local"}), disk_reserve_bytes=0),
        stream_opener=lambda url, _timeout: BytesIO(payloads[url]),
        free_space_reader=lambda _path: 1_000_000,
    )
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=acquirer,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
    )

    v1_record = installer.install(discovered_plan[0], consent=True)
    v2_record = installer.install(discovered_plan[1], consent=True)

    assert v1_record.manifest.version == "1.0.0"
    assert v2_record.state == PackLifecycleState.ACTIVE
    assert (tmp_path / "installed" / "packs" / v2_record.manifest.pack_id / "2.0.0" / "artifacts" / "worker-v2.bin").read_bytes() == payloads[
        "https://downloads.nexusnet.local/worker-v2.bin"
    ]

    cpu_key = _key("cpu-v1", version="1.0.0", device="device::" + "1" * 32)
    gpu_key = _key("cuda-v2", version="2.0.0", device="device::" + "2" * 32)
    selector = VerifiedRouteSelector(
        [_route(cpu_key, kind="cpu", score=3.0), _route(gpu_key, kind="gpu", score=9.0)]
    )
    route_request = RouteRequest(model_hash=MODEL_HASH, workload_profile_hash=PROFILE_HASH)

    assert selector.select(route_request).route_id == "cuda-v2"
    kernel = ReferenceKernel()
    assert kernel.handle(_request(WorkerOperation.HEALTH))[0]["available"] is True
    assert kernel.handle(_request(WorkerOperation.SELF_TEST))[0]["passed"] is True
    assert kernel.handle(_request(WorkerOperation.LOAD_MODEL, {"scale": 2.0, "bias": 1.0}))[0]["loaded"] is True
    assert kernel.handle(_request(WorkerOperation.INFER, {"values": [1.0, 2.0, 3.0]}))[0]["values"] == [3.0, 5.0, 7.0]

    manager = PackLifecycleManager(
        registry=registry,
        installer=installer,
        circuit_breaker=PackCircuitBreaker(tmp_path / "circuits.json", failure_threshold=2),
        receipt_path=tmp_path / "receipts.json",
        quarantine_sink=lambda pack_id, version: selector.quarantine(pack_id=pack_id, pack_version=version),
    )
    manager.record_worker_failure(gpu_key, reason_code="worker-crashed")
    rollback_receipt = manager.record_worker_failure(gpu_key, reason_code="worker-crashed")

    assert rollback_receipt.action == "rollback"
    assert registry.active(discovered_plan[0].pack_id).manifest.version == "1.0.0"
    assert selector.select(route_request).route_id == "cpu-v1"

    manager.uninstall(discovered_plan[1].pack_id, discovered_plan[1].version)
    manager.uninstall(discovered_plan[0].pack_id, discovered_plan[0].version)

    assert registry.get(discovered_plan[1].pack_id, "2.0.0").state == PackLifecycleState.REMOVED
    assert registry.get(discovered_plan[0].pack_id, "1.0.0").state == PackLifecycleState.REMOVED
    assert [receipt.action for receipt in manager.receipts()] == ["observe", "rollback", "uninstall", "uninstall"]
