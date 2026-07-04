from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth.production_spine import DeepReplayBundleBuilder
from nexusnet.knowledge import KnowledgeArtifactCompiler
from nexusnet.security.artifact_trust import ArtifactScanRequest, ArtifactTrustRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_artifact_trust_registry_trusts_signed_safetensors_with_provenance():
    registry = ArtifactTrustRegistry()

    scan = registry.scan(
        ArtifactScanRequest(
            artifact_id="model::qwen-safetensors",
            artifact_type="model",
            uri="hf://Qwen/Qwen3.5-14B",
            format="safetensors",
            license_status="approved",
            provenance_refs=["https://huggingface.co/Qwen/Qwen3.5-14B"],
            checksum="sha256:abc123",
            signature_ref="sigstore::bundle::abc123",
            contains_pickle=False,
        )
    )

    assert scan["status_label"] == "LOCKED CANON"
    assert scan["authority"] == "NexusBrain"
    assert scan["status"] == "trusted"
    assert scan["trust_decision"] == "allow-shadow-or-active-use"
    assert scan["policy_scan"]["summary"]["allow_merge"] is True
    assert "safetensors_preferred" in scan["reason_codes"]


def test_artifact_trust_registry_quarantines_pickle_or_unsigned_artifacts():
    registry = ArtifactTrustRegistry()

    scan = registry.scan(
        {
            "artifact_id": "model::unsafe-pickle",
            "artifact_type": "model",
            "uri": "file://runtime/models/unsafe/pytorch_model.bin",
            "format": "pickle",
            "license_status": "needs_review",
            "provenance_refs": [],
            "checksum": "",
            "signature_ref": "",
            "contains_pickle": True,
        }
    )

    assert scan["status"] == "quarantined"
    assert scan["trust_decision"] == "blocked-pending-review"
    assert {
        "artifact_pickle_serialization_risk",
        "artifact_requires_checksum",
        "artifact_requires_signature_or_signed_manifest",
    }.issubset({finding["rule_id"] for finding in scan["trust_findings"]})
    assert scan["policy_scan"]["summary"]["allow_merge"] is False

    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["quarantined_count"] == 1
    assert scorecard["latest_scan"]["status"] == "quarantined"


def test_artifact_trust_registry_scans_signed_deep_replay_index(tmp_path):
    cycle_dir = tmp_path / "cycle"
    cycle_dir.mkdir()
    (cycle_dir / "training_report.json").write_text('{"status":"ok"}\n', encoding="utf-8")
    replay = DeepReplayBundleBuilder(cycle_dir).build(
        {
            "cycle_id": "cycle:trusted-replay",
            "replay_id": "replay:trusted",
            "signing_seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        }
    )
    registry = ArtifactTrustRegistry(artifacts_dir=tmp_path)

    summary = registry.scan_deep_replay_bundle(replay)

    assert summary["source"] == "deep_replay_bundle"
    assert summary["scan_count"] == replay["artifact_count"]
    assert summary["trusted_count"] == replay["artifact_count"]
    assert summary["quarantined_count"] == 0
    assert summary["signature_summary"]["signing_coverage"] == 1.0
    assert all(scan["metadata"]["signature_state"] == "signed_ed25519" for scan in summary["scans"])


def test_artifact_trust_registry_persists_long_artifact_ids_with_bounded_filename(tmp_path):
    registry = ArtifactTrustRegistry(artifacts_dir=tmp_path)
    artifact_id = "deep-replay::" + "::".join(
        f"signed/security/artifact-trust/deep-replay/child-execution/{index}"
        for index in range(12)
    )

    scan = registry.scan(
        {
            "artifact_id": artifact_id,
            "artifact_type": "document",
            "uri": "file://runtime/deep-replay/execution_report.json",
            "format": "unknown",
            "license_status": "approved",
            "provenance_refs": ["deep-replay-bundle"],
            "checksum": "sha256:abc123",
            "signature_ref": "ed25519:test",
            "contains_pickle": False,
        }
    )

    artifact_path = Path(scan["artifact_path"])
    assert artifact_path.exists()
    assert len(artifact_path.name) <= 120
    assert scan["artifact_id"] == artifact_id
    assert registry.summary()["latest_scan"]["artifact_id"] == artifact_id


def _build_signed_replay(tmp_path):
    cycle_dir = tmp_path / "cycle"
    cycle_dir.mkdir()
    (cycle_dir / "training_report.json").write_text('{"status":"ok"}\n', encoding="utf-8")
    return cycle_dir, DeepReplayBundleBuilder(cycle_dir).build(
        {
            "cycle_id": "cycle:trusted-replay",
            "replay_id": "replay:trusted",
            "signing_seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        }
    )


def _rewrite_index(index_path, records):
    index_path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def test_artifact_trust_registry_quarantines_forged_ed25519_signature(tmp_path):
    cycle_dir, replay = _build_signed_replay(tmp_path)
    index_path = Path(replay["artifacts"]["artifact_index_path"])
    records = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Forge: flip the signature on a signed record while leaving the claim intact.
    forged = False
    for record in records:
        if record.get("signature_state") == "signed_ed25519" and record.get("signature"):
            sig = record["signature"]
            record["signature"] = ("0" if sig[0] != "0" else "1") + sig[1:]
            forged = True
            break
    assert forged, "expected at least one signed record to forge"
    _rewrite_index(index_path, records)

    summary = ArtifactTrustRegistry(artifacts_dir=tmp_path).scan_deep_replay_bundle(replay)

    assert summary["quarantined_count"] >= 1
    forged_scans = [
        scan
        for scan in summary["scans"]
        if any(f["rule_id"] == "artifact_signature_verification_failed" for f in scan["trust_findings"])
    ]
    assert forged_scans, "forged signature must produce a verification-failed finding"
    assert all(scan["status"] == "quarantined" for scan in forged_scans)


def test_artifact_trust_registry_quarantines_tampered_artifact_content(tmp_path):
    cycle_dir, replay = _build_signed_replay(tmp_path)
    # Tamper the on-disk content so its hash no longer matches the signed claim.
    (cycle_dir / "training_report.json").write_text('{"status":"tampered"}\n', encoding="utf-8")

    summary = ArtifactTrustRegistry(artifacts_dir=tmp_path).scan_deep_replay_bundle(replay)

    tampered_scans = [
        scan
        for scan in summary["scans"]
        if any(f["rule_id"] == "artifact_checksum_mismatch" for f in scan["trust_findings"])
    ]
    assert tampered_scans, "tampered content must produce a checksum-mismatch finding"
    assert all(scan["status"] == "quarantined" for scan in tampered_scans)


def test_artifact_trust_registry_marks_blocked_lifecycle_replay_not_promotion_ready(tmp_path):
    cycle_dir = tmp_path / "cycle"
    lifecycle_dir = cycle_dir / "growth-lifecycles" / "blocked"
    lifecycle_dir.mkdir(parents=True)
    (lifecycle_dir / "lifecycle_report.json").write_text(
        (
            '{"status":"closed_loop_blocked",'
            '"growth_engine_gate":{"allowed":false,'
            '"blockers":["growth_engine_adapter_training_gate_blocked"]},'
            '"blocked_reasons":["growth_engine_adapter_training_gate_blocked"]}\n'
        ),
        encoding="utf-8",
    )
    replay = DeepReplayBundleBuilder(cycle_dir).build(
        {
            "cycle_id": "cycle:blocked-growth-replay",
            "replay_id": "replay:blocked-growth",
            "signing_seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        }
    )
    registry = ArtifactTrustRegistry(artifacts_dir=tmp_path)

    summary = registry.scan_deep_replay_bundle(replay)

    assert summary["trusted_count"] == replay["artifact_count"]
    assert summary["quarantined_count"] == 0
    assert summary["promotion_allowed"] is False
    assert "growth_engine_adapter_training_gate_blocked" in summary["promotion_blockers"]
    assert summary["blocked_lifecycle_count"] == 1


def test_artifact_trust_registry_quarantines_knowledge_artifact_with_blocked_source_refs(tmp_path):
    project_root = make_project(tmp_path)
    allowed_path = project_root / "docs" / "trusted-kac-source.md"
    private_path = project_root / ".secrets" / "raw-private-note.md"
    allowed_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.parent.mkdir(parents=True, exist_ok=True)
    allowed_path.write_text("Trusted KAC source refs may enter the compiled artifact.", encoding="utf-8")
    private_path.write_text("private raw material must stay blocked", encoding="utf-8")
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path, source_root=project_root)
    artifact = compiler.compile(
        {
            "task_family": "architecture_review",
            "source_refs": ["docs/trusted-kac-source.md", ".secrets/raw-private-note.md"],
            "scope": {"rbac_scope": ["operator"]},
        }
    )
    registry = ArtifactTrustRegistry(artifacts_dir=tmp_path)

    preview = registry.preview_knowledge_artifact(artifact)
    assert preview["status"] == "quarantined"
    assert preview["persisted"] is False
    assert registry.scorecard()["scan_count"] == 0

    scan = registry.scan_knowledge_artifact(artifact)

    assert scan["status"] == "quarantined"
    assert scan["persisted"] is True
    assert scan["trust_decision"] == "blocked-pending-review"
    assert "kac_source_ref_security_gate_blocked" in scan["reason_codes"]
    assert scan["metadata"]["source_ref_security_gate"]["blocked_count"] == 1
    assert scan["metadata"]["blocked_source_refs"][0]["reason"] == "source_ref_private_path_blocked"
    assert "private raw material" not in str(scan)
    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["latest_scan"]["metadata"]["blocked_source_refs"][0]["source_ref"] == ".secrets/raw-private-note.md"


def test_artifact_trust_registry_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/artifact-trust/scans",
        json={
            "artifact_id": "adapter::api-safetensors",
            "artifact_type": "adapter",
            "uri": "runtime/artifacts/adapters/api/adapter.safetensors",
            "format": "safetensors",
            "license_status": "approved",
            "provenance_refs": ["docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"],
            "checksum": "sha256:def456",
            "signature_ref": "sigstore::bundle::def456",
            "contains_pickle": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "trusted"

    summary = client.get("/ops/brain/artifact-trust")
    assert summary.status_code == 200
    assert summary.json()["scan_count"] == 1

    scorecard = client.get("/ops/brain/canon/artifact-trust-registry")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "pickle_scanning" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "artifact-trust-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["artifact_trust_registry_scorecard"]["scan_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "artifact-trust-cockpit"}).json()
    assert blackbox["scorecard_refs"]["artifact_trust_registry"] == "/ops/brain/canon/artifact-trust-registry"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Artifact Trust Registry" in ui.text
    assert "artifactTrustRegistryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderArtifactTrustRegistryScorecard" in app_js
    assert "/ops/brain/canon/artifact-trust-registry" in app_js
