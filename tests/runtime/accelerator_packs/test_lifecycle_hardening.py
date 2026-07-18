from __future__ import annotations

from pathlib import Path

from nexusnet.runtime.accelerator_packs.calibration import CalibrationKey
from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.installer import (
    PackInstaller,
    PackVerification,
    PrivateEnvironmentBuilder,
)
from nexusnet.runtime.accelerator_packs.lifecycle import (
    PackCircuitBreaker,
    PackLifecycleManager,
)
from nexusnet.runtime.accelerator_packs.registry import RuntimePackRegistry


def _key(*, version: str = "2.0.0", profile: str = "b" * 64) -> CalibrationKey:
    return CalibrationKey(
        route_id="cuda",
        pack_id="org.nexusnet.test.cuda",
        pack_version=version,
        worker_version=version,
        device_fingerprint="device::" + "1" * 32,
        driver_version="driver-1.0",
        model_hash="a" * 64,
        workload="llm-generate",
        workload_profile_hash=profile,
    )


def _installer(tmp_path: Path, registry: RuntimePackRegistry) -> PackInstaller:
    return PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=None,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
    )


def test_circuit_breaker_is_bounded_and_oom_is_exact_profile_scoped(tmp_path) -> None:
    breaker = PackCircuitBreaker(tmp_path / "circuits.json", failure_threshold=2, max_records=3)
    small = _key(profile="b" * 64)
    large = _key(profile="c" * 64)

    first = breaker.record_failure(small, reason_code="worker-oom")
    opened = breaker.record_failure(small, reason_code="worker-oom")

    assert first.opened is False
    assert opened.opened is True
    assert opened.failure_count == 2
    assert breaker.state(large).failure_count == 0
    breaker.record_success(large)
    assert breaker.summary()["open_count"] == 1
    assert all("device::" not in item["key_ref"] for item in breaker.summary()["circuits"])


def test_lifecycle_open_circuit_quarantines_rolls_back_repairs_updates_and_uninstalls(
    tmp_path, manifest_factory
) -> None:
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = _installer(tmp_path, registry)
    v1 = manifest_factory(version="1.0.0", artifacts=[], rollback_compatible_from=[])
    v2 = manifest_factory(version="2.0.0", artifacts=[], rollback_compatible_from=["1.0.0"])
    installer.install(v1, consent=True)
    installer.install(v2, consent=True)
    quarantined: list[tuple[str, str]] = []
    manager = PackLifecycleManager(
        registry=registry,
        installer=installer,
        circuit_breaker=PackCircuitBreaker(tmp_path / "circuits.json", failure_threshold=2),
        receipt_path=tmp_path / "receipts.json",
        quarantine_sink=lambda pack_id, version: quarantined.append((pack_id, version)),
    )
    key = _key()

    manager.record_worker_failure(key, reason_code="worker-crashed")
    receipt = manager.record_worker_failure(key, reason_code="worker-crashed")

    assert receipt.action == "rollback"
    assert receipt.outcome == "passed"
    assert registry.active(v1.pack_id).manifest.version == "1.0.0"
    assert registry.get(v2.pack_id, v2.version).state == PackLifecycleState.QUARANTINED
    assert quarantined == [(v2.pack_id, v2.version)]

    repaired = manager.repair(key)
    assert repaired.action == "repair"
    assert registry.active(v2.pack_id).manifest.version == "2.0.0"
    assert manager.circuit_breaker.state(key).failure_count == 0

    v3 = manifest_factory(version="3.0.0", artifacts=[], rollback_compatible_from=["2.0.0"])
    updated = manager.update(v3, consent=True)
    assert updated.action == "update"
    assert registry.active(v3.pack_id).manifest.version == "3.0.0"

    removed = manager.uninstall(v3.pack_id, v3.version)
    assert removed.action == "uninstall"
    assert registry.get(v3.pack_id, v3.version).state == PackLifecycleState.REMOVED
    assert registry.active(v2.pack_id).manifest.version == "2.0.0"


def test_lifecycle_receipts_are_sanitized_bounded_and_include_provenance_and_sbom(
    tmp_path, manifest_factory
) -> None:
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = _installer(tmp_path, registry)
    manifest = manifest_factory(version="2.0.0", artifacts=[], rollback_compatible_from=[])
    installer.install(manifest, consent=True)
    manager = PackLifecycleManager(
        registry=registry,
        installer=installer,
        circuit_breaker=PackCircuitBreaker(tmp_path / "circuits.json", failure_threshold=10),
        receipt_path=tmp_path / "receipts.json",
        max_receipts=3,
    )

    for index in range(5):
        manager.record_worker_failure(
            _key(profile=f"{index + 1:064x}"),
            reason_code="worker-timeout",
        )

    receipts = manager.receipts()
    certification = manager.certification_summary(manifest)
    serialized = "".join(receipt.model_dump_json() for receipt in receipts)

    assert len(receipts) == 3
    assert certification["provenance"]["publisher"] == "NexusNet"
    assert certification["provenance"]["artifact_count"] == 0
    assert certification["sbom"]["component_count"] >= 1
    assert len(certification["sbom"]["digest_sha256"]) == 64
    assert "Users" not in serialized
    assert "\\" not in serialized
    assert not list((tmp_path).glob("*.partial"))


def test_installer_materializes_builtin_environment_lock_automatically(tmp_path, manifest_factory) -> None:
    commands: list[tuple[str, ...]] = []

    def runner(command, **_kwargs):
        commands.append(tuple(str(item) for item in command))
        return 0

    manifest = manifest_factory(
        pack_id="org.nexusnet.torch.cpu",
        pack_type="python-worker",
        accelerator_apis=["cpu"],
        device_matches=[{"accelerator_apis": ["cpu"]}],
        execution_modes=["cpu"],
        launch={"command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"]},
        dependency_constraints={"environment_lock_id": "torch-cpu-2.11.0-cp311-win-amd64"},
        artifacts=[],
        rollback_compatible_from=[],
    )
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=None,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
        environment_builder=PrivateEnvironmentBuilder(
            interpreter="C:/Python311/python.exe",
            command_runner=runner,
            platform_name="windows",
        ),
    )

    installer.install(manifest, consent=True)

    pip_command = next(command for command in commands if "pip" in command)
    requirements_path = Path(pip_command[-1])
    assert requirements_path.is_file()
    assert requirements_path.parent == tmp_path / "installed" / "environment-locks"
    assert "torch-2.11.0" in requirements_path.read_text(encoding="utf-8")
