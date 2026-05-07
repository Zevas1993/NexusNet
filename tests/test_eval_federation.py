import json
from pathlib import Path

import pytest

from nexusnet.evals.federation import EvalFederationRegistry


def test_eval_federation_records_external_adapter_shape(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:browsergym:001",
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:browser-readonly",
        scores={"success": 0.8, "safety": 1.0},
        evidence_refs=["trace:browsergym-fixture"],
        held_out=True,
    )

    assert event["status"] == "recorded"
    assert event["promotion_allowed"] is True
    assert event["adapter"] == "browsergym"


def test_eval_federation_blocks_non_held_out_eval(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:swebench:001",
        adapter="swebench",
        target_surface="coding",
        candidate_ref="patch:demo",
        scores={"success": 1.0, "safety": 1.0},
        evidence_refs=["trace:swebench-fixture"],
        held_out=False,
    )

    assert event["status"] == "blocked"
    assert event["promotion_allowed"] is False
    assert "eval_event_requires_held_out_set" in event["findings"]


def test_eval_federation_returned_event_mutation_does_not_corrupt_projection(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)
    event = registry.record_event(
        event_id="eval:mutation:001",
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:mutation",
        scores={"success": 0.9, "safety": 1.0},
        evidence_refs=["trace:mutation"],
        held_out=True,
    )

    event["adapter"] = "corrupted"
    event["scores"]["safety"] = 0.0
    event["findings"].append("corrupted")

    summary = registry.summary()
    latest = summary["latest_event"]
    assert summary["adapters"] == ["browsergym"]
    assert latest["adapter"] == "browsergym"
    assert latest["scores"]["safety"] == 1.0
    assert latest["findings"] == []


def test_eval_federation_summary_sees_persisted_events_after_restart(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)
    event = registry.record_event(
        event_id="eval:persisted:001",
        adapter="swebench",
        target_surface="coding",
        candidate_ref="patch:persisted",
        scores={"success": 1.0, "safety": 0.9},
        evidence_refs=["trace:persisted"],
        held_out=True,
    )

    persisted = json.loads(Path(event["artifact_path"]).read_text(encoding="utf-8"))
    summary = EvalFederationRegistry(artifacts_dir=tmp_path).summary()

    assert persisted == event
    assert summary["event_count"] == 1
    assert summary["latest_event"]["event_id"] == "eval:persisted:001"


def test_eval_federation_skips_bad_disk_files_without_hiding_valid_events(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)
    valid = registry.record_event(
        event_id="eval:valid-disk:001",
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:valid-disk",
        scores={"success": 0.8, "safety": 0.8},
        evidence_refs=["trace:valid-disk"],
        held_out=True,
    )
    events_dir = tmp_path / "evals" / "federation"
    (events_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (events_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (events_dir / "shape-invalid.json").write_text(
        json.dumps({"event_id": "eval:missing-required"}),
        encoding="utf-8",
    )

    summary = EvalFederationRegistry(artifacts_dir=tmp_path).summary()

    assert summary["event_count"] == 1
    assert summary["latest_event"]["event_id"] == valid["event_id"]


@pytest.mark.parametrize("event_id", ["eval\\unsafe\\001", "eval/unsafe/001", "../eval/unsafe"])
def test_eval_federation_safely_persists_unsafe_event_ids_inside_root(tmp_path, event_id):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id=event_id,
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:unsafe",
        scores={"success": 0.8, "safety": 0.95},
        evidence_refs=["trace:unsafe"],
        held_out=True,
    )

    events_dir = tmp_path / "evals" / "federation"
    artifact_path = Path(event["artifact_path"]).resolve()
    assert artifact_path.parent == events_dir.resolve()
    assert artifact_path.exists()
    assert not (events_dir / ".." / "eval").exists()


def test_eval_federation_does_not_record_phantoms_after_write_failure(tmp_path, monkeypatch):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    def fail_write(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(type(tmp_path), "write_text", fail_write)

    with pytest.raises(OSError):
        registry.record_event(
            event_id="eval:write-failure:001",
            adapter="swebench",
            target_surface="coding",
            candidate_ref="patch:write-failure",
            scores={"success": 1.0, "safety": 1.0},
            evidence_refs=["trace:write-failure"],
            held_out=True,
        )

    assert registry.summary()["event_count"] == 0


def test_eval_federation_dedupes_disk_events_and_memory_wins(tmp_path):
    events_dir = tmp_path / "evals" / "federation"
    events_dir.mkdir(parents=True)
    disk_first = {
        "surface_id": "eval-federation",
        "authority": "NexusBrain",
        "event_id": "eval:duplicate:001",
        "adapter": "a-disk",
        "target_surface": "coding",
        "candidate_ref": "patch:disk-a",
        "scores": {"success": 0.7, "safety": 0.9},
        "evidence_refs": ["trace:disk-a"],
        "held_out": True,
        "status": "recorded",
        "promotion_allowed": True,
        "findings": [],
    }
    disk_second = {**disk_first, "adapter": "b-disk", "candidate_ref": "patch:disk-b"}
    (events_dir / "a.json").write_text(json.dumps(disk_first), encoding="utf-8")
    (events_dir / "b.json").write_text(json.dumps(disk_second), encoding="utf-8")

    disk_summary = EvalFederationRegistry(artifacts_dir=tmp_path).summary()
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)
    registry.record_event(
        event_id="eval:duplicate:001",
        adapter="memory",
        target_surface="coding",
        candidate_ref="patch:memory",
        scores={"success": 1.0, "safety": 1.0},
        evidence_refs=["trace:memory"],
        held_out=True,
    )

    memory_summary = registry.summary()

    assert disk_summary["event_count"] == 1
    assert disk_summary["latest_event"]["adapter"] == "b-disk"
    assert memory_summary["event_count"] == 1
    assert memory_summary["latest_event"]["adapter"] == "memory"


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_eval_federation_rejects_non_finite_scores_without_persisting(tmp_path, score):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    with pytest.raises(ValueError):
        registry.record_event(
            event_id="eval:non-finite:001",
            adapter="browsergym",
            target_surface="computer-use",
            candidate_ref="plan:non-finite",
            scores={"success": score, "safety": 1.0},
            evidence_refs=["trace:non-finite"],
            held_out=True,
        )

    assert registry.summary()["event_count"] == 0
    assert not list((tmp_path / "evals" / "federation").glob("*.json"))


@pytest.mark.parametrize("scores", ["bad-scores", None, {"success": "1.0"}, {"success": None}])
def test_eval_federation_malformed_scores_are_rejected_deterministically(tmp_path, scores):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    with pytest.raises(ValueError):
        registry.record_event(
            event_id="eval:malformed-scores:001",
            adapter="swebench",
            target_surface="coding",
            candidate_ref="patch:malformed-scores",
            scores=scores,
            evidence_refs=["trace:malformed-scores"],
            held_out=True,
        )

    assert registry.summary()["event_count"] == 0
