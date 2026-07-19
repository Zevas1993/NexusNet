from __future__ import annotations

from nexusnet.evidence.standards import EvidenceStandardsRuntime


def test_evidence_dag_lineage_credentials_and_transparency_receipts(tmp_path):
    runtime = EvidenceStandardsRuntime(artifacts_dir=tmp_path, signing_key=b"evidence-key")
    source = runtime.add_node(
        kind="source",
        subject_ref="paper:1",
        payload={"title": "Pinned memory study"},
        source_refs=["doi:1"],
        parent_refs=[],
    )
    result = runtime.add_node(
        kind="eval-result",
        subject_ref="eval:1",
        payload={"score": 0.94},
        source_refs=["trace:1"],
        parent_refs=[source["content_hash"]],
    )

    assert runtime.verify_dag()["valid"] is True
    assert result["parent_refs"] == [source["content_hash"]]
    time_receipt = runtime.issue_time_receipt(subject_ref=result["content_hash"])
    transparency = runtime.append_transparency_receipt(subject_ref=result["content_hash"], evidence_refs=["eval:1"])
    credential = runtime.issue_content_credential(
        subject_ref="artifact:report",
        claim_refs=[result["content_hash"]],
        issuer_ref="NexusBrain",
    )
    assert runtime.verify_signed_receipt(time_receipt)["valid"] is True
    assert runtime.verify_signed_receipt(transparency)["valid"] is True
    assert runtime.verify_signed_receipt(credential)["valid"] is True
    assert time_receipt["assurance"] == "local-signed-clock-not-external-tsa"
    assert transparency["standard_posture"] == "scitt-inspired-not-standards-conformant"


def test_provenance_crate_is_replayable_and_source_grounded(tmp_path):
    runtime = EvidenceStandardsRuntime(artifacts_dir=tmp_path, signing_key=b"evidence-key")
    source = runtime.add_node(kind="source", subject_ref="dataset:1", payload={}, source_refs=["sha256:data"], parent_refs=[])
    artifact = runtime.add_node(
        kind="artifact",
        subject_ref="model:adapter",
        payload={"format": "safetensors"},
        source_refs=["training:run-1"],
        parent_refs=[source["content_hash"]],
    )
    crate = runtime.export_provenance_crate(crate_id="crate:1", root_refs=[artifact["content_hash"]])

    assert crate["status"] == "exported"
    assert {item["content_hash"] for item in crate["entities"]} == {source["content_hash"], artifact["content_hash"]}
    assert crate["replay_order"] == [source["content_hash"], artifact["content_hash"]]
