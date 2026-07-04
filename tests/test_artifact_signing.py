from __future__ import annotations

import json

import pytest

from nexusnet.growth.production_spine import DeepReplayBundleBuilder, _validate_lifecycle_replay_consistency
from nexusnet.security.artifact_signing import ArtifactSigner
from nexusnet.security.ed25519 import Ed25519Keypair
from nexusnet.security.project_key_store import ProjectLocalSigningKeyStore


def test_artifact_signer_signs_file_hash_with_ed25519(tmp_path):
    artifact_path = tmp_path / "artifact.json"
    artifact_path.write_text(json.dumps({"value": 42}, sort_keys=True), encoding="utf-8")
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")

    signature_record = ArtifactSigner.from_seed(seed).sign_file(artifact_path, artifact_type="demo_artifact")

    assert signature_record["signature_state"] == "signed_ed25519"
    assert signature_record["artifact_path"] == str(artifact_path)
    assert signature_record["artifact_type"] == "demo_artifact"
    assert signature_record["hash"].startswith("sha256:")
    assert signature_record["public_key"] == Ed25519Keypair.from_seed(seed).public_key_hex
    assert Ed25519Keypair.verify(
        bytes.fromhex(signature_record["public_key"]),
        signature_record["signed_payload"].encode("utf-8"),
        bytes.fromhex(signature_record["signature"]),
    )


def test_security_package_exports_artifact_signing_primitives():
    from nexusnet.security import ArtifactSigner as ExportedArtifactSigner
    from nexusnet.security import Ed25519Keypair as ExportedEd25519Keypair
    from nexusnet.security import ProjectLocalSigningKeyStore as ExportedProjectLocalSigningKeyStore

    assert ExportedArtifactSigner is ArtifactSigner
    assert ExportedEd25519Keypair is Ed25519Keypair
    assert ExportedProjectLocalSigningKeyStore is ProjectLocalSigningKeyStore


def test_project_local_signing_key_store_encrypts_seed_without_persisting_secret(tmp_path):
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    passphrase = "operator-local-passphrase"
    key_path = tmp_path / "runtime" / "security" / "signing" / "artifact_signing_key.enc.json"

    record = ProjectLocalSigningKeyStore.create(key_path, seed=seed, passphrase=passphrase)

    assert record["storage_scope"] == "project_local_encrypted_file"
    assert record["secret_persisted"] is False
    assert record["key_file_path"] == str(key_path)
    encrypted_text = key_path.read_text(encoding="utf-8")
    assert seed.hex() not in encrypted_text
    assert passphrase not in encrypted_text
    assert ProjectLocalSigningKeyStore.load_seed(key_path, passphrase=passphrase) == seed
    with pytest.raises(ValueError, match="decrypt"):
        ProjectLocalSigningKeyStore.load_seed(key_path, passphrase="wrong-passphrase")


def test_deep_replay_bundle_signs_artifact_index_records_when_key_is_configured(tmp_path):
    cycle_dir = tmp_path / "cycle"
    cycle_dir.mkdir()
    (cycle_dir / "training_report.json").write_text(json.dumps({"status": "ok"}, sort_keys=True), encoding="utf-8")
    seed_hex = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"

    replay = DeepReplayBundleBuilder(cycle_dir).build(
        {"cycle_id": "cycle:signed", "replay_id": "replay:signed", "signing_seed_hex": seed_hex}
    )

    assert replay["signature_policy"]["current_signature_state"] == "signed_ed25519"
    assert replay["signature_policy"]["real_signing_blocker"] is None
    assert replay["signature_summary"]["signed_count"] == replay["artifact_count"]
    assert replay["signature_summary"]["unsigned_count"] == 0
    assert replay["signature_summary"]["signing_coverage"] == 1.0
    artifact_records = [
        json.loads(line)
        for line in open(replay["artifacts"]["artifact_index_path"], encoding="utf-8")
        if line.strip()
    ]
    assert artifact_records
    assert all(record["signature_state"] == "signed_ed25519" for record in artifact_records)
    for record in artifact_records:
        assert Ed25519Keypair.verify(
            bytes.fromhex(record["public_key"]),
            record["signed_payload"].encode("utf-8"),
            bytes.fromhex(record["signature"]),
        )

    consistency = _validate_lifecycle_replay_consistency(
        {
            "training_report_path": str(cycle_dir / "training_report.json"),
            "deep_replay_artifact_index_path": replay["artifacts"]["artifact_index_path"],
        },
        replay,
    )

    assert consistency["passed"] is True
    assert consistency["expected_signature_state"] == "signed_ed25519"
    assert consistency["bridge_signature_state_mismatches"] == []


def test_deep_replay_bundle_signs_from_project_local_encrypted_key_file(tmp_path):
    cycle_dir = tmp_path / "cycle"
    cycle_dir.mkdir()
    (cycle_dir / "training_report.json").write_text(json.dumps({"status": "ok"}, sort_keys=True), encoding="utf-8")
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    passphrase = "project-local-key-passphrase"
    key_file = tmp_path / "runtime" / "security" / "signing" / "artifact_signing_key.enc.json"
    ProjectLocalSigningKeyStore.create(key_file, seed=seed, passphrase=passphrase)

    replay = DeepReplayBundleBuilder(cycle_dir).build(
        {
            "cycle_id": "cycle:signed-file",
            "replay_id": "replay:signed-file",
            "signing_key_file": str(key_file),
            "signing_key_passphrase": passphrase,
        }
    )

    assert replay["signature_policy"]["current_signature_state"] == "signed_ed25519"
    assert replay["signature_policy"]["signing_key_source"] == "project_local_encrypted_key_file"
    assert replay["signature_policy"]["signing_configuration_state"] == "configured_valid"
    assert replay["signature_policy"]["signing_secret_persisted"] is False
    assert replay["signature_policy"]["encrypted_key_file_persisted"] is True
    assert replay["signature_policy"]["signing_key_storage_scope"] == "project_local_encrypted_file"
    assert replay["signature_summary"]["signing_coverage"] == 1.0
    replay_text = open(replay["artifacts"]["deep_replay_bundle_path"], encoding="utf-8").read()
    index_text = open(replay["artifacts"]["artifact_index_path"], encoding="utf-8").read()
    assert seed.hex() not in replay_text
    assert seed.hex() not in index_text
    assert passphrase not in replay_text
    assert passphrase not in index_text


def test_replay_consistency_rejects_signed_artifact_with_invalid_signature(tmp_path):
    cycle_dir = tmp_path / "cycle"
    cycle_dir.mkdir()
    artifact_path = cycle_dir / "training_report.json"
    artifact_path.write_text(json.dumps({"status": "ok"}, sort_keys=True), encoding="utf-8")
    seed_hex = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    replay = DeepReplayBundleBuilder(cycle_dir).build(
        {"cycle_id": "cycle:signed", "replay_id": "replay:signed", "signing_seed_hex": seed_hex}
    )

    artifact_index_path = replay["artifacts"]["artifact_index_path"]
    records = [json.loads(line) for line in open(artifact_index_path, encoding="utf-8") if line.strip()]
    for record in records:
        if record["artifact_path"] == str(artifact_path):
            record["signature"] = "00" * 64
    with open(artifact_index_path, "w", encoding="utf-8") as handle:
        handle.write("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))

    consistency = _validate_lifecycle_replay_consistency(
        {
            "training_report_path": str(artifact_path),
            "deep_replay_artifact_index_path": artifact_index_path,
        },
        replay,
    )

    assert consistency["passed"] is False
    assert "bridge_signature_verification_failures" in consistency["integrity_blockers"]
    assert consistency["bridge_signature_verification_failures"] == ["training_report_path"]
