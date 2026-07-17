import json

import pytest

from nexusnet.runtime.accelerator_packs import registry as registry_module
from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.registry import RegistryError, RuntimePackRegistry


def _advance_to_verifying(registry, pack_id: str, version: str) -> None:
    registry.transition(pack_id, version, PackLifecycleState.DOWNLOADING)
    registry.transition(pack_id, version, PackLifecycleState.STAGED, install_ref=f"packs/{pack_id}/{version}")
    registry.transition(pack_id, version, PackLifecycleState.VERIFYING)


def test_registry_restores_atomic_active_and_previous_versions_then_rolls_back(tmp_path, manifest_factory):
    path = tmp_path / "runtime" / "accelerator-packs" / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    first = manifest_factory(version="1.0.0")
    second = manifest_factory(version="1.1.0", rollback_compatible_from=["1.0.0"])

    registry.register_manifest(first)
    _advance_to_verifying(registry, first.pack_id, first.version)
    registry.activate(first.pack_id, first.version)
    registry.register_manifest(second)
    _advance_to_verifying(registry, second.pack_id, second.version)
    registry.activate(second.pack_id, second.version)

    restored = RuntimePackRegistry(path)
    assert restored.active(first.pack_id).manifest.version == "1.1.0"
    assert restored.get(first.pack_id, "1.0.0").state == PackLifecycleState.ROLLBACK_AVAILABLE
    assert restored.snapshot().previous_versions[first.pack_id] == "1.0.0"

    restored.rollback(first.pack_id, reason_code="new-version-crashed")
    assert restored.active(first.pack_id).manifest.version == "1.0.0"
    assert restored.get(first.pack_id, "1.1.0").state == PackLifecycleState.QUARANTINED
    assert not list(path.parent.glob(f"{path.name}.*.tmp"))


def test_registry_rejects_invalid_transitions_and_corrupt_state_without_private_detail(tmp_path, manifest_factory):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)

    with pytest.raises(RegistryError, match="lifecycle-transition-invalid") as invalid:
        registry.activate(manifest.pack_id, manifest.version)
    assert str(tmp_path) not in str(invalid.value)

    path.write_text('{"secret":"C:/Users/Private/model.gguf"}', encoding="utf-8")
    with pytest.raises(RegistryError, match="registry-invalid") as corrupt:
        RuntimePackRegistry(path)
    assert "Private" not in str(corrupt.value)


def test_registry_persist_failure_preserves_memory_and_disk_and_cleans_temp_file(
    tmp_path,
    manifest_factory,
    monkeypatch,
):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)
    before_snapshot = registry.snapshot()
    before_disk = path.read_bytes()

    def fail_replace(source, destination):
        raise OSError("C:/Users/Private/registry-v1.json is locked")

    monkeypatch.setattr(registry_module.os, "replace", fail_replace)
    with pytest.raises(RegistryError, match="registry-persist-failed") as failure:
        registry.transition(manifest.pack_id, manifest.version, PackLifecycleState.DOWNLOADING)

    assert "Private" not in str(failure.value)
    assert registry.snapshot() == before_snapshot
    assert path.read_bytes() == before_disk
    assert not list(path.parent.glob(f"{path.name}.*.tmp"))


def test_registry_snapshots_and_reason_codes_are_deeply_immutable(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    manifest = manifest_factory()
    record = registry.register_manifest(manifest)
    snapshot = registry.snapshot()

    with pytest.raises(TypeError):
        snapshot.records["other@1.0.0"] = record
    with pytest.raises(TypeError):
        snapshot.active_versions[manifest.pack_id] = manifest.version
    with pytest.raises(AttributeError):
        record.reason_codes.append("tampered")


@pytest.mark.parametrize(
    "install_ref",
    [
        "",
        ".",
        "../private",
        "/absolute/private",
        "C:/Users/Private/model",
        "packs\\private",
        "packs/private\x00model",
    ],
)
def test_registry_rejects_unsafe_install_references_without_state_drift(
    tmp_path,
    manifest_factory,
    install_ref,
):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    manifest = manifest_factory()
    registry.register_manifest(manifest)
    registry.transition(manifest.pack_id, manifest.version, PackLifecycleState.DOWNLOADING)

    with pytest.raises(RegistryError, match="registry-record-invalid") as invalid:
        registry.transition(
            manifest.pack_id,
            manifest.version,
            PackLifecycleState.STAGED,
            install_ref=install_ref,
        )

    assert "Private" not in str(invalid.value)
    assert registry.get(manifest.pack_id, manifest.version).state == PackLifecycleState.DOWNLOADING


def test_registry_rejects_dangling_active_pointers_on_restart(tmp_path, manifest_factory):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["active_versions"][manifest.pack_id] = "C:/Users/Private/missing"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RegistryError, match="registry-invalid") as invalid:
        RuntimePackRegistry(path)

    assert "Private" not in str(invalid.value)


def test_registry_requires_declared_rollback_compatibility_before_replacing_active_pack(
    tmp_path,
    manifest_factory,
):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    first = manifest_factory(version="1.0.0")
    second = manifest_factory(version="1.1.0", rollback_compatible_from=[])
    registry.register_manifest(first)
    _advance_to_verifying(registry, first.pack_id, first.version)
    registry.activate(first.pack_id, first.version)
    registry.register_manifest(second)
    _advance_to_verifying(registry, second.pack_id, second.version)

    with pytest.raises(RegistryError, match="rollback-incompatible"):
        registry.activate(second.pack_id, second.version)

    assert registry.active(first.pack_id).manifest.version == "1.0.0"
    assert registry.get(second.pack_id, second.version).state == PackLifecycleState.VERIFYING


def test_registry_rotates_only_the_immediate_previous_version_across_three_activations(
    tmp_path,
    manifest_factory,
):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifests = [
        manifest_factory(version="1.0.0"),
        manifest_factory(version="1.1.0", rollback_compatible_from=["1.0.0"]),
        manifest_factory(version="1.2.0", rollback_compatible_from=["1.1.0"]),
    ]
    for manifest in manifests:
        registry.register_manifest(manifest)
        _advance_to_verifying(registry, manifest.pack_id, manifest.version)
        registry.activate(manifest.pack_id, manifest.version)

    restored = RuntimePackRegistry(path)
    pack_id = manifests[0].pack_id
    assert restored.active(pack_id).manifest.version == "1.2.0"
    assert restored.snapshot().previous_versions[pack_id] == "1.1.0"
    assert restored.get(pack_id, "1.1.0").state == PackLifecycleState.ROLLBACK_AVAILABLE
    assert restored.get(pack_id, "1.0.0").state == PackLifecycleState.STAGED
    assert restored.rollback(pack_id, reason_code="latest-version-failed").manifest.version == "1.1.0"


def test_registry_can_quarantine_the_active_pack_then_restore_previous_version(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    first = manifest_factory(version="1.0.0")
    second = manifest_factory(version="1.1.0", rollback_compatible_from=["1.0.0"])
    for manifest in (first, second):
        registry.register_manifest(manifest)
        _advance_to_verifying(registry, manifest.pack_id, manifest.version)
        registry.activate(manifest.pack_id, manifest.version)

    registry.transition(
        second.pack_id,
        second.version,
        PackLifecycleState.QUARANTINED,
        reason_code="worker-crashed",
    )
    with pytest.raises(RegistryError, match="active-pack-unavailable"):
        registry.active(second.pack_id)

    restored = registry.rollback(second.pack_id, reason_code="worker-crashed")
    assert restored.manifest.version == "1.0.0"
    assert registry.active(second.pack_id).manifest.version == "1.0.0"
    assert "worker-crashed" in registry.get(second.pack_id, second.version).reason_codes


def test_removing_previous_version_does_not_clear_the_newer_active_pointer(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    first = manifest_factory(version="1.0.0")
    second = manifest_factory(version="1.1.0", rollback_compatible_from=["1.0.0"])
    for manifest in (first, second):
        registry.register_manifest(manifest)
        _advance_to_verifying(registry, manifest.pack_id, manifest.version)
        registry.activate(manifest.pack_id, manifest.version)

    registry.transition(first.pack_id, first.version, PackLifecycleState.REMOVED)

    assert registry.active(second.pack_id).manifest.version == "1.1.0"
    assert first.pack_id not in registry.snapshot().previous_versions
    assert registry.get(first.pack_id, first.version).install_ref is None


def test_transition_rejects_malformed_state_and_reason_code_without_drift(tmp_path, manifest_factory):
    registry = RuntimePackRegistry(tmp_path / "registry-v1.json")
    manifest = manifest_factory()
    before = registry.register_manifest(manifest)

    with pytest.raises(RegistryError, match="lifecycle-transition-invalid"):
        registry.transition(manifest.pack_id, manifest.version, "C:/Users/Private")
    with pytest.raises(RegistryError, match="reason-code-invalid") as invalid_reason:
        registry.transition(
            manifest.pack_id,
            manifest.version,
            PackLifecycleState.DOWNLOADING,
            reason_code="C:/Users/Private",
        )

    assert "Private" not in str(invalid_reason.value)
    assert registry.get(manifest.pack_id, manifest.version) == before


def test_registry_rejects_staged_records_without_install_references_on_restart(tmp_path, manifest_factory):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["records"][f"{manifest.pack_id}@{manifest.version}"]["state"] = "staged"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RegistryError, match="registry-invalid"):
        RuntimePackRegistry(path)


def test_registry_rejects_private_or_malformed_persisted_reason_codes(tmp_path, manifest_factory):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["records"][f"{manifest.pack_id}@{manifest.version}"]["reason_codes"] = [
        "C:/Users/Private/model.gguf"
    ]
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RegistryError, match="registry-invalid") as invalid:
        RuntimePackRegistry(path)

    assert "Private" not in str(invalid.value)
