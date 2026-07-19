from __future__ import annotations

import json
import tomllib
from pathlib import Path


def test_release_wrapper_cli_boots_product_surface_without_manual_uvicorn_target(capsys):
    from nexusnet.cli import wrapper

    calls: list[dict] = []

    def fake_uvicorn_run(app_target: str, **kwargs):
        calls.append({"app_target": app_target, **kwargs})

    exit_code = wrapper.main(
        ["--host", "0.0.0.0", "--port", "8765", "--log-level", "debug"],
        uvicorn_run=fake_uvicorn_run,
    )

    assert exit_code == 0
    assert calls == [
        {
            "app_target": "nexus.api.app:app",
            "host": "0.0.0.0",
            "port": 8765,
            "reload": False,
            "log_level": "debug",
        }
    ]
    output = capsys.readouterr().out
    assert "NexusNet release wrapper" in output
    assert "http://0.0.0.0:8765/ui/wrapper/" in output
    assert "http://0.0.0.0:8765/ops/wrapper/release-runtime" in output


def test_release_wrapper_cli_is_registered_as_console_script():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"]["nexusnet-wrapper"] == "nexusnet.cli.wrapper:main"


class _FakeResponse:
    def __init__(self, payload=None, *, status_code: int = 200, text: str = ""):
        self._payload = payload if payload is not None else {}
        self.status_code = status_code
        self.text = text or json.dumps(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeHttpClient:
    def __init__(self):
        self.calls: list[tuple[str, str, dict]] = []
        self.chat_session_id = ""
        self.import_calls = 0

    def get(self, url: str, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if url.endswith("/health"):
            return _FakeResponse({"ok": True, "status": "ok"})
        if url.endswith("/ui/wrapper/"):
            return _FakeResponse(text="<html>NexusNet release wrapper</html>")
        if url.endswith("/v1/models"):
            return _FakeResponse({"object": "list", "data": [{"id": "nexusnet-offline"}]})
        if "/ops/wrapper/release-runtime" in url:
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-runtime",
                    "entrypoint": {"runtime_state": "live-bound", "boot_target": "/ui/wrapper/"},
                    "global_growth": {"users": 1, "training_ready_nodes": ["expert.debugging"]},
                    "federated_packet_count": 1,
                    "latest_federated_packet": {
                        "packet_id": "fed::boot",
                        "raw_content_included": False,
                        "contains_personal_data": False,
                        "route_metadata": {"selected_capability_terms": ["debugging"]},
                        "learning_metadata": {"final_confidence": 0.95},
                        "security_envelope": {
                            "signed_packet": {"raw_private_data_exported": False},
                            "privacy_audit": {"raw_private_data_exported": False},
                        },
                    },
                    "federated_packet_inbox": {
                        "surface_id": "release-wrapper-federated-packet-inbox",
                        "status": "shadow-quarantine-active",
                        "import_count": 2,
                        "accepted_import_count": 1,
                        "rejected_import_count": 1,
                        "degraded_import_count": 0,
                        "latest_import": {
                            "import_id": "fed-import::boot",
                            "status": "quarantined-shadow-accepted",
                            "security_envelope_verified": True,
                            "assimilation_shadow_captured": True,
                            "global_growth_shadow_captured": True,
                            "raw_content_included": False,
                            "contains_personal_data": False,
                            "active_production_mutation_allowed": False,
                        },
                        "raw_content_included": False,
                        "contains_personal_data": False,
                        "active_production_mutation_allowed": False,
                    },
                    "production_spine": {"packet_count": 1},
                    "dream_research_queue": {
                        "item_count": 2,
                        "episode_count": 2,
                        "status": "live-bound",
                        "latest_item": {
                            "metadata": {
                                "federated_import_shadow": True,
                                "federated_packet_import_id": "fed-import::boot",
                                "raw_content_included": False,
                            }
                        },
                    },
                    "autonomous_updates": {
                        "proposal_count": 3,
                        "proposals": [
                            {
                                "update_id": "proposal::peer-shadow",
                                "status": "queued",
                                "metadata": {
                                    "safe_payload": {
                                        "peer_shadow_import": True,
                                        "raw_content_included": False,
                                    }
                                },
                            }
                        ],
                    },
                    "live_wrapper_telemetry": {
                        "failure_learning": {
                            "captured_count": 0,
                            "degraded_count": 0,
                            "latest_status": "not-run",
                        }
                    },
                    "latest_interaction": {
                        "trace_id": "trace::boot",
                        "federated_packet_id": "fed::boot",
                        "forward_pass_receipt_id": "fpr::boot",
                    },
                    "forward_pass_coverage": {
                        "surface_id": "release-wrapper-forward-pass-coverage",
                        "latest_status": "covered",
                        "receipt_count": 1,
                        "latest_receipt": {
                            "receipt_id": "fpr::boot",
                            "raw_content_included": False,
                            "active_production_mutation_allowed": False,
                        },
                    },
                }
            )
        if "/ops/wrapper/federated-packets/imports" in url:
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-federated-packet-inbox",
                    "status": "shadow-quarantine-active",
                    "import_count": 2,
                    "accepted_import_count": 1,
                    "rejected_import_count": 1,
                    "degraded_import_count": 0,
                    "latest_import": {
                        "import_id": "fed-import::boot",
                        "status": "quarantined-shadow-accepted",
                        "security_envelope_verified": True,
                        "assimilation_shadow_captured": True,
                        "global_growth_shadow_captured": True,
                        "raw_content_included": False,
                        "contains_personal_data": False,
                        "active_production_mutation_allowed": False,
                    },
                    "raw_content_included": False,
                    "contains_personal_data": False,
                    "active_production_mutation_allowed": False,
                }
            )
        if "/ops/wrapper/release-readiness?" in url:
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-readiness",
                    "go_no_go": "go",
                    "blockers": [],
                    "evidence": {
                        "release_readiness_evidence_runner": {
                            "latest_status": "completed",
                            "latest_run": {"run_id": "run::boot"},
                        }
                    },
                }
            )
        if "/ops/wrapper/status-card" in url:
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-status-card",
                    "honest_status_label": "go",
                    "operator_action_lane": {
                        "proposal_update_id": "update::release-wrapper-boot",
                        "latest_action_statuses": {
                            "admin_approval": "pending-admin-approval",
                            "sandbox_tests": "not-run",
                            "apply": "not-applied",
                            "rollback": "not-rolled-back",
                        }
                    },
                    "self_repair_ledger": {
                        "repair_count": 4,
                        "latest_action": "rollback",
                        "mutation_boundary": "admin-approved-shadow-safe-file-only-no-active-production-mutation",
                    },
                    "release_readiness_evidence_runner": {
                        "latest_status": "completed",
                        "latest_run": {"run_id": "run::boot"},
                    },
                }
            )
        raise AssertionError(f"unexpected GET {url}")

    def post(self, url: str, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if url.endswith("/ops/approvals"):
            payload = kwargs["json"]
            assert payload["decision"] == "approved"
            if payload["subject"] == "release-wrapper-autonomous-update":
                assert payload["metadata"]["update_id"] == "update::release-wrapper-boot"
                return _FakeResponse({"decision_id": "approval::release-wrapper-boot"})
            if payload["subject"] == "release-wrapper-production-spine-release-lifecycle":
                assert payload["metadata"]["session_id"] == "release-wrapper-boot-raw-session"
                return _FakeResponse({"decision_id": "approval::release-wrapper-production-boot"})
            raise AssertionError(f"unexpected approval subject {payload['subject']}")
        if url.endswith("/v1/chat/completions"):
            payload = kwargs["json"]
            self.chat_session_id = payload["session_id"]
            return _FakeResponse(
                {
                    "object": "chat.completion",
                    "nexusnet": {
                        "status": "ok",
                        "session_id": payload["session_id"],
                        "release_runtime_ref": "/ops/wrapper/release-runtime",
                    },
                }
            )
        if url.endswith("/ops/wrapper/release-readiness/run"):
            payload = kwargs["json"]
            assert payload["update_id"] == "update::release-wrapper-boot"
            assert payload["approval_decision_id"] == "approval::release-wrapper-boot"
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-readiness-evidence-run",
                    "status": "completed",
                    "run_id": "run::boot",
                    "active_production_mutated": False,
                    "artifact_path": "artifacts/release-wrapper-runtime/release-readiness-run.json",
                    "actions": {
                        "admin_approval": {"status": "admin-approved"},
                        "sandbox_tests": {"status": "passed", "evidence_ref": "sandbox::boot"},
                        "apply": {"status": "applied-shadow-safe-file"},
                        "rollback": {"status": "rolled-back"},
                    },
                }
            )
        if url.endswith("/ops/wrapper/release-product-smoke/run"):
            payload = kwargs["json"]
            assert kwargs["timeout"] == 270
            assert payload["update_id"] == "update::release-wrapper-boot"
            assert payload["approval_decision_id"] == "approval::release-wrapper-boot"
            assert payload["production_approval_decision_id"] == "approval::release-wrapper-production-boot"
            return _FakeResponse(
                {
                    "schema_version": "nexusnet-release-wrapper-product-smoke-v1",
                    "surface_id": "release-wrapper-product-smoke",
                    "manifest_id": "release-product-smoke::boot",
                    "status": "release-product-smoke-governed-shadow-lifecycle-completed",
                    "governed_update_lifecycle": {
                        "status": "completed",
                        "actions": {
                            "admin_approval": {"status": "admin-approved"},
                            "sandbox_tests": {"status": "passed"},
                            "apply": {"status": "applied-shadow-safe-file"},
                            "rollback": {"status": "rolled-back"},
                        },
                    },
                    "product_surface": "wrapper",
                    "product_scope": "whole-system",
                    "artifact_ref": "artifacts/release-wrapper-runtime/release-product-smoke.json",
                    "check_count": 9,
                    "pass_count": 9,
                    "failed_count": 0,
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                    "active_production_mutated": False,
                }
            )
        if url.endswith("/ops/wrapper/federated-packets/import"):
            self.import_calls += 1
            if self.import_calls == 1:
                return _FakeResponse(
                    {
                        "surface_id": "release-wrapper-federated-packet-import",
                        "import_id": "fed-import::rejected-boot",
                        "status": "quarantined-rejected",
                        "security_envelope_verified": False,
                        "assimilation_shadow_captured": False,
                        "global_growth_shadow_captured": False,
                        "quarantine_state": "blocked",
                        "raw_content_included": False,
                        "contains_personal_data": False,
                        "active_production_mutation_allowed": False,
                    }
                )
            return _FakeResponse(
                {
                    "surface_id": "release-wrapper-federated-packet-import",
                    "import_id": "fed-import::boot",
                    "status": "quarantined-shadow-accepted",
                    "security_envelope_verified": True,
                    "assimilation_shadow_captured": True,
                    "global_growth_shadow_captured": True,
                    "quarantine_state": "shadow-only",
                    "raw_content_included": False,
                    "contains_personal_data": False,
                    "active_production_mutation_allowed": False,
                }
            )
        raise AssertionError(f"unexpected POST {url}")


class _FakeProcess:
    pid = 4242

    def __init__(self):
        self.terminated = False
        self.waited = False

    def poll(self):
        return None

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        self.waited = True
        return 0


def test_release_wrapper_cli_boot_supervisor_starts_api_smokes_runtime_and_writes_sanitized_manifest(tmp_path: Path):
    from nexusnet.cli import wrapper

    manifest_path = tmp_path / "boot-manifest.json"
    started: list[dict] = []
    fake_process = _FakeProcess()
    fake_http = _FakeHttpClient()

    def fake_process_factory(command, **kwargs):
        started.append({"command": command, **kwargs})
        return fake_process

    exit_code = wrapper.main(
        [
            "boot",
            "--host",
            "127.0.0.1",
            "--port",
            "8771",
            "--manifest",
            str(manifest_path),
            "--session-id",
            "release-wrapper-boot-raw-session",
            "--exit-after-smoke",
            "--readiness-command",
            "pytest tests/test_release_wrapper_cli.py::test_release_wrapper_cli_is_registered_as_console_script -q",
        ],
        process_factory=fake_process_factory,
        http_client=fake_http,
        sleep=lambda _seconds: None,
    )

    assert exit_code == 0
    assert started
    assert started[0]["command"][:4] == [
        wrapper._python_executable(),
        "-m",
        "uvicorn",
        "nexus.api.app:app",
    ]
    assert "--port" in started[0]["command"]
    assert "8771" in started[0]["command"]
    assert fake_process.terminated is True
    assert fake_process.waited is True

    methods_and_urls = [(method, url) for method, url, _kwargs in fake_http.calls]
    assert ("GET", "http://127.0.0.1:8771/ui/wrapper/") in methods_and_urls
    assert ("GET", "http://127.0.0.1:8771/v1/models") in methods_and_urls
    assert ("POST", "http://127.0.0.1:8771/v1/chat/completions") in methods_and_urls
    assert methods_and_urls.count(("POST", "http://127.0.0.1:8771/ops/wrapper/federated-packets/import")) == 2
    assert ("GET", "http://127.0.0.1:8771/ops/wrapper/federated-packets/imports?session_id=release-wrapper-boot-raw-session") in methods_and_urls
    assert ("POST", "http://127.0.0.1:8771/ops/wrapper/release-readiness/run") in methods_and_urls
    assert ("POST", "http://127.0.0.1:8771/ops/wrapper/release-product-smoke/run") in methods_and_urls

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["surface_id"] == "release-wrapper-boot-supervisor"
    assert manifest["status"] == "boot-smoke-passed"
    assert manifest["base_url"] == "http://127.0.0.1:8771"
    assert manifest["server"]["pid"] == 4242
    assert manifest["evidence"]["forward_pass_coverage"]["latest_status"] == "covered"
    assert manifest["evidence"]["peer_federation_reject"] == {
        "status": "quarantined-rejected",
        "import_id": "fed-import::rejected-boot",
        "security_envelope_verified": False,
        "assimilation_shadow_captured": False,
        "global_growth_shadow_captured": False,
        "active_production_mutation_allowed": False,
        "raw_content_included": False,
        "contains_personal_data": False,
    }
    assert manifest["evidence"]["peer_federation_import"] == {
        "status": "quarantined-shadow-accepted",
        "import_id": "fed-import::boot",
        "security_envelope_verified": True,
        "assimilation_shadow_captured": True,
        "global_growth_shadow_captured": True,
        "active_production_mutation_allowed": False,
        "raw_content_included": False,
        "contains_personal_data": False,
    }
    assert manifest["evidence"]["release_readiness_evidence_runner"]["latest_status"] == "completed"
    assert manifest["evidence"]["release_readiness"]["go_no_go"] == "go"
    assert manifest["evidence"]["release_product_smoke"]["latest_status"] == (
        "release-product-smoke-governed-shadow-lifecycle-completed"
    )
    assert manifest["evidence"]["release_product_smoke"]["failed_count"] == 0
    assert manifest["evidence"]["release_product_smoke"]["raw_content_included"] is False
    assert manifest["evidence"]["release_product_path"] == {
        "entrypoint_runtime_state": "live-bound",
        "global_growth_users": 1,
        "training_ready_node_count": 1,
        "federated_packet_count": 1,
        "federated_import_count": 2,
        "federated_import_accepted_count": 1,
        "federated_import_rejected_count": 1,
        "federated_import_degraded_count": 0,
        "peer_shadow_proposal_count": 1,
        "production_spine_packet_count": 1,
        "dream_research_item_count": 2,
        "dream_research_episode_count": 2,
        "autonomous_update_proposal_count": 3,
        "self_repair_action_count": 4,
        "latest_self_repair_action": "rollback",
        "admin_action_statuses": {
            "admin_approval": "admin-approved",
            "sandbox_tests": "passed",
            "apply": "applied-shadow-safe-file",
            "rollback": "rolled-back",
        },
        "failure_learning": {
            "captured_count": 0,
            "degraded_count": 0,
            "latest_status": "not-run",
        },
        "active_production_mutation_allowed": False,
        "raw_content_included": False,
    }
    assert manifest["raw_content_included"] is False
    serialized = json.dumps(manifest)
    assert "release-wrapper-boot-raw-session" not in serialized
    assert "Release wrapper boot smoke" not in serialized
