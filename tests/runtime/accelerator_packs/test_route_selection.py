from __future__ import annotations

from pathlib import Path

import pytest

from nexusnet.runtime.accelerator_packs.route_selection import (
    RouteEvidence,
    RouteRequest,
    RuntimeModeStore,
    VerifiedRouteSelector,
)


def _route(
    route_id: str,
    *,
    device_kind: str,
    modes: tuple[str, ...],
    score: float = 1.0,
    verified: bool = True,
    healthy: bool = True,
    correctness_passed: bool = True,
    quarantined: bool = False,
) -> RouteEvidence:
    return RouteEvidence(
        route_id=route_id,
        pack_id=f"org.nexusnet.{route_id}",
        pack_version="1.0.0",
        device_node_id=f"{device_kind}:0",
        device_kind=device_kind,
        execution_modes=modes,
        verified=verified,
        healthy=healthy,
        correctness_passed=correctness_passed,
        quarantined=quarantined,
        calibration_score=score,
        evidence_refs=(f"receipt::{route_id}",),
    )


def test_forced_modes_never_silently_fall_back() -> None:
    selector = VerifiedRouteSelector(
        [
            _route("cpu", device_kind="cpu", modes=("cpu",), score=1.0),
            _route("cuda", device_kind="gpu", modes=("gpu",), score=4.0, healthy=False),
        ]
    )

    cpu = selector.select(RouteRequest(execution_mode="cpu"))
    gpu = selector.select(RouteRequest(execution_mode="gpu"))

    assert cpu.available is True
    assert cpu.route_id == "cpu"
    assert gpu.available is False
    assert gpu.route_id is None
    assert "accelerator-route-unavailable" in gpu.reason_codes
    assert "cpu" not in gpu.reason_codes


def test_auto_uses_conservative_verified_cpu_without_exact_calibration() -> None:
    selector = VerifiedRouteSelector(
        [
            _route("cpu", device_kind="cpu", modes=("cpu",), score=1.0),
            _route("fast-unverified", device_kind="gpu", modes=("gpu",), score=99.0, verified=False),
            _route("fast-wrong", device_kind="gpu", modes=("gpu",), score=98.0, correctness_passed=False),
            _route("cuda", device_kind="gpu", modes=("gpu",), score=3.0),
        ]
    )

    decision = selector.select(RouteRequest(execution_mode="auto"))

    assert decision.available is True
    assert decision.route_id == "cpu"
    assert decision.reason_codes == ("calibration-required",)


def test_hybrid_requires_explicitly_verified_hybrid_offload() -> None:
    selector = VerifiedRouteSelector(
        [
            _route("cuda", device_kind="gpu", modes=("gpu", "hybrid"), score=3.0),
            _route("hybrid", device_kind="gpu", modes=("hybrid",), score=2.0),
        ]
    )

    unavailable = selector.select(RouteRequest(execution_mode="hybrid"))
    selector.replace(
        [
            _route("cuda", device_kind="gpu", modes=("gpu", "hybrid"), score=3.0),
            _route("hybrid", device_kind="gpu", modes=("hybrid",), score=2.0).model_copy(
                update={"hybrid_offload_verified": True}
            ),
        ]
    )
    available = selector.select(RouteRequest(execution_mode="hybrid"))

    assert unavailable.available is False
    assert unavailable.reason_codes == ("hybrid-route-unverified",)
    assert available.route_id == "hybrid"


def test_mode_store_maps_both_to_hybrid_and_persists_atomically(tmp_path: Path) -> None:
    path = tmp_path / "state" / "runtime-mode.json"
    store = RuntimeModeStore(path)

    assert store.status()["requested_mode"] == "Auto"
    stored = store.set_mode("Both")

    assert stored["requested_mode"] == "Both"
    assert stored["execution_mode"] == "hybrid"
    assert RuntimeModeStore(path).status() == stored
    assert not path.with_suffix(".tmp").exists()


@pytest.mark.parametrize("value", ["", "cuda", "all", "GPU\nCPU", 1, None])
def test_mode_store_rejects_unknown_or_non_string_modes(tmp_path: Path, value: object) -> None:
    with pytest.raises(ValueError):
        RuntimeModeStore(tmp_path / "mode.json").set_mode(value)  # type: ignore[arg-type]
