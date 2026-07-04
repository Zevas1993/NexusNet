from __future__ import annotations

import importlib
import importlib.util


def _project_heartbeat_module():
    spec = importlib.util.find_spec("nexusnet.release_wrapper_project_heartbeat")
    assert spec is not None
    return importlib.import_module("nexusnet.release_wrapper_project_heartbeat")


def test_empty_project_heartbeat_is_sanitized_not_run_receipt():
    module = _project_heartbeat_module()

    heartbeat = module.empty_release_project_heartbeat(
        session_ref_digest="session-digest",
    )

    assert heartbeat["schema_version"] == "nexusnet-project-heartbeat-v1"
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["status"] == "not-run"
    assert heartbeat["runtime_state"] == "not-run"
    assert heartbeat["session_ref_digest"] == "session-digest"
    assert heartbeat["heartbeat_id"] is None
    assert heartbeat["lane_count"] == 0
    assert heartbeat["alive_lane_count"] == 0
    assert heartbeat["degraded_lane_count"] == 0
    assert heartbeat["lanes"] == []
    assert heartbeat["blockers"] == ["project_heartbeat_not_observed"]
    assert heartbeat["evidence_refs"] == []
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False


def test_project_heartbeat_from_substrate_compacts_alive_heartbeat_without_session_id():
    module = _project_heartbeat_module()

    class Substrate:
        def summary(self, *, session_id: str | None = None):
            return {
                "project_heartbeat": {
                    "schema_version": "nexusnet-project-heartbeat-v1",
                    "surface_id": "nexusnet-project-heartbeat",
                    "status": "alive",
                    "heartbeat_id": "heartbeat::1",
                    "source_run_id": "run::1",
                    "source_trace_ref": "trace::1",
                    "session_id": session_id,
                    "session_ref_digest": "old-digest",
                    "lane_count": 1,
                    "alive_lane_count": 1,
                    "degraded_lane_count": 0,
                    "lanes": [
                        {
                            "lane_id": "brain",
                            "status": "alive",
                            "evidence_refs": ["run::1"],
                        }
                    ],
                    "evidence_refs": ["heartbeat::1", "run::1"],
                    "blockers": [],
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                    "active_production_mutated": False,
                }
            }

    heartbeat = module.release_project_heartbeat_from_substrate(
        Substrate(),
        session_id="secret-session-id",
        session_ref_digest="new-digest",
    )

    assert heartbeat["status"] == "alive"
    assert heartbeat["runtime_state"] == "live-bound"
    assert heartbeat["heartbeat_id"] == "heartbeat::1"
    assert heartbeat["session_ref_digest"] == "new-digest"
    assert "session_id" not in heartbeat
    assert heartbeat["lanes"][0]["lane_id"] == "brain"
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False


def test_project_heartbeat_from_substrate_degrades_on_contract_or_summary_failure():
    module = _project_heartbeat_module()

    class LeakySubstrate:
        def summary(self, *, session_id: str | None = None):
            return {
                "project_heartbeat": {
                    "schema_version": "nexusnet-project-heartbeat-v1",
                    "surface_id": "nexusnet-project-heartbeat",
                    "status": "alive",
                    "raw_content_included": True,
                    "active_production_mutation_allowed": False,
                    "active_production_mutated": False,
                }
            }

    class BrokenSubstrate:
        def summary(self, *, session_id: str | None = None):
            raise RuntimeError("secret failure detail")

    leaky = module.release_project_heartbeat_from_substrate(
        LeakySubstrate(),
        session_id="secret-session-id",
        session_ref_digest="digest",
    )
    broken = module.release_project_heartbeat_from_substrate(
        BrokenSubstrate(),
        session_id="secret-session-id",
        session_ref_digest="digest",
    )

    assert leaky["status"] == "degraded"
    assert leaky["blockers"] == ["project_heartbeat_sanitization_or_contract_failed"]
    assert leaky["raw_content_included"] is False
    assert broken["status"] == "degraded"
    assert broken["blockers"] == ["hive_substrate_summary_unavailable::RuntimeError"]
    assert "secret failure detail" not in str(broken)
    assert "secret-session-id" not in str(broken)
