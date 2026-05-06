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


def test_reference_frame_store_exports_contracts_from_package():
    from nexusnet.developmental import FrameType, ReferenceFrameRecord as ExportedRecord, ReferenceFrameStore as ExportedStore

    assert FrameType is not None
    assert ExportedRecord is ReferenceFrameRecord
    assert ExportedStore is ReferenceFrameStore


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
    assert type(tmp_path)(frame["artifact_path"]).parent == tmp_path / "developmental" / "reference-frames"
    assert type(tmp_path)(frame["artifact_path"]).exists()


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


def test_reference_frame_store_safely_persists_windows_separator_ids(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="..\\escaped\\frame",
        frame_type="artifact",
        subject_ref="artifact:escaped",
        facts=[{"claim": "Unsafe path separators are reduced to a safe artifact file.", "source_ref": "tests"}],
        evidence_refs=["tests/test_reference_frame_store.py"],
    )

    frames_dir = tmp_path / "developmental" / "reference-frames"
    artifact_path = frame["artifact_path"]
    resolved_artifact_path = artifact_path and type(tmp_path)(artifact_path).resolve()

    assert resolved_artifact_path is not None
    assert resolved_artifact_path.parent == frames_dir.resolve()
    assert resolved_artifact_path.exists()
    assert not (frames_dir / ".." / "escaped").exists()
    assert store.summary()["frame_count"] == 1


def test_reference_frame_store_summary_dedupes_duplicate_disk_frames(tmp_path):
    frames_dir = tmp_path / "developmental" / "reference-frames"
    frames_dir.mkdir(parents=True)
    first = ReferenceFrameRecord(
        frame_id="frame:duplicate",
        frame_type="artifact",
        subject_ref="artifact:first",
        evidence_refs=["tests/first"],
        created_at="2026-05-06T00:00:01+00:00",
    ).model_dump(mode="json")
    second = ReferenceFrameRecord(
        frame_id="frame:duplicate",
        frame_type="artifact",
        subject_ref="artifact:second",
        evidence_refs=["tests/second"],
        created_at="2026-05-06T00:00:02+00:00",
    ).model_dump(mode="json")
    (frames_dir / "a.json").write_text(json.dumps(first), encoding="utf-8")
    (frames_dir / "b.json").write_text(json.dumps(second), encoding="utf-8")

    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    summary = store.summary()

    assert summary["frame_count"] == 1
    assert summary["frames"][0]["frame_id"] == "frame:duplicate"
    assert summary["frames"][0]["subject_ref"] == "artifact:second"
    assert summary["frames"][0]["created_at"] == "2026-05-06T00:00:02+00:00"


def test_reference_frame_store_summary_skips_non_object_json_files(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)
    frame = store.record(
        frame_id="frame:valid:memory",
        frame_type="memory",
        subject_ref="memory:valid",
        facts=[{"claim": "Valid in-memory frames survive corrupt disk files.", "source_ref": "tests"}],
        evidence_refs=["tests/test_reference_frame_store.py"],
    )
    frames_dir = tmp_path / "developmental" / "reference-frames"
    (frames_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")

    summary = store.summary()

    assert summary["frame_count"] == 1
    assert summary["frames"][0]["frame_id"] == frame["frame_id"]


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
