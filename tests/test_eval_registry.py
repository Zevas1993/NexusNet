from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.evals.registry import EvalRegistry, EvalSuiteRequest, ShadowEvalRunRequest
from tests.test_nexus_phase1_foundation import make_project


def test_eval_registry_registers_held_out_agent_eval_suite_with_policy_gate():
    registry = EvalRegistry.default()

    suite = registry.register(
        EvalSuiteRequest(
            suite_id="eval::agent-autonomy",
            suite_type="agentic",
            target_surfaces=["agentic-pipelines", "self-improvement", "browser-context"],
            benchmark_refs=["GAIA", "tau-bench", "OSWorld", "SWE-bench"],
            held_out=True,
            metrics={"pass_rate": 0.82, "regression_count": 0},
            promotion_target="autonomous_update",
            evidence_refs=["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
        )
    )

    assert suite["status_label"] == "LOCKED CANON"
    assert suite["authority"] == "NexusBrain"
    assert suite["status"] == "active"
    assert suite["promotion_gate"] == "passed"
    assert "external_not_self_grading" in suite["required_controls"]
    assert suite["policy_scan"]["summary"]["allow_merge"] is True


def test_eval_registry_blocks_non_held_out_or_unprovenanced_eval_suites():
    registry = EvalRegistry.default()

    suite = registry.register(
        {
            "suite_id": "eval::self-graded",
            "suite_type": "agentic",
            "target_surfaces": ["autonomous-updates"],
            "benchmark_refs": [],
            "held_out": False,
            "metrics": {"pass_rate": 0.95, "regression_count": 2},
            "promotion_target": "autonomous_update",
            "evidence_refs": [],
        }
    )

    assert suite["status"] == "blocked"
    assert suite["promotion_gate"] == "blocked"
    assert {
        "eval_suite_requires_held_out_cases",
        "eval_suite_requires_external_or_tool_verifier",
        "eval_suite_requires_regression_free_result",
    }.issubset({finding["rule_id"] for finding in suite["eval_findings"]})
    assert suite["policy_scan"]["summary"]["allow_merge"] is False


def test_eval_registry_runs_shadow_eval_with_heldout_and_trace_gates():
    registry = EvalRegistry.default()
    registry.register(
        EvalSuiteRequest(
            suite_id="eval::harness-shadow",
            suite_type="agentic",
            target_surfaces=["harness-ledger", "agentic-pipelines"],
            benchmark_refs=["nexus-held-out"],
            held_out=True,
            metrics={"pass_rate": 0.8, "regression_count": 0},
            promotion_target="autonomous_update",
            evidence_refs=["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
        )
    )

    run = registry.run_shadow(
        "eval::harness-shadow",
        ShadowEvalRunRequest(
            run_id="shadow-run::harness-v2",
            candidate_ref="harness-ledger::context-router-v2",
            baseline_ref="harness-ledger::context-router-v1",
            metrics={"pass_rate": 0.86, "regression_count": 0, "cost_delta": -0.08},
            trace_refs=["trace::shadow-harness-v2"],
            evaluator_refs=["tool::pytest", "eval::nexus-held-out"],
            evidence_refs=["shadow::context-router-v2"],
            operator_approved=True,
        ),
    )

    assert run["status_label"] == "LOCKED CANON"
    assert run["authority"] == "NexusBrain"
    assert run["surface_id"] == "eval-shadow-run"
    assert run["suite_id"] == "eval::harness-shadow"
    assert run["status"] == "passed-shadow"
    assert run["promotion_allowed"] is True
    assert run["policy_scan"]["summary"]["allow_merge"] is True


def test_eval_registry_blocks_shadow_eval_from_blocked_production_lifecycle():
    registry = EvalRegistry.default()
    registry.register(
        EvalSuiteRequest(
            suite_id="eval::growth-lifecycle-shadow",
            suite_type="coding",
            target_surfaces=["production-spine", "growth-engine"],
            benchmark_refs=["nexus-held-out"],
            held_out=True,
            metrics={"pass_rate": 0.84, "regression_count": 0},
            promotion_target="adapter",
            evidence_refs=["artifact-trust::blocked-growth-replay"],
        )
    )

    run = registry.run_shadow(
        "eval::growth-lifecycle-shadow",
        {
            "run_id": "shadow-run::blocked-growth-lifecycle",
            "candidate_ref": "student:blocked_growth_candidate",
            "baseline_ref": "node:expert_coder",
            "metrics": {"pass_rate": 0.91, "regression_count": 0},
            "trace_refs": ["trace::blocked-growth-lifecycle"],
            "evaluator_refs": ["eval::nexus-held-out"],
            "evidence_refs": ["artifact-trust::blocked-growth-replay"],
            "operator_approved": True,
            "lifecycle_ref": "lifecycle:growth_gate_blocked",
            "lifecycle_status": "closed_loop_blocked",
            "growth_engine_gate": {
                "allowed": False,
                "blockers": ["growth_engine_adapter_training_gate_blocked"],
            },
            "artifact_trust_promotion": {
                "promotion_allowed": False,
                "promotion_blockers": ["growth_engine_adapter_training_gate_blocked"],
            },
        },
    )

    assert run["status"] == "blocked"
    assert run["promotion_allowed"] is False
    assert run["upstream_lifecycle_gate"]["lifecycle_status"] == "closed_loop_blocked"
    assert run["upstream_lifecycle_gate"]["growth_engine_gate_allowed"] is False
    assert run["upstream_lifecycle_gate"]["artifact_trust_promotion_allowed"] is False
    assert "growth_engine_adapter_training_gate_blocked" in run["upstream_lifecycle_gate"]["blockers"]
    assert {
        "shadow_eval_blocks_blocked_lifecycle",
        "shadow_eval_blocks_growth_engine_gate",
        "shadow_eval_blocks_artifact_trust_promotion",
    }.issubset({finding["rule_id"] for finding in run["shadow_findings"]})

    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_shadow_count"] == 1
    assert scorecard["latest_shadow_run"]["status"] == "blocked"


def test_eval_registry_blocks_shadow_run_without_trace_or_external_evaluator():
    registry = EvalRegistry.default()
    registry.register(
        {
            "suite_id": "eval::unsafe-shadow",
            "suite_type": "agentic",
            "target_surfaces": ["autonomous-updates"],
            "benchmark_refs": ["nexus-held-out"],
            "held_out": True,
            "metrics": {"pass_rate": 0.8, "regression_count": 0},
            "promotion_target": "autonomous_update",
            "evidence_refs": ["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
        }
    )

    run = registry.run_shadow(
        "eval::unsafe-shadow",
        {
            "run_id": "shadow-run::unsafe",
            "candidate_ref": "autonomous-update::unsafe",
            "baseline_ref": "",
            "metrics": {"pass_rate": 0.91, "regression_count": 1},
            "trace_refs": [],
            "evaluator_refs": [],
            "evidence_refs": [],
            "operator_approved": False,
        },
    )

    assert run["status"] == "blocked"
    assert run["promotion_allowed"] is False
    assert {
        "shadow_eval_requires_baseline_ref",
        "shadow_eval_requires_trace_refs",
        "shadow_eval_requires_external_evaluator_refs",
        "shadow_eval_requires_evidence_refs",
        "shadow_eval_blocks_regressions",
        "shadow_eval_requires_operator_approval",
    }.issubset({finding["rule_id"] for finding in run["shadow_findings"]})


def test_eval_registry_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/eval-registry/suites",
        json={
            "suite_id": "eval::api-quantization",
            "suite_type": "runtime",
            "target_surfaces": ["quantization-catalog", "edge-workload-router"],
            "benchmark_refs": ["needle-recall", "latency-delta", "capability-retention"],
            "held_out": True,
            "metrics": {"pass_rate": 0.9, "regression_count": 0},
            "promotion_target": "quantization",
            "evidence_refs": ["docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    shadow = client.post(
        "/ops/brain/eval-suites/eval::api-quantization/run-shadow",
        json={
            "run_id": "shadow-run::api-quantization",
            "candidate_ref": "quantization::api-candidate",
            "baseline_ref": "quantization::baseline",
            "metrics": {"pass_rate": 0.91, "regression_count": 0, "latency_delta": -0.12},
            "trace_refs": ["trace::api-quantization-shadow"],
            "evaluator_refs": ["eval::needle-recall"],
            "evidence_refs": ["cache::api-vllm-prefix"],
            "operator_approved": True,
        },
    )
    assert shadow.status_code == 200
    assert shadow.json()["status"] == "passed-shadow"

    summary = client.get("/ops/brain/eval-registry")
    assert summary.status_code == 200
    assert summary.json()["suite_count"] == 1
    assert summary.json()["shadow_run_count"] == 1

    eval_suites = client.get("/ops/brain/eval-suites")
    assert eval_suites.status_code == 200
    assert eval_suites.json()["shadow_run_count"] == 1

    scorecard = client.get("/ops/brain/canon/eval-registry")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["run_shadow"]["endpoint"] == "/ops/brain/eval-suites/{suite_id}/run-shadow"
    assert "gaia_tau_osworld_swebench_lanes" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "eval-registry-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["eval_registry_scorecard"]["suite_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "eval-registry-cockpit"}).json()
    assert blackbox["scorecard_refs"]["eval_registry"] == "/ops/brain/canon/eval-registry"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Eval Registry" in ui.text
    assert "evalRegistryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderEvalRegistryScorecard" in app_js
    assert "/ops/brain/canon/eval-registry" in app_js
    assert "upstream lifecycle gate" in app_js
    assert "upstream_lifecycle_gate" in app_js
