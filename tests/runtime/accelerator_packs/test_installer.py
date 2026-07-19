from hashlib import sha256
from io import BytesIO
from pathlib import Path

import pytest

from nexusnet.runtime.accelerator_packs.acquisition import AcquisitionPolicy, ArtifactAcquirer
from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.installer import (
    EnvironmentBuildError,
    PackInstallError,
    PackInstaller,
    PackVerification,
    PrivateEnvironmentBuilder,
)
from nexusnet.runtime.accelerator_packs.registry import RuntimePackRegistry


def test_private_environment_builder_uses_clean_venv_and_hashed_lock(tmp_path):
    commands: list[tuple[str, ...]] = []
    lock = tmp_path / "torch-cpu.lock"
    lock.write_text("demo==1.0 --hash=sha256:" + "a" * 64, encoding="utf-8")

    def runner(command, **_kwargs):
        commands.append(tuple(str(item) for item in command))
        return 0

    environment = PrivateEnvironmentBuilder(
        interpreter=Path("C:/NexusNet/python/python.exe"),
        command_runner=runner,
        platform_name="windows",
    ).build(
        root=tmp_path / "packs",
        pack_id="org.nexusnet.torch.cpu",
        version="1.0.0",
        requirements_lock=lock,
    )

    assert environment == tmp_path / "packs" / "org.nexusnet.torch.cpu" / "1.0.0" / "venv"
    flattened = " ".join(" ".join(command) for command in commands)
    assert "--system-site-packages" not in flattened
    assert " -m venv " in f" {flattened} "
    assert "--require-hashes" in flattened
    assert "--no-deps" in flattened


def test_private_environment_builder_rejects_path_escape_before_running(tmp_path):
    ran = False

    def runner(_command, **_kwargs):
        nonlocal ran
        ran = True
        return 0

    with pytest.raises(EnvironmentBuildError, match="environment-identity-invalid"):
        PrivateEnvironmentBuilder(interpreter=Path("python.exe"), command_runner=runner).build(
            root=tmp_path,
            pack_id="../private",
            version="1.0.0",
            requirements_lock=None,
        )

    assert ran is False


def test_pack_installer_activates_only_after_health_and_self_test(tmp_path, manifest_factory):
    payload = b"native-worker"
    manifest = manifest_factory(
        artifacts=[
            {
                "url": "https://downloads.nexusnet.local/worker.bin",
                "size_bytes": len(payload),
                "sha256": sha256(payload).hexdigest(),
            }
        ]
    )
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    acquirer = ArtifactAcquirer(
        root=tmp_path / "downloads",
        policy=AcquisitionPolicy(
            allowed_hosts=frozenset({"downloads.nexusnet.local"}),
            disk_reserve_bytes=0,
        ),
        stream_opener=lambda _url, _timeout: BytesIO(payload),
        free_space_reader=lambda _path: 10_000,
    )
    verified_paths: list[Path] = []

    def verify(_manifest, install_root):
        verified_paths.append(install_root)
        return PackVerification(health_passed=True, self_test_passed=True, reason_code="pack-verified")

    record = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=acquirer,
        verifier=verify,
    ).install(manifest, consent=True)

    assert record.state == PackLifecycleState.ACTIVE
    assert record.install_ref == "packs/org.nexusnet.test.cuda/1.0.0"
    assert verified_paths == [tmp_path / "installed" / "packs" / manifest.pack_id / manifest.version]
    assert registry.active(manifest.pack_id).manifest.version == "1.0.0"


def test_pack_installer_quarantines_failed_self_test_with_sanitized_reason(tmp_path, manifest_factory):
    payload = b"native-worker"
    manifest = manifest_factory(
        artifacts=[
            {
                "url": "https://downloads.nexusnet.local/worker.bin",
                "size_bytes": len(payload),
                "sha256": sha256(payload).hexdigest(),
            }
        ]
    )
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=ArtifactAcquirer(
            root=tmp_path / "downloads",
            policy=AcquisitionPolicy(
                allowed_hosts=frozenset({"downloads.nexusnet.local"}),
                disk_reserve_bytes=0,
            ),
            stream_opener=lambda _url, _timeout: BytesIO(payload),
            free_space_reader=lambda _path: 10_000,
        ),
        verifier=lambda _manifest, _root: PackVerification(
            health_passed=True,
            self_test_passed=False,
            reason_code="worker-self-test-failed",
        ),
    )

    with pytest.raises(PackInstallError, match="worker-self-test-failed"):
        installer.install(manifest, consent=True)

    record = registry.get(manifest.pack_id, manifest.version)
    assert record.state == PackLifecycleState.QUARANTINED
    assert record.reason_codes[-1] == "worker-self-test-failed"
    assert "Users" not in str(record.model_dump(mode="json"))


def test_pack_installer_requires_explicit_download_consent(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=None,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
    )

    with pytest.raises(PackInstallError, match="pack-download-consent-required"):
        installer.install(manifest_factory(), consent=False)

    assert registry.snapshot().records == {}


def test_pack_installer_repairs_quarantined_version_only_after_fresh_verification(tmp_path, manifest_factory):
    manifest = manifest_factory(artifacts=[])
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    verifications = iter(
        [
            PackVerification(True, False, "worker-self-test-failed"),
            PackVerification(True, True, "pack-verified"),
        ]
    )
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=None,
        verifier=lambda _manifest, _root: next(verifications),
    )
    with pytest.raises(PackInstallError, match="worker-self-test-failed"):
        installer.install(manifest, consent=True)

    repaired = installer.repair(manifest.pack_id, manifest.version)

    assert repaired.state == PackLifecycleState.ACTIVE


def test_pack_installer_uninstall_removes_only_nexusnet_owned_pack_root(tmp_path, manifest_factory):
    manifest = manifest_factory(artifacts=[])
    install_root = tmp_path / "installed"
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = PackInstaller(
        registry=registry,
        install_root=install_root,
        acquirer=None,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
    )
    installer.install(manifest, consent=True)
    pack_root = install_root / "packs" / manifest.pack_id / manifest.version
    (pack_root / "owned.bin").write_bytes(b"owned")
    unrelated = tmp_path / "unrelated.bin"
    unrelated.write_bytes(b"preserve")

    removed = installer.uninstall(manifest.pack_id, manifest.version)

    assert removed.state == PackLifecycleState.REMOVED
    assert not pack_root.exists()
    assert unrelated.read_bytes() == b"preserve"


def test_pack_installer_uninstall_of_active_update_restores_rollback_predecessor(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry.json")
    installer = PackInstaller(
        registry=registry,
        install_root=tmp_path / "installed",
        acquirer=None,
        verifier=lambda _manifest, _root: PackVerification(True, True, "pack-verified"),
    )
    v1 = manifest_factory(version="1.0.0", artifacts=[], rollback_compatible_from=[])
    v2 = manifest_factory(version="2.0.0", artifacts=[], rollback_compatible_from=["1.0.0"])
    installer.install(v1, consent=True)
    installer.install(v2, consent=True)

    removed = installer.uninstall(v2.pack_id, v2.version)

    assert removed.state == PackLifecycleState.REMOVED
    assert registry.active(v1.pack_id).manifest.version == "1.0.0"
