import json
import math
from pathlib import Path

import pytest

from nexusnet.evidence.contracts import EvidenceRecord
from nexusnet.evidence.store import EvidenceStore


def test_evidence_store_hash_chains_records(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)

    first = store.append(
        kind="eval",
        subject_ref="suite:route",
        payload={"score": 0.91},
        source_refs=["eval:route"],
    )
    second = store.append(
        kind="policy",
        subject_ref="policy:tool",
        payload={"blocked": False},
        source_refs=["policy:scan"],
    )

    assert first["content_hash"].startswith("sha256:")
    assert second["previous_hash"] == first["content_hash"]
    assert second["content_hash"] != first["content_hash"]


def test_evidence_store_projection_counts_by_kind(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    store.append(
        kind="eval",
        subject_ref="suite:route",
        payload={"score": 0.91},
        source_refs=["eval:route"],
    )
    store.append(
        kind="eval",
        subject_ref="suite:cache",
        payload={"score": 0.83},
        source_refs=["eval:cache"],
    )

    projection = store.projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"]["eval"] == 2
    assert projection["runtime_state"] == "live-bound"


def test_evidence_store_returned_and_persisted_records_revalidate(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)

    record = store.append(
        kind="eval",
        subject_ref="suite:model-valid",
        payload={"score": 0.97},
        source_refs=["tests/test_evidence_store.py"],
    )

    revalidated = EvidenceRecord(**record)
    persisted = json.loads(Path(record["artifact_path"]).read_text(encoding="utf-8"))

    assert revalidated.content_hash == record["content_hash"]
    assert EvidenceRecord(**persisted).content_hash == record["content_hash"]


def test_evidence_store_fresh_projection_sees_persisted_records(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    first = store.append(
        kind="eval",
        subject_ref="suite:route",
        payload={"score": 0.91},
        source_refs=["eval:route"],
    )
    second = store.append(
        kind="policy",
        subject_ref="policy:tool",
        payload={"blocked": False},
        source_refs=["policy:scan"],
    )

    projection = EvidenceStore(artifacts_dir=tmp_path).projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"] == {"eval": 1, "policy": 1}
    assert projection["latest_hash"] == second["content_hash"]
    assert projection["latest_hash"] != first["content_hash"]


def test_evidence_store_projection_skips_bad_disk_files(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    valid = store.append(
        kind="eval",
        subject_ref="suite:valid",
        payload={"score": 0.91},
        source_refs=["eval:valid"],
    )
    records_dir = tmp_path / "evidence" / "records"
    (records_dir / "malformed.json").write_text("{", encoding="utf-8")
    (records_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (records_dir / "model-invalid.json").write_text(
        json.dumps({"record_id": "missing-required-fields"}),
        encoding="utf-8",
    )

    projection = EvidenceStore(artifacts_dir=tmp_path).projection()

    assert projection["record_count"] == 1
    assert projection["latest_hash"] == valid["content_hash"]


def test_evidence_store_failed_disk_write_leaves_no_phantom_record(tmp_path, monkeypatch):
    store = EvidenceStore(artifacts_dir=tmp_path)

    def fail_write(self, *args, **kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "write_text", fail_write)

    with pytest.raises(OSError, match="disk unavailable"):
        store.append(
            kind="eval",
            subject_ref="suite:write-failure",
            payload={"score": 0.91},
            source_refs=["eval:write-failure"],
        )

    assert store.projection()["record_count"] == 0


def test_evidence_store_rejects_non_finite_payloads_without_persisting(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)

    with pytest.raises(ValueError):
        store.append(
            kind="eval",
            subject_ref="suite:nan",
            payload={"score": math.inf},
            source_refs=["eval:nan"],
        )

    assert store.projection()["record_count"] == 0
    assert list((tmp_path / "evidence" / "records").glob("*.json")) == []


def test_evidence_store_duplicate_persisted_records_do_not_inflate_counts(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    record = store.append(
        kind="eval",
        subject_ref="suite:duplicate",
        payload={"score": 0.91},
        source_refs=["eval:duplicate"],
    )
    records_dir = tmp_path / "evidence" / "records"
    duplicate_path = records_dir / "duplicate.json"
    duplicate_path.write_text(Path(record["artifact_path"]).read_text(encoding="utf-8"), encoding="utf-8")

    projection = EvidenceStore(artifacts_dir=tmp_path).projection()

    assert projection["record_count"] == 1
    assert projection["kind_counts"]["eval"] == 1
    assert projection["latest_hash"] == record["content_hash"]


def test_evidence_store_skips_tampered_disk_record_claiming_valid_hash(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    first = store.append(
        kind="eval",
        subject_ref="suite:canonical",
        payload={"score": 0.91},
        source_refs=["eval:canonical"],
    )
    second = store.append(
        kind="policy",
        subject_ref="policy:canonical",
        payload={"blocked": False},
        source_refs=["policy:canonical"],
    )
    records_dir = tmp_path / "evidence" / "records"
    tampered = json.loads(Path(first["artifact_path"]).read_text(encoding="utf-8"))
    tampered["kind"] = "policy"
    tampered["payload"] = {"score": 0.0, "tampered": True}
    (records_dir / "0000-tampered.json").write_text(json.dumps(tampered), encoding="utf-8")

    projection = EvidenceStore(artifacts_dir=tmp_path).projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"] == {"eval": 1, "policy": 1}
    assert projection["latest_hash"] == second["content_hash"]


def test_evidence_store_returned_in_memory_record_is_defensive_copy():
    store = EvidenceStore()
    first = store.append(
        kind="eval",
        subject_ref="suite:in-memory",
        payload={"score": 0.91},
        source_refs=["eval:in-memory"],
    )
    second = store.append(
        kind="policy",
        subject_ref="policy:in-memory",
        payload={"blocked": False},
        source_refs=["policy:in-memory"],
    )

    first["kind"] = "policy"
    first["payload"] = {"score": 0.0, "tampered": True}

    projection = store.projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"] == {"eval": 1, "policy": 1}
    assert projection["latest_hash"] == second["content_hash"]


def test_evidence_store_skips_hash_invalid_internal_memory_records():
    store = EvidenceStore()
    record = store.append(
        kind="eval",
        subject_ref="suite:internal",
        payload={"score": 0.91},
        source_refs=["eval:internal"],
    )
    store._records[0] = {**record, "kind": "policy", "payload": {"score": 0.0, "tampered": True}}

    projection = store.projection()

    assert projection["record_count"] == 0
    assert projection["kind_counts"] == {}
    assert projection["latest_hash"] == ""
