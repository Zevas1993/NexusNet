from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.checkpoint_rewind import CheckpointRewindLedger
from tests.test_nexus_phase1_foundation import make_project


def test_checkpoint_rewind_restores_the_exact_prewrite_snapshot():
    ledger = CheckpointRewindLedger()
    state = {"route": "local", "settings": {"temperature": 0.2}}

    checkpoint = ledger.capture(subject_ref="inference:session-1", state=state)
    state["route"] = "cloud"
    state["settings"]["temperature"] = 0.9
    restored = ledger.rewind(checkpoint["checkpoint_id"], subject_ref="inference:session-1")

    assert restored["state"] == {"route": "local", "settings": {"temperature": 0.2}}
    assert restored["restore_policy"] == "exact-snapshot"
    assert restored["snapshot_sha256"] == checkpoint["snapshot_sha256"]


def test_checkpoint_rewind_rejects_a_different_subject():
    ledger = CheckpointRewindLedger()
    checkpoint = ledger.capture(subject_ref="inference:session-1", state={"route": "local"})

    try:
        ledger.rewind(checkpoint["checkpoint_id"], subject_ref="inference:session-2")
    except PermissionError as error:
        assert "subject mismatch" in str(error)
    else:
        raise AssertionError("rewind must reject a different subject")


def test_checkpoint_rewind_survives_a_ledger_restart(tmp_path):
    ledger = CheckpointRewindLedger(artifacts_dir=tmp_path)
    checkpoint = ledger.capture(subject_ref="inference:durable", state={"route": "local"})

    restarted = CheckpointRewindLedger(artifacts_dir=tmp_path)
    restored = restarted.rewind(checkpoint["checkpoint_id"], subject_ref="inference:durable")

    assert restored["state"] == {"route": "local"}


def test_checkpoint_rewind_is_available_through_the_nexusnet_operations_api(tmp_path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    captured = client.post(
        "/ops/brain/checkpoints",
        json={"subject_ref": "inference:session-api", "state": {"route": "local", "step": 1}},
    )

    assert captured.status_code == 200
    checkpoint = captured.json()["checkpoint"]
    rewound = client.post(
        f"/ops/brain/checkpoints/{checkpoint['checkpoint_id']}/rewind",
        json={"subject_ref": "inference:session-api"},
    )

    assert rewound.status_code == 200
    assert rewound.json()["checkpoint"]["state"] == {"route": "local", "step": 1}

    summary = client.get("/ops/brain/checkpoints")
    assert summary.status_code == 200
    assert summary.json()["checkpoint_count"] == 1
    assert summary.json()["raw_state_exposed"] is False
    assert "state" not in summary.json()["recent_checkpoints"][0]
    assert summary.json()["recent_checkpoints"][0]["subject_ref_digest"].startswith("sha256:")
