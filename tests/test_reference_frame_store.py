from nexusnet.developmental.reference_frames import ReferenceFrameStore


def test_reference_frame_store_records_local_models(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="frame:project:nexusnet",
        frame_type="project",
        subject_ref="repo:NexusNet",
        facts=[{"claim": "Developmental cortex is refs-only until code-backed.", "source_ref": "docs/assimilation"}],
        evidence_refs=["docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md"],
        uncertainty=0.2,
    )

    assert frame["frame_id"] == "frame:project:nexusnet"
    assert frame["runtime_state"] == "live-bound"
    assert frame["mutation_allowed"] is False
    assert frame["artifact_path"]


def test_reference_frame_store_rejects_mutation_claims(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="frame:unsafe",
        frame_type="tool",
        subject_ref="tool:browser",
        facts=[{"claim": "Browser tool may mutate production without review.", "source_ref": "bad"}],
        evidence_refs=[],
        uncertainty=0.7,
    )

    assert frame["runtime_state"] == "degraded"
    assert "reference_frame_requires_evidence_refs" in frame["findings"]
