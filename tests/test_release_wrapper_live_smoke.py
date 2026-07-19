from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from tests.test_nexus_phase1_foundation import make_project


def test_release_wrapper_cli_boot_smoke_exercises_real_http_product_path(tmp_path: Path):
    from nexusnet.cli import wrapper

    repo_root = Path(__file__).resolve().parents[1]
    project_root = make_project(tmp_path)
    manifest_path = tmp_path / "release-wrapper-live-smoke-manifest.json"
    raw_session_id = "release-wrapper-live-smoke-raw-session"
    probe_test = project_root / "tests" / "release_wrapper_live_smoke_probe_test.py"
    probe_test.parent.mkdir(parents=True, exist_ok=True)
    probe_test.write_text(
        "def test_release_wrapper_live_smoke_probe():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    wrapper_ui = project_root / "ui" / "wrapper" / "index.html"
    wrapper_ui.parent.mkdir(parents=True, exist_ok=True)
    wrapper_ui.write_text("<html><body>NexusNet release wrapper</body></html>", encoding="utf-8")

    def real_process_factory(command: list[str], **kwargs: Any):
        env = dict(kwargs.pop("env", os.environ.copy()))
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(repo_root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
        return subprocess.Popen(command, env=env, **kwargs)

    exit_code = wrapper.main(
        [
            "boot",
            "--project-root",
            str(project_root),
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--manifest",
            str(manifest_path),
            "--session-id",
            raw_session_id,
            "--timeout-seconds",
            "90",
            "--request-timeout-seconds",
            "20",
            "--readiness-command",
            "pytest tests/release_wrapper_live_smoke_probe_test.py -q",
            "--exit-after-smoke",
        ],
        process_factory=real_process_factory,
    )

    assert exit_code == 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["surface_id"] == "release-wrapper-boot-supervisor"
    assert manifest["status"] == "boot-smoke-passed"
    assert manifest["server"]["pid"] > 0
    assert manifest["server"]["app_target"] == "nexus.api.app:app"
    assert manifest["session_ref_digest"].startswith("sha256:")
    assert manifest["raw_content_included"] is False
    checks = {check["check_id"]: check for check in manifest["checks"]}
    assert {
        "api-health",
        "wrapper-ui",
        "models",
        "wrapper-chat",
        "forward-pass-coverage",
        "federated-peer-reject",
        "federated-peer-import",
        "federated-peer-inbox",
        "readiness-runner",
        "release-readiness",
        "status-card",
        "release-product-path",
        "release-product-smoke",
    }.issubset(checks)
    assert all(check["status"] == "pass" for check in checks.values())

    evidence = manifest["evidence"]
    assert evidence["chat"]["status"] == "ok"
    assert evidence["forward_pass_coverage"]["latest_status"] == "covered"
    assert evidence["forward_pass_coverage"]["receipt_count"] >= 1
    assert evidence["forward_pass_coverage"]["raw_content_included"] is False
    assert evidence["peer_federation_reject"]["status"] == "quarantined-rejected"
    assert evidence["peer_federation_import"]["status"] == "quarantined-shadow-accepted"
    assert evidence["release_readiness_evidence_runner"]["latest_status"] == "completed"
    assert evidence["release_readiness_evidence_runner"]["active_production_mutated"] is False
    assert evidence["release_readiness"]["go_no_go"] == "go"
    assert evidence["release_product_smoke"]["latest_status"] == (
        "release-product-smoke-governed-shadow-lifecycle-completed"
    )
    assert evidence["release_product_smoke"]["runtime_state"] == "live-evidence"
    assert evidence["release_product_smoke"]["failed_count"] == 0
    assert evidence["release_product_smoke"]["raw_content_included"] is False
    assert evidence["release_product_smoke"]["active_production_mutated"] is False
    assert evidence["release_product_smoke"]["manifest_ref"] == "artifacts/release-wrapper-runtime/release-product-smoke.json"
    product_smoke_artifact = project_root / "runtime" / "artifacts" / "release-wrapper-runtime" / "release-product-smoke.json"
    assert product_smoke_artifact.exists()
    product_smoke_manifest = json.loads(product_smoke_artifact.read_text(encoding="utf-8"))
    assert product_smoke_manifest["status"] == "release-product-smoke-governed-shadow-lifecycle-completed"
    assert product_smoke_manifest["governance"]["status"] == "governed-update-completed"
    assert product_smoke_manifest["production_lifecycle"]["status"] == "approved-shadow-release-lifecycle"
    assert product_smoke_manifest["production_rollback"]["status"] == "rolled-back"
    assert product_smoke_manifest["raw_content_included"] is False
    assert product_smoke_manifest["active_production_mutated"] is False

    product_path = evidence["release_product_path"]
    assert product_path["entrypoint_runtime_state"] == "live-bound"
    assert product_path["global_growth_users"] >= 1
    assert product_path["federated_packet_count"] >= 1
    assert product_path["federated_import_accepted_count"] >= 1
    assert product_path["federated_import_rejected_count"] >= 1
    assert product_path["production_spine_packet_count"] >= 1
    assert product_path["dream_research_item_count"] >= 1
    assert product_path["autonomous_update_proposal_count"] >= 1
    assert product_path["self_repair_action_count"] >= 1
    assert product_path["admin_action_statuses"] == {
        "admin_approval": "admin-approved",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }
    assert product_path["active_production_mutation_allowed"] is False
    assert product_path["raw_content_included"] is False

    manifest_text = json.dumps(manifest, sort_keys=True)
    assert raw_session_id not in manifest_text
    assert wrapper.BOOT_SMOKE_PROMPT not in manifest_text
    assert "release-wrapper-live-smoke-admin@example.invalid" not in manifest_text
