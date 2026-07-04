from nexusnet.evidence.store import EvidenceStore


def test_evidence_store_hash_chains_records(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)

    first = store.append(kind="eval", subject_ref="suite:route", payload={"score": 0.91}, source_refs=["eval:route"])
    second = store.append(kind="policy", subject_ref="policy:tool", payload={"blocked": False}, source_refs=["policy:scan"])

    assert first["content_hash"].startswith("sha256:")
    assert second["previous_hash"] == first["content_hash"]
    assert second["content_hash"] != first["content_hash"]


def test_evidence_store_projection_counts_by_kind(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    store.append(kind="eval", subject_ref="suite:route", payload={"score": 0.91}, source_refs=["eval:route"])
    store.append(kind="eval", subject_ref="suite:cache", payload={"score": 0.83}, source_refs=["eval:cache"])

    projection = store.projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"]["eval"] == 2
    assert projection["runtime_state"] == "live-bound"
