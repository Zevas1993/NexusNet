from __future__ import annotations

import importlib
import importlib.util


def test_federated_import_governance_helper_builds_manual_receipt_without_raw_content():
    spec = importlib.util.find_spec("nexusnet.release_wrapper_governance")
    assert spec is not None
    apply_federated_import_governed_update_path = importlib.import_module(
        "nexusnet.release_wrapper_governance"
    ).apply_federated_import_governed_update_path

    record = {
        "import_id": "import-1",
        "source_packet_ref": "federated-packet::packet-1",
    }
    receipt = {
        "receipt_id": "receipt-1",
        "governed_update_path": {"status": "proposal-queued-admin-approval-pending"},
        "replay": {},
        "evidence_refs": ["federated-import::import-1"],
        "raw_content_included": False,
    }
    action_records = [
        {
            "action": "admin_approval",
            "status": "admin-approved",
            "operation_receipt": {"receipt_id": "op-admin"},
            "evidence_refs": ["approval_ref::operator-review"],
            "active_production_mutated": False,
        },
        {
            "action": "sandbox_tests",
            "status": "passed",
            "operation_receipt": {"receipt_id": "op-sandbox"},
            "evidence_refs": ["sandbox::pytest"],
            "active_production_mutated": False,
        },
        {
            "action": "apply",
            "status": "applied-shadow-safe-file",
            "operation_receipt": {"receipt_id": "op-apply"},
            "evidence_refs": ["safe_file_path_digest::sha256:abc"],
            "active_production_mutated": False,
        },
        {
            "action": "rollback",
            "status": "rolled-back",
            "operation_receipt": {"receipt_id": "op-rollback"},
            "evidence_refs": ["rollback_plan_digest::sha256:def"],
            "active_production_mutated": False,
        },
    ]

    backfill = apply_federated_import_governed_update_path(
        update_id="update::federated-import::manual",
        import_id="import-1",
        source_packet_ref="federated-packet::packet-1",
        record=record,
        receipt=receipt,
        action_records=action_records,
    )

    governed_path = record["whole_system_enforcement_receipt"]["governed_update_path"]
    assert backfill["status"] == "completed-admin-approved-sandbox-applied-rolled-back"
    assert backfill["manual_governance_recorded"] is True
    assert governed_path["manual_governance_recorded"] is True
    assert governed_path["readiness_run_id"] is None
    assert governed_path["action_statuses"] == {
        "admin_approval": "admin-approved",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }
    assert governed_path["action_operation_receipt_ids"] == {
        "admin_approval": "op-admin",
        "sandbox_tests": "op-sandbox",
        "apply": "op-apply",
        "rollback": "op-rollback",
    }
    assert governed_path["raw_content_included"] is False
    assert governed_path["active_production_mutation_allowed"] is False
    assert governed_path["active_production_mutated"] is False
    assert record["governed_update_path_status"] == "completed-admin-approved-sandbox-applied-rolled-back"
