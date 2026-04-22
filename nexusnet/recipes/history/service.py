from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..execution_store import RecipeExecutionStore
from ..reports import build_recipe_execution_report


class RecipeHistoryService:
    def __init__(self, *, execution_store: RecipeExecutionStore, recipe_catalog: Any, artifacts_dir: Path):
        self.execution_store = execution_store
        self.recipe_catalog = recipe_catalog
        self.artifacts_dir = Path(artifacts_dir)

    def execute(
        self,
        *,
        recipe_id: str,
        trigger_source: str,
        parameter_set: dict[str, Any],
        linked_trace_ids: list[str],
        linked_subagent_ids: list[str],
        policy_path: list[dict[str, Any]],
        approval_path: dict[str, Any],
        gateway_decision_path: list[dict[str, Any]] | None = None,
        gateway_execution_id: str | None = None,
        gateway_report_id: str | None = None,
        execution_path: list[dict[str, Any]] | None = None,
        approval_fallback_chain: list[dict[str, Any]] | None = None,
        adversary_review_report_ids: list[str] | None = None,
        linked_report_ids: list[str] | None = None,
        extension_bundle_ids: list[str] | None = None,
        extension_policy_set_ids: list[str] | None = None,
        extension_bundle_families: list[str] | None = None,
        extension_provenance: list[dict[str, Any]] | None = None,
        artifacts_produced: list[str],
        status: str,
        schedule_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        item = self.recipe_catalog.get(recipe_id) or {}
        record = self.execution_store.record(
            recipe_id=recipe_id,
            execution_kind=item.get("kind", "recipe"),
            ao_association=item.get("ao_targets", []),
            trigger_source=trigger_source,
            parameter_set=parameter_set,
            linked_trace_ids=linked_trace_ids,
            linked_subagent_ids=linked_subagent_ids,
            policy_path=policy_path,
            approval_path=approval_path,
            gateway_decision_path=gateway_decision_path,
            gateway_resolution_id=((gateway_decision_path or [{}])[0] or {}).get("resolution_id"),
            gateway_execution_id=gateway_execution_id,
            gateway_report_id=gateway_report_id,
            execution_path=execution_path,
            approval_fallback_chain=approval_fallback_chain,
            adversary_review_report_ids=adversary_review_report_ids,
            linked_report_ids=linked_report_ids,
            extension_bundle_ids=extension_bundle_ids,
            extension_policy_set_ids=extension_policy_set_ids,
            extension_bundle_families=extension_bundle_families,
            extension_provenance=extension_provenance,
            artifacts_produced=artifacts_produced,
            status=status,
            schedule_id=schedule_id,
            metadata=metadata or {},
        )
        report = build_recipe_execution_report(artifacts_dir=self.artifacts_dir, record=record)
        record["report"] = report
        record["linked_report_ids"] = sorted(
            set([*record.get("linked_report_ids", []), report["report_id"], *record.get("adversary_review_report_ids", [])])
        )
        record["artifacts_produced"] = sorted(set([*record.get("artifacts_produced", []), report["payload_path"], report["markdown_path"]]))
        Path(record["artifact_path"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def summary(
        self,
        *,
        execution_kind: str | None = None,
        recipe_id: str | None = None,
        schedule_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ) -> dict[str, Any]:
        items = self.execution_store.list_executions(
            execution_kind=execution_kind,
            recipe_id=recipe_id,
            schedule_id=schedule_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )
        status_counts: dict[str, int] = {}
        flow_family_counts: dict[str, int] = {}
        latest_by_flow_family: dict[str, dict[str, Any]] = {}
        for item in items:
            status = str(item.get("status", "unknown"))
            status_counts[status] = status_counts.get(status, 0) + 1
            for family in item.get("flow_families", []):
                flow_family_counts[family] = flow_family_counts.get(family, 0) + 1
                latest_by_flow_family.setdefault(
                    family,
                    {
                        "execution_id": item.get("execution_id"),
                        "recipe_id": item.get("recipe_id"),
                        "execution_kind": item.get("execution_kind"),
                        "status": item.get("status"),
                        "trigger_source": item.get("trigger_source"),
                        "gateway_resolution_id": item.get("gateway_resolution_id"),
                        "report_id": ((item.get("report") or {}).get("report_id")),
                    },
                )
        latest = items[0] if items else {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "execution_kind": execution_kind or "all",
            "recipe_id": recipe_id,
            "schedule_id": schedule_id,
            "trigger_source": trigger_source,
            "status_filter": status,
            "execution_count": len(items),
            "status_counts": status_counts,
            "latest_execution": latest or None,
            "latest_report_id": ((latest.get("report") or {}).get("report_id")),
            "latest_gateway_resolution_id": latest.get("gateway_resolution_id")
            or (((latest.get("gateway_decision_path") or [{}])[0] or {}).get("resolution_id")),
            "latest_gateway_execution_id": latest.get("gateway_execution_id"),
            "latest_gateway_report_id": latest.get("gateway_report_id"),
            "latest_adversary_report_ids": latest.get("adversary_review_report_ids", []),
            "latest_linked_trace_ids": latest.get("linked_trace_ids", []),
            "latest_linked_subagent_ids": latest.get("linked_subagent_ids", []),
            "latest_linked_report_ids": latest.get("linked_report_ids", []),
            "latest_extension_bundle_ids": latest.get("extension_bundle_ids", []),
            "latest_extension_policy_set_ids": latest.get("extension_policy_set_ids", []),
            "latest_extension_bundle_families": latest.get("extension_bundle_families", []),
            "latest_flow_families": latest.get("flow_families", []),
            "flow_family_counts": flow_family_counts,
            "latest_by_flow_family": latest_by_flow_family,
            "latest_artifacts_produced": latest.get("artifacts_produced", []),
            "latest_human_summary": ((latest.get("report") or {}).get("human_summary")),
            "report_ids": [(((item.get("report") or {}).get("report_id"))) for item in items if (item.get("report") or {}).get("report_id")],
            "compare_refs": {
                "history": (
                    "/ops/brain/runbooks/history"
                    if execution_kind == "runbook"
                    else "/ops/brain/recipes/history"
                    if execution_kind == "recipe"
                    else "/ops/brain/recipes/history"
                ),
                "history_detail_template": (
                    "/ops/brain/runbooks/history/{execution_id}"
                    if execution_kind == "runbook"
                    else "/ops/brain/recipes/history/{execution_id}"
                ),
                "history_compare": (
                    "/ops/brain/runbooks/history/compare"
                    if execution_kind == "runbook"
                    else "/ops/brain/recipes/history/compare"
                ),
            },
            "items": items,
        }

    def detail(self, execution_id: str) -> dict[str, Any] | None:
        record = self.execution_store.get(execution_id)
        if record is None:
            return None
        report = record.get("report") or {}
        payload = None
        markdown = None
        if report.get("payload_path"):
            try:
                payload = json.loads(Path(report["payload_path"]).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = None
        if report.get("markdown_path"):
            try:
                markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")
            except OSError:
                markdown = None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": record,
            "report_payload": payload,
            "report_markdown": markdown,
            "compare_refs": {
                "history": (
                    "/ops/brain/runbooks/history"
                    if record.get("execution_kind") == "runbook"
                    else "/ops/brain/recipes/history"
                ),
                "history_compare": (
                    "/ops/brain/runbooks/history/compare"
                    if record.get("execution_kind") == "runbook"
                    else "/ops/brain/recipes/history/compare"
                ),
            },
        }

    def compare(self, left_execution_id: str, right_execution_id: str) -> dict[str, Any] | None:
        comparison = self.execution_store.compare(left_execution_id, right_execution_id)
        if comparison is None:
            return None
        return {
            **comparison,
            "compare_refs": {
                "recipe_history": "/ops/brain/recipes/history",
                "runbook_history": "/ops/brain/runbooks/history",
            },
        }
