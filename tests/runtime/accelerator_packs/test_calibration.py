from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from nexusnet.runtime.accelerator_packs.calibration import (
    CalibrationKey,
    CalibrationLedger,
    CalibrationRecord,
)
from nexusnet.runtime.accelerator_packs.route_selection import RouteEvidence, RouteRequest, VerifiedRouteSelector


MODEL_HASH = "a" * 64
SMALL_PROFILE = "b" * 64
LARGE_PROFILE = "c" * 64


def _key(
    route_id: str,
    *,
    device: str,
    profile: str = SMALL_PROFILE,
    driver: str = "driver-1.0",
) -> CalibrationKey:
    return CalibrationKey(
        route_id=route_id,
        pack_id=f"org.nexusnet.{route_id}",
        pack_version="1.0.0",
        worker_version="1.0.0",
        device_fingerprint=device,
        driver_version=driver,
        model_hash=MODEL_HASH,
        workload="llm-generate",
        workload_profile_hash=profile,
    )


def _record(
    key: CalibrationKey,
    *,
    score: float = 1.0,
    outcome: str = "passed",
    measured_at: datetime | None = None,
    valid_until: datetime | None = None,
) -> CalibrationRecord:
    measured = measured_at or datetime.now(timezone.utc)
    return CalibrationRecord(
        key=key,
        outcome=outcome,
        correctness_passed=outcome == "passed",
        health_passed=outcome == "passed",
        score=score if outcome == "passed" else None,
        latency_ms=10.0 if outcome == "passed" else None,
        throughput_units_per_s=100.0 if outcome == "passed" else None,
        peak_memory_bytes=1024,
        measured_at=measured,
        valid_until=valid_until or measured + timedelta(days=7),
        evidence_refs=(f"receipt::{key.route_id}",),
    )


def _route(key: CalibrationKey, *, kind: str, score: float) -> RouteEvidence:
    return RouteEvidence(
        route_id=key.route_id,
        pack_id=key.pack_id,
        pack_version=key.pack_version,
        device_node_id=f"{kind}:0",
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


def test_calibration_ledger_uses_exact_key_identity_and_atomic_storage(tmp_path) -> None:
    path = tmp_path / "state" / "calibration.json"
    ledger = CalibrationLedger(path)
    key = _key("cpu", device="device::" + "1" * 32)
    record = _record(key, score=4.0)

    ledger.put(record)

    assert ledger.get(key) == record
    assert ledger.get(key.model_copy(update={"driver_version": "driver-2.0"})) is None
    assert ledger.get(key.model_copy(update={"model_hash": "d" * 64})) is None
    assert ledger.get(key.model_copy(update={"workload_profile_hash": LARGE_PROFILE})) is None
    assert not list(path.parent.glob("*.partial"))
    assert CalibrationLedger(path).get(key) == record


def test_calibration_ledger_invalidates_stale_and_changed_evidence(tmp_path) -> None:
    now = datetime.now(timezone.utc)
    ledger = CalibrationLedger(tmp_path / "calibration.json")
    current = _key("cuda", device="device::" + "2" * 32)
    stale = _key("old", device="device::" + "3" * 32)
    ledger.put(_record(current, measured_at=now, valid_until=now + timedelta(hours=1)))
    ledger.put(_record(stale, measured_at=now - timedelta(days=2), valid_until=now - timedelta(days=1)))

    assert ledger.get(stale, at=now) is None
    assert ledger.invalidate(pack_id=current.pack_id, device_fingerprint=current.device_fingerprint) == 1
    assert ledger.get(current, at=now) is None
    assert ledger.summary(at=now)["record_count"] == 1
    assert ledger.summary(at=now)["stale_count"] == 1


def test_auto_route_uses_only_exact_calibration_and_supports_cpu_gpu_crossover() -> None:
    cpu_small = _key("cpu", device="device::" + "1" * 32, profile=SMALL_PROFILE)
    gpu_small = _key("cuda", device="device::" + "2" * 32, profile=SMALL_PROFILE)
    small_selector = VerifiedRouteSelector(
        [_route(cpu_small, kind="cpu", score=9.0), _route(gpu_small, kind="gpu", score=5.0)]
    )

    small = small_selector.select(
        RouteRequest(model_hash=MODEL_HASH, workload_profile_hash=SMALL_PROFILE)
    )

    cpu_large = _key("cpu", device="device::" + "1" * 32, profile=LARGE_PROFILE)
    gpu_large = _key("cuda", device="device::" + "2" * 32, profile=LARGE_PROFILE)
    large_selector = VerifiedRouteSelector(
        [_route(cpu_large, kind="cpu", score=4.0), _route(gpu_large, kind="gpu", score=12.0)]
    )
    large = large_selector.select(
        RouteRequest(model_hash=MODEL_HASH, workload_profile_hash=LARGE_PROFILE)
    )

    assert (small.route_id, small.reason_codes) == ("cpu", ("auto-calibration-verified",))
    assert (large.route_id, large.reason_codes) == ("cuda", ("auto-calibration-verified",))


def test_auto_uses_conservative_cpu_when_calibration_is_missing_or_contradictory() -> None:
    cpu = RouteEvidence(
        route_id="cpu",
        pack_id="org.nexusnet.cpu",
        pack_version="1.0.0",
        device_node_id="cpu:0",
        device_kind="cpu",
        execution_modes=("cpu",),
        verified=True,
        healthy=True,
        correctness_passed=True,
        evidence_refs=("receipt::cpu",),
    )
    gpu = cpu.model_copy(
        update={
            "route_id": "cuda",
            "pack_id": "org.nexusnet.cuda",
            "device_node_id": "gpu:0",
            "device_kind": "gpu",
            "execution_modes": ("gpu",),
            "calibration_score": 999.0,
            "evidence_refs": ("receipt::cuda",),
        }
    )

    decision = VerifiedRouteSelector([cpu, gpu]).select(
        RouteRequest(model_hash=MODEL_HASH, workload_profile_hash=SMALL_PROFILE)
    )

    assert decision.route_id == "cpu"
    assert decision.reason_codes == ("calibration-required",)
    with pytest.raises(ValidationError, match="passed calibration"):
        _record(_key("bad", device="device::" + "4" * 32), outcome="passed").model_copy(
            update={"correctness_passed": False}
        ).__class__.model_validate(
            {
                **_record(_key("bad", device="device::" + "4" * 32)).model_dump(mode="json"),
                "correctness_passed": False,
            }
        )


def test_oom_evidence_is_scoped_to_the_exact_workload_profile(tmp_path) -> None:
    ledger = CalibrationLedger(tmp_path / "calibration.json")
    small = _key("cuda", device="device::" + "2" * 32, profile=SMALL_PROFILE)
    large = _key("cuda", device="device::" + "2" * 32, profile=LARGE_PROFILE)
    ledger.put(_record(small, outcome="oom"))
    ledger.put(_record(large, score=7.0))

    assert ledger.get(small).outcome == "oom"
    assert ledger.verified(small) is None
    assert ledger.verified(large).score == 7.0
