from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

import yaml

from nexus.schemas import new_id, utcnow
from nexusnet.recipes.reports import build_recipe_execution_report
from nexusnet.operations.change_passport import OperationalChangeRegistry


class WorkflowCatalogService:
    SAFE_NODE_KINDS = {
        "prompt",
        "bash",
        "approval",
        "validation",
        "artifact",
        "package_candidate",
        "parallel_run",
        "plan_review",
        "review",
        "self_healing",
    }
    DANGEROUS_BASH_MARKERS = ("rm -rf", "sudo ", "chmod 777", "chown ", "curl ", "Invoke-WebRequest", "iwr ")

    def __init__(
        self,
        *,
        config_dir: Path,
        artifacts_dir: Path,
        runtime_configs: dict[str, Any],
        execution_store: Any,
        gateway: Any | None = None,
        events: Any | None = None,
    ):
        repo_root = Path(__file__).resolve().parents[2]
        workflow_config = ((runtime_configs.get("goose_lane") or {}).get("workflows") or {})
        configured_roots = workflow_config.get("roots") or ["nexusnet/aos/workflows"]
        self.workflow_roots = [repo_root / root for root in configured_roots]
        self.workspace_workflow_root = Path(config_dir) / "workflows"
        self.artifacts_dir = Path(artifacts_dir)
        self.execution_store = execution_store
        self.operational_changes = OperationalChangeRegistry(artifacts_dir=self.artifacts_dir)
        self.gateway = gateway
        self.events = events

    def summary(self) -> dict[str, Any]:
        items = self.list_items()
        history = self.history(limit=12)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "schema_kind": "governed-workflow-dag",
            "workflow_count": len(items),
            "starter_workflow_ids": [item["workflow_id"] for item in items if item.get("starter")],
            "validation": self.validation_summary(items),
            "history": {
                "execution_count": history["execution_count"],
                "latest_execution_id": ((history.get("latest_execution") or {}).get("execution_id")),
                "latest_workflow_id": ((history.get("latest_execution") or {}).get("recipe_id")),
                "status_counts": history.get("status_counts", {}),
            },
            "event_log": self.events.summary(subject_prefix="workflow:", limit=50) if self.events else {},
            "compare_refs": {
                "summary": "/ops/brain/workflows",
                "execute": "/ops/brain/workflows/execute",
                "history": "/ops/brain/workflows/history",
            },
            "items": items,
        }

    def list_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for root in [*self.workflow_roots, self.workspace_workflow_root]:
            if not root.exists():
                continue
            for path in sorted(root.glob("*.yaml")):
                payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if not isinstance(payload, dict):
                    continue
                payload["source_path"] = str(path)
                payload.setdefault("starter", str(path).replace("\\", "/").endswith("/nexusnet/aos/workflows/" + path.name))
                payload["validation"] = self.validate_payload(payload)
                items.append(payload)
        items.sort(key=lambda item: str(item.get("workflow_id") or ""))
        return items

    def get(self, workflow_id: str) -> dict[str, Any] | None:
        for item in self.list_items():
            if item.get("workflow_id") == workflow_id:
                return item
        return None

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        nodes = payload.get("nodes") or []
        if not isinstance(nodes, list) or not nodes:
            errors.append({"reason": "missing-nodes", "node_id": None})
            return {"ok": False, "errors": errors, "topological_order": []}

        seen: set[str] = set()
        node_by_id: dict[str, dict[str, Any]] = {}
        for index, node in enumerate(nodes):
            node_id = str(node.get("id") or "")
            if not node_id:
                errors.append({"reason": "missing-node-id", "node_id": f"index-{index}"})
                continue
            if node_id in seen:
                errors.append({"reason": "duplicate-node-id", "node_id": node_id})
            seen.add(node_id)
            node_by_id.setdefault(node_id, node)
            kind = str(node.get("kind") or "prompt")
            if kind not in self.SAFE_NODE_KINDS:
                errors.append({"reason": "unsupported-node-kind", "node_id": node_id, "kind": kind})
            bash = str(node.get("bash") or "")
            if bash and any(marker.lower() in bash.lower() for marker in self.DANGEROUS_BASH_MARKERS):
                errors.append({"reason": "unsafe-bash-command", "node_id": node_id})

        for node_id, node in node_by_id.items():
            for dependency in node.get("depends_on", []) or []:
                if dependency not in node_by_id:
                    errors.append({"reason": "missing-dependency", "node_id": node_id, "dependency": dependency})

        order, cycle = self._topological_order(node_by_id)
        if cycle:
            errors.append({"reason": "cycle-detected", "node_id": cycle})

        return {"ok": not errors, "errors": errors, "topological_order": order if not cycle else []}

    def validation_summary(self, items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        items = items or self.list_items()
        errors = [
            {"workflow_id": item.get("workflow_id"), **error}
            for item in items
            for error in (item.get("validation") or self.validate_payload(item)).get("errors", [])
        ]
        return {"ok": not errors, "item_count": len(items), "error_count": len(errors), "errors": errors}

    def execute(
        self,
        *,
        workflow_id: str,
        trigger_source: str = "manual",
        workspace_id: str = "default",
        agent_id: str = "standard-wrapper-agent",
        parameter_set: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
        requested_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        approval_path: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        workflow = self.get(workflow_id)
        if workflow is None:
            raise KeyError(workflow_id)
        validation = self.validate_payload(workflow)
        if not validation["ok"]:
            raise ValueError(json.dumps(validation["errors"]))

        linked_trace_ids = list(linked_trace_ids or [])
        parameter_set = parameter_set or {}
        requested_tools = sorted(set([*(requested_tools or []), *self._workflow_requested_tools(workflow)]))
        requested_extensions = sorted(set([*(requested_extensions or []), *self._workflow_requested_extensions(workflow)]))
        subject = f"workflow:{workflow_id}"
        if self.events:
            self.events.record(event_type="workflow.start", subject=subject, trace_ids=linked_trace_ids, payload={"trigger_source": trigger_source})
            for tool in requested_tools:
                self.events.record(
                    event_type="tool.requested",
                    subject=subject,
                    trace_ids=linked_trace_ids,
                    payload={"tool": tool, "execution_allowed": False},
                )
            for extension_id in requested_extensions:
                self.events.record(
                    event_type="extension.requested",
                    subject=subject,
                    trace_ids=linked_trace_ids,
                    payload={"extension_id": extension_id, "mutation_requires_policy_grant": True},
                )

        gateway_resolution = None
        if self.gateway is not None and (requested_tools or requested_extensions):
            gateway_resolution = self.gateway.resolve(
                agent_id=agent_id,
                workspace_id=workspace_id,
                requested_tools=requested_tools,
                requested_extensions=requested_extensions,
                require_user_approval=True,
                trigger_source=f"workflow:{workflow_id}",
                linked_trace_ids=linked_trace_ids,
                record_gateway_flow=True,
            )

        node_states = []
        execution_path = []
        for node_id in validation["topological_order"]:
            node = next(item for item in workflow.get("nodes", []) if item.get("id") == node_id)
            if self.events:
                self.events.record(event_type="workflow.node.start", subject=f"{subject}:{node_id}", trace_ids=linked_trace_ids, payload={"kind": node.get("kind", "prompt")})
                if node.get("fresh_context"):
                    self.events.record(
                        event_type="session.forked",
                        subject=f"{subject}:{node_id}",
                        trace_ids=linked_trace_ids,
                        payload={"reason": "fresh_context", "execution_allowed": False},
                    )
            state = self._node_state(node)
            node_states.append(state)
            execution_path.append(
                {
                    "stage": state["node_id"],
                    "kind": state["kind"],
                    "status": state["status"],
                    "mutation_allowed": False,
                    "execution_allowed": False,
                }
            )
            if self.events:
                self.events.record(event_type="workflow.node.end", subject=f"{subject}:{node_id}", trace_ids=linked_trace_ids, payload=state)

        effective_status = status or self._overall_status(node_states)
        approval_decision = str(
            ((approval_path or {}).get("decision"))
            or ((gateway_resolution or {}).get("approval_path") or {}).get("decision")
            or "not-requested"
        )
        operational_change_passport = self.operational_changes.create(
            change_id=f"workflow-change:{workflow_id}:{self._stable_hash({'traces': linked_trace_ids, 'parameters': parameter_set})}",
            owner=str(parameter_set.get("owner") or agent_id),
            goal=str(workflow.get("label") or workflow_id),
            source_refs=[str(workflow.get("source_path") or f"workflow:{workflow_id}")],
            base_state_ref=str(parameter_set.get("base_state_ref") or "runtime:current"),
            worktree_ref=str(parameter_set.get("worktree_ref") or f"workspace:{workspace_id}"),
            affected_surfaces=[str(item.get("id")) for item in workflow.get("nodes", []) if item.get("id")],
            permissions=sorted(set(requested_tools or ["workflow:metadata"])),
            feature_flag=str(parameter_set.get("feature_flag") or f"workflow:{workflow_id}"),
            evidence_refs=linked_trace_ids or [f"workflow-validation:{self._stable_hash(validation)}"],
            telemetry_refs=linked_trace_ids or [f"workflow-event:{workflow_id}"],
            rollback_ref=str(parameter_set.get("rollback_ref") or f"workflow-checkpoints:{workflow_id}"),
            approval_refs=[f"approval:{approval_decision}"],
        )
        durable_ledger = self._durable_ledger(
            workflow_id=workflow_id,
            node_states=node_states,
            linked_trace_ids=linked_trace_ids,
            parameter_set=parameter_set,
            effective_status=effective_status,
        )
        report_stub = {
            "workflow_id": workflow_id,
            "status": effective_status,
            "node_states": node_states,
            "validation": validation,
            "gateway_resolution_id": (gateway_resolution or {}).get("resolution_id"),
            "durable_ledger": durable_ledger,
            "operational_change_passport": operational_change_passport,
        }
        record = self.execution_store.record(
            recipe_id=workflow_id,
            execution_kind="workflow",
            ao_association=workflow.get("ao_targets", []),
            trigger_source=trigger_source,
            parameter_set={
                **parameter_set,
                "requested_tools": requested_tools,
                "requested_extensions": requested_extensions,
                "workflow_validation": validation,
            },
            linked_trace_ids=linked_trace_ids,
            linked_subagent_ids=[],
            policy_path=(gateway_resolution or {}).get("policy_path", []),
            approval_path={**((gateway_resolution or {}).get("approval_path") or {}), **(approval_path or {})},
            gateway_decision_path=(gateway_resolution or {}).get("gateway_decision_path", []),
            gateway_resolution_id=(gateway_resolution or {}).get("resolution_id"),
            gateway_execution_id=((gateway_resolution or {}).get("execution_history") or {}).get("execution_id"),
            gateway_report_id=((gateway_resolution or {}).get("execution_history") or {}).get("report", {}).get("report_id"),
            execution_path=execution_path,
            approval_fallback_chain=(gateway_resolution or {}).get("approval_fallback_chain", []),
            adversary_review_report_ids=(gateway_resolution or {}).get("adversary_review_report_ids", []),
            linked_report_ids=(gateway_resolution or {}).get("linked_report_ids", []),
            extension_bundle_ids=(gateway_resolution or {}).get("extension_bundle_ids", []),
            extension_policy_set_ids=self._gateway_policy_set_ids(gateway_resolution),
            extension_bundle_families=self._gateway_bundle_families(gateway_resolution),
            extension_provenance=(gateway_resolution or {}).get("extension_provenance", []),
            artifacts_produced=[(gateway_resolution or {}).get("artifact_path")] if (gateway_resolution or {}).get("artifact_path") else [],
            status=effective_status,
            report=report_stub,
            metadata={
                "workflow_id": workflow_id,
                "workflow_label": workflow.get("label"),
                "gateway_resolution_id": (gateway_resolution or {}).get("resolution_id"),
                "requested_tools": requested_tools,
                "requested_extensions": requested_extensions,
                "durable_ledger": durable_ledger,
                "operational_change_passport": operational_change_passport,
                "execution_allowed": False,
                "mutation_allowed": False,
            },
        )
        report = build_recipe_execution_report(artifacts_dir=self.artifacts_dir, record=record)
        record["report"] = report
        record["linked_report_ids"] = sorted(set([*record.get("linked_report_ids", []), report["report_id"]]))
        record["artifacts_produced"] = sorted(
            set([artifact for artifact in [*record.get("artifacts_produced", []), report["payload_path"], report["markdown_path"]] if artifact])
        )
        Path(record["artifact_path"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
        payload = {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workflow_id": workflow_id,
            "status": effective_status,
            "execution_allowed": False,
            "mutation_allowed": False,
            "node_states": node_states,
            "durable_ledger": durable_ledger,
            "operational_change_passport": operational_change_passport,
            "validation": validation,
            "gateway_resolution": gateway_resolution,
            "execution_history": record,
            "artifact_path": record["artifact_path"],
            "report": report,
            "compare_refs": {
                "summary": "/ops/brain/workflows",
                "history": "/ops/brain/workflows/history",
            },
        }
        if self.events:
            self.events.record(event_type="workflow.end", subject=subject, trace_ids=linked_trace_ids, payload={"status": effective_status, "execution_id": record["execution_id"]})
        return payload

    def history(
        self,
        *,
        workflow_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        items = self.execution_store.list_executions(
            execution_kind="workflow",
            recipe_id=workflow_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )
        status_counts: dict[str, int] = {}
        for item in items:
            item_status = str(item.get("status") or "unknown")
            status_counts[item_status] = status_counts.get(item_status, 0) + 1
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "execution_kind": "workflow",
            "workflow_id": workflow_id,
            "execution_count": len(items),
            "status_counts": status_counts,
            "latest_execution": items[0] if items else None,
            "event_type_counts": (self.events.summary(subject_prefix="workflow:", limit=200).get("event_type_counts", {}) if self.events else {}),
            "items": items,
        }

    def _topological_order(self, nodes: dict[str, dict[str, Any]]) -> tuple[list[str], str | None]:
        temporary: set[str] = set()
        permanent: set[str] = set()
        order: list[str] = []

        def visit(node_id: str) -> str | None:
            if node_id in permanent:
                return None
            if node_id in temporary:
                return node_id
            temporary.add(node_id)
            for dependency in nodes.get(node_id, {}).get("depends_on", []) or []:
                if dependency in nodes:
                    cycle = visit(str(dependency))
                    if cycle:
                        return cycle
            temporary.remove(node_id)
            permanent.add(node_id)
            order.append(node_id)
            return None

        for node_id in nodes:
            cycle = visit(node_id)
            if cycle:
                return [], cycle
        return order, None

    def _node_state(self, node: dict[str, Any]) -> dict[str, Any]:
        kind = str(node.get("kind") or "prompt")
        status = "recorded"
        if kind == "approval":
            status = "approval_required"
        elif kind == "validation":
            status = "validation_pending"
        elif kind == "bash":
            status = "policy_recorded_no_execution"
        return {
            "node_id": node.get("id"),
            "kind": kind,
            "status": status,
            "depends_on": node.get("depends_on", []) or [],
            "fresh_context": bool(node.get("fresh_context", False)),
            "loop": node.get("loop"),
            "artifacts": node.get("artifacts", []) or [],
        }

    def _durable_ledger(
        self,
        *,
        workflow_id: str,
        node_states: list[dict[str, Any]],
        linked_trace_ids: list[str],
        parameter_set: dict[str, Any],
        effective_status: str,
    ) -> dict[str, Any]:
        checkpoints = [
            {
                "checkpoint_id": f"{workflow_id}:{state['node_id']}",
                "node_id": state["node_id"],
                "status": state["status"],
                "state_edit_allowed": False,
                "resume_pointer": index + 1 if index + 1 < len(node_states) else None,
            }
            for index, state in enumerate(node_states)
        ]
        return {
            "ledger_kind": "durable-run-ledger",
            "metadata_only": True,
            "mutation_allowed": False,
            "execution_allowed": False,
            "workflow_id": workflow_id,
            "status": effective_status,
            "checkpoint_count": len(checkpoints),
            "checkpoints": checkpoints,
            "resume": {
                "state": "available_after_policy_grant",
                "resume_from": checkpoints[-1]["checkpoint_id"] if checkpoints else None,
                "requires_gateway_grant": True,
                "requires_product_sweep_pass": True,
            },
            "interrupts": [
                {
                    "reason": "human_state_edit_requires_policy",
                    "state_edit_allowed": False,
                    "operator_visible": True,
                }
            ],
            "replay": {
                "deterministic_replay_supported": True,
                "metadata_only": True,
                "linked_trace_ids": linked_trace_ids,
                "parameter_hash": self._stable_hash(parameter_set),
            },
            "human_state_edit": {
                "allowed": False,
                "approval_path": "gateway-and-product-sweep-required",
            },
        }

    def _overall_status(self, node_states: list[dict[str, Any]]) -> str:
        statuses = {item.get("status") for item in node_states}
        if "approval_required" in statuses:
            return "approval_required"
        if "validation_pending" in statuses:
            return "validation_pending"
        return "gated"

    def _workflow_requested_tools(self, workflow: dict[str, Any]) -> list[str]:
        requested: set[str] = set(workflow.get("requested_tools", []) or [])
        for node in workflow.get("nodes", []) or []:
            requested.update(node.get("requested_tools", []) or [])
        return sorted(requested)

    def _workflow_requested_extensions(self, workflow: dict[str, Any]) -> list[str]:
        requested: set[str] = set(workflow.get("requested_extensions", []) or [])
        for node in workflow.get("nodes", []) or []:
            requested.update(node.get("requested_extensions", []) or [])
        return sorted(requested)

    def _gateway_policy_set_ids(self, gateway_resolution: dict[str, Any] | None) -> list[str]:
        return sorted(
            {
                item.get("policy_set_id")
                for item in (gateway_resolution or {}).get("extension_provenance", [])
                if item.get("policy_set_id")
            }
        )

    def _gateway_bundle_families(self, gateway_resolution: dict[str, Any] | None) -> list[str]:
        return sorted(
            {
                item.get("bundle_family")
                for item in (gateway_resolution or {}).get("extension_provenance", [])
                if item.get("bundle_family")
            }
        )

    def _stable_hash(self, payload: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]
