from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class EvalSuiteService:
    SUITES = [
        ("rag_quality", "Retrieval answer quality, grounding, claim support, and source usefulness."),
        ("tool_call_accuracy", "Tool selection, argument validity, denied-tool visibility, and execution policy fit."),
        ("workflow_completion", "Workflow DAG completion, validation gates, artifact capture, and approval routing."),
        ("code_agent_issue_to_patch", "Issue-as-spec implementation trace, diff review, validation, and PR readiness."),
        ("prompt_security_red_team", "Prompt injection, data exfiltration, unsafe autonomy, and guardrail bypass attempts."),
        ("runtime_quality", "Backend capability, latency, throughput, structured output, and tool-call posture."),
        ("regression_behavior", "Previously fixed behavior, product-sweep gates, and release-blocking regressions."),
    ]

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "eval-suites"
        self.events = events

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "suite_count": len(self.SUITES),
            "promotion_requires_eval_pass": True,
            "manual_approval_is_not_sufficient": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "suites": [self._suite(suite_type, description) for suite_type, description in self.SUITES],
            "latest_results": self._results(limit=20),
        }

    def compact_summary(self) -> dict[str, Any]:
        payload = self.summary()
        return {
            "status_label": payload["status_label"],
            "suite_count": payload["suite_count"],
            "promotion_requires_eval_pass": payload["promotion_requires_eval_pass"],
            "latest_result": payload["latest_results"][0] if payload["latest_results"] else None,
            "suite_types": [item["suite_type"] for item in payload["suites"]],
        }

    def run(self, *, suite_type: str, subject: str, linked_trace_ids: list[str] | None = None) -> dict[str, Any]:
        suite = next((item for item in self.summary()["suites"] if item["suite_type"] == suite_type), None)
        if suite is None:
            raise ValueError(f"unsupported eval suite type: {suite_type}")
        status = "blocked" if suite_type == "prompt_security_red_team" else "recorded"
        result = {
            "result_id": new_id("evalsuite"),
            "suite_type": suite_type,
            "subject": subject,
            "created_at": utcnow().isoformat(),
            "status": status,
            "pass": status == "passed",
            "blocked_reason": "metadata-only-red-team-requires-policy-grant" if status == "blocked" else None,
            "product_sweep_gate_ids": suite["product_sweep_gate_ids"],
            "promotion_decision": "not_promotable_without_passed_eval",
            "execution_allowed": False,
            "mutation_allowed": False,
            "linked_trace_ids": list(linked_trace_ids or []),
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result['result_id']}.json"
        result["artifact_path"] = str(path)
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        if self.events:
            self.events.record(
                event_type="eval_suite.run_recorded",
                subject=f"eval-suite:{suite_type}:{subject}",
                trace_ids=result["linked_trace_ids"],
                payload={
                    "result_id": result["result_id"],
                    "status": status,
                    "execution_allowed": False,
                    "mutation_allowed": False,
                },
            )
        return {"status_label": "STRONG ACCEPTED DIRECTION", "suite": suite, "result": result}

    def _suite(self, suite_type: str, description: str) -> dict[str, Any]:
        return {
            "suite_type": suite_type,
            "description": description,
            "status": "available_metadata_only",
            "product_sweep_gate_ids": self._gate_ids(suite_type),
            "policy_path": [{"stage": "eval-suite", "decision": "hold", "reason": "execution-gated"}],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def _gate_ids(self, suite_type: str) -> list[str]:
        if suite_type == "prompt_security_red_team":
            return ["phase-4-security", "product-sweep-security", "prompt-injection-gate"]
        if suite_type == "runtime_quality":
            return ["phase-7-runtime", "runtime-certification"]
        if suite_type == "rag_quality":
            return ["phase-6-context-assembly", "retrieval-grounding-gate"]
        if suite_type == "code_agent_issue_to_patch":
            return ["phase-9-product-ops", "parallel-run-gate"]
        return ["phase-2-trace-evals", "promotion-provenance-gate"]

    def _results(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items
