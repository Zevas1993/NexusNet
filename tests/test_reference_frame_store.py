import json

from nexusnet.developmental.contracts import ReferenceFrameRecord
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


def test_reference_frame_store_accepts_positional_artifacts_dir(tmp_path):
    store = ReferenceFrameStore(tmp_path)

    frame = store.record(
        frame_id="frame:task:constructor",
        frame_type="task",
        subject_ref="task:reference-frame-store",
        facts=[{"claim": "Reference frame store accepts positional artifacts directories.", "source_ref": "tests"}],
        evidence_refs=["tests/test_reference_frame_store.py"],
    )

    assert frame["artifact_path"]
    assert (tmp_path / "developmental" / "reference-frames" / "frame_task_constructor.json").exists()


def test_reference_frame_store_returns_revalidatable_record(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="frame:artifact:model-valid",
        frame_type="artifact",
        subject_ref="artifact:reference-frame",
        facts=[{"claim": "Returned reference frames stay inside the validated contract.", "source_ref": "tests"}],
        evidence_refs=["tests/test_reference_frame_store.py"],
    )

    revalidated = ReferenceFrameRecord(**frame)

    assert revalidated.created_at == frame["created_at"]
    assert revalidated.artifact_path == frame["artifact_path"]


def test_reference_frame_store_summary_skips_invalid_persisted_records(tmp_path):
    frames_dir = tmp_path / "developmental" / "reference-frames"
    frames_dir.mkdir(parents=True)
    (frames_dir / "invalid.json").write_text(
        json.dumps(
            {
                "frame_id": "frame:invalid",
                "frame_type": "invalid-type",
                "subject_ref": "bad",
                "forbidden_extra": "skip-me",
            }
        ),
        encoding="utf-8",
    )

    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    summary = store.summary()

    assert summary["frame_count"] == 0
    assert summary["frames"] == []


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
