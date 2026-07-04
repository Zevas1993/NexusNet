from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.codegraph_gate import CodegraphGate, CodegraphRunManifestRequest
from nexusnet.policy import PolicyKernel
from tests.test_nexus_phase1_foundation import make_project


def test_codegraph_gate_blocks_code_edit_without_impact_evidence():
    gate = CodegraphGate()

    report = gate.evaluate(
        CodegraphRunManifestRequest(
            manifest_id="codegraph::missing-impact",
            run_kind="code_edit",
            indexed_repo="NexusNet",
            indexed_commit="abc",
            worktree_commit="def",
            graph_query_ref="gitnexus::query::policy",
            impact_target="PolicyKernel",
            impact_risk="missing",
            affected_processes=[],
            detect_changes_ref="",
        )
    )

    assert report["status"] == "blocked"
    assert "codegraph_gate_requires_impact_evidence" in {finding["rule_id"] for finding in report["findings"]}
    assert "codegraph_gate_blocks_stale_index" in {finding["rule_id"] for finding in report["findings"]}


def test_codegraph_gate_allows_docs_only_without_impact_target():
    gate = CodegraphGate()

    report = gate.evaluate(
        {
            "manifest_id": "codegraph::docs",
            "run_kind": "docs_only",
            "indexed_repo": "NexusNet",
            "indexed_commit": "abc",
            "worktree_commit": "abc",
            "graph_query_ref": "",
            "impact_target": "",
            "impact_risk": "not_required",
            "affected_processes": [],
            "detect_changes_ref": "gitnexus::detect::docs",
        }
    )

    assert report["status"] == "allowed"
    assert report["policy_boundary"] == "code-affecting-runs-require-current-graph-impact-and-detect-changes"


def test_policy_kernel_blocks_code_change_missing_codegraph_manifest():
    report = PolicyKernel.default().scan(
        [
            {
                "target_id": "code::planner",
                "target_type": "code_change",
                "metadata": {"tests_provided": True, "codegraph_manifest_ref": ""},
            }
        ]
    )

    assert report.summary.allow_merge is False
    assert "code_change_requires_codegraph_manifest" in {finding.rule_id for finding in report.findings}


def test_codegraph_gate_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/codegraph-gate/manifests",
        json={
            "manifest_id": "codegraph::api",
            "run_kind": "code_edit",
            "indexed_repo": "NexusNet",
            "indexed_commit": "abc",
            "worktree_commit": "abc",
            "graph_query_ref": "gitnexus::query::api",
            "impact_target": "RetrievalPlanner",
            "impact_risk": "LOW",
            "affected_processes": ["retrieval planning"],
            "detect_changes_ref": "gitnexus::detect::api",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "allowed"
