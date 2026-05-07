from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


MUTATING_ACTIONS = {"click", "type", "write", "submit", "delete", "shell", "install"}
MUTATING_ACTION_TOKENS = MUTATING_ACTIONS | {
    "add",
    "append",
    "apply",
    "checkout",
    "chmod",
    "chown",
    "commit",
    "copy",
    "create",
    "edit",
    "exec",
    "execute",
    "merge",
    "mkdir",
    "move",
    "pull",
    "push",
    "remove",
    "reset",
    "rebase",
    "rename",
    "overwrite",
    "replace",
    "rmdir",
    "run",
    "save",
    "stage",
    "truncate",
    "update",
}
ELEVATED_TOOL_REFS = {"cmd", "powershell", "shell", "terminal"}
UNKNOWN_SANDBOX_STATES = {"", "none", "unknown"}
READY_SANDBOX_STATES = {"operator-sandbox-ready", "ready", "sandbox-ready", "session-shadow"}
SURFACE_ID = "tool-action-harness"
AUTHORITY = "NexusBrain"
TRACE_CONTRACT = "plan-only-replayable-no-direct-tool-execution"
REQUIRED_PLAN_KEYS = {
    "surface_id",
    "authority",
    "action_id",
    "tool_ref",
    "action_type",
    "requested_effect",
    "contains_private_data",
    "sandbox_state",
    "operator_approved",
    "evidence_refs",
    "status",
    "execution_allowed",
    "operator_confirmation_required",
    "findings",
    "trace_contract",
    "sequence",
    "record_digest",
}
HASHED_PLAN_FILENAME = re.compile(r"^[0-9a-f]{64}\.json$")


class ToolActionHarness:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "tools" / "action-harness" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._plans: list[dict[str, Any]] = []

    def plan_action(
        self,
        *,
        action_id: str,
        tool_ref: str,
        action_type: str,
        requested_effect: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        normalized_action_type = self._validate_string("action_type", action_type)
        normalized_tool_ref = self._validate_string("tool_ref", tool_ref)
        normalized_sandbox_state = self._validate_string("sandbox_state", sandbox_state)
        normalized_private = self._validate_bool("contains_private_data", contains_private_data)
        normalized_operator_approved = self._validate_bool("operator_approved", operator_approved)
        normalized_evidence_refs = self._validate_string_list("evidence_refs", evidence_refs)
        mutating = self._is_mutating_action(
            tool_ref=normalized_tool_ref,
            action_type=normalized_action_type,
        )

        findings = self._derive_findings(
            tool_ref=normalized_tool_ref,
            action_type=normalized_action_type,
            contains_private_data=normalized_private,
            sandbox_state=normalized_sandbox_state,
            operator_approved=normalized_operator_approved,
            evidence_refs=normalized_evidence_refs,
        )
        plan = {
            "surface_id": SURFACE_ID,
            "authority": AUTHORITY,
            "action_id": self._validate_string("action_id", action_id),
            "tool_ref": normalized_tool_ref,
            "action_type": normalized_action_type,
            "requested_effect": self._validate_string("requested_effect", requested_effect),
            "contains_private_data": normalized_private,
            "sandbox_state": normalized_sandbox_state,
            "operator_approved": normalized_operator_approved,
            "evidence_refs": normalized_evidence_refs,
            "status": "blocked" if findings else "planned-shadow",
            "execution_allowed": False,
            "operator_confirmation_required": mutating or normalized_private,
            "findings": findings,
            "trace_contract": TRACE_CONTRACT,
            "sequence": self._next_sequence(),
        }
        plan["record_digest"] = self._record_digest(plan)
        self._persist(plan)
        return copy.deepcopy(plan)

    def summary(self) -> dict[str, Any]:
        plans = self._list_plans()
        return {
            "surface_id": SURFACE_ID,
            "authority": AUTHORITY,
            "runtime_state": "degraded"
            if any(plan.get("status") == "blocked" for plan in plans)
            else ("live-bound" if plans else "static-canon"),
            "plan_count": len(plans),
            "latest_plan": copy.deepcopy(plans[0]) if plans else None,
        }

    def _persist(self, plan: dict[str, Any]) -> None:
        if self.plans_dir is None:
            self._plans.insert(0, copy.deepcopy(plan))
            return
        path = self._artifact_path_for_action_id(plan["action_id"])
        plan["artifact_path"] = str(path)
        payload = json.dumps(plan, allow_nan=False, indent=2, sort_keys=True)
        path.write_text(payload, encoding="utf-8")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        self._validate_persisted_plan(persisted, path=path)
        self._plans.insert(0, copy.deepcopy(plan))

    def _artifact_path_for_action_id(self, action_id: str) -> Path:
        if self.plans_dir is None:
            raise ValueError("plans_dir is required for persisted tool action plans")
        digest = hashlib.sha256(action_id.encode("utf-8")).hexdigest()
        path = self.plans_dir / f"{digest}.json"
        plans_root = self.plans_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != plans_root:
            raise ValueError("tool action plan artifact path escaped plans directory")
        return path

    def _list_plans(self) -> list[dict[str, Any]]:
        memory_by_action_id: dict[str, dict[str, Any]] = {}
        memory_order: list[str] = []
        for plan in self._plans:
            try:
                validated_plan = self._validate_plan_shape(plan)
            except (ValueError, TypeError):
                continue
            action_id = validated_plan["action_id"]
            if action_id in memory_by_action_id:
                continue
            memory_order.append(action_id)
            memory_by_action_id[action_id] = validated_plan

        disk_by_action_id: dict[str, tuple[str, dict[str, Any]]] = {}
        if self.plans_dir is not None:
            for path in sorted(self.plans_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    plan = self._validate_persisted_plan(payload, path=path)
                except (OSError, json.JSONDecodeError, ValueError, TypeError):
                    continue
                action_id = plan["action_id"]
                if action_id not in disk_by_action_id or plan["sequence"] > disk_by_action_id[action_id][1]["sequence"]:
                    disk_by_action_id[action_id] = (path.name, plan)

        plans = [copy.deepcopy(memory_by_action_id[action_id]) for action_id in memory_order]
        disk_only = [
            plan
            for action_id, (_, plan) in disk_by_action_id.items()
            if action_id not in memory_by_action_id
        ]
        disk_only.sort(key=lambda item: (item["sequence"], item["action_id"]), reverse=True)
        plans.extend(copy.deepcopy(plan) for plan in disk_only)
        return plans

    def _next_sequence(self) -> int:
        sequences = [
            plan["sequence"]
            for plan in self._list_plans()
            if isinstance(plan.get("sequence"), int) and not isinstance(plan.get("sequence"), bool)
        ]
        return (max(sequences) if sequences else 0) + 1

    def _validate_persisted_plan(self, payload: Any, *, path: Path) -> dict[str, Any]:
        if not HASHED_PLAN_FILENAME.fullmatch(path.name):
            raise ValueError("tool action plan filename must be a sha256 artifact name")
        plan = self._validate_plan_shape(payload)
        if "artifact_path" not in plan:
            raise ValueError("persisted tool action plan missing artifact_path")
        if not self._record_digest_matches(plan):
            raise ValueError("tool action plan digest does not match payload")
        expected_path = self._artifact_path_for_action_id(plan["action_id"])
        if path.resolve() != expected_path.resolve():
            raise ValueError("tool action plan filename does not match action id")
        artifact_path = Path(plan["artifact_path"])
        if artifact_path.resolve() != expected_path.resolve():
            raise ValueError("tool action plan artifact_path does not match action id")
        if artifact_path.name != expected_path.name:
            raise ValueError("tool action plan artifact_path filename does not match action id")
        return plan

    def _validate_plan_shape(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("tool action plan must be an object")
        if not REQUIRED_PLAN_KEYS.issubset(payload):
            raise ValueError("tool action plan missing required keys")
        plan = {
            "surface_id": self._validate_string("surface_id", payload["surface_id"]),
            "authority": self._validate_string("authority", payload["authority"]),
            "action_id": self._validate_string("action_id", payload["action_id"]),
            "tool_ref": self._validate_string("tool_ref", payload["tool_ref"]),
            "action_type": self._validate_string("action_type", payload["action_type"]),
            "requested_effect": self._validate_string("requested_effect", payload["requested_effect"]),
            "contains_private_data": self._validate_bool(
                "contains_private_data",
                payload["contains_private_data"],
            ),
            "sandbox_state": self._validate_string("sandbox_state", payload["sandbox_state"]),
            "operator_approved": self._validate_bool("operator_approved", payload["operator_approved"]),
            "evidence_refs": self._validate_string_list("evidence_refs", payload["evidence_refs"]),
            "status": self._validate_string("status", payload["status"]),
            "execution_allowed": self._validate_bool("execution_allowed", payload["execution_allowed"]),
            "operator_confirmation_required": self._validate_bool(
                "operator_confirmation_required",
                payload["operator_confirmation_required"],
            ),
            "findings": self._validate_string_list("findings", payload["findings"]),
            "trace_contract": self._validate_string("trace_contract", payload["trace_contract"]),
            "sequence": self._validate_sequence(payload["sequence"]),
            "record_digest": self._validate_string("record_digest", payload["record_digest"]),
        }
        if plan["surface_id"] != SURFACE_ID or plan["authority"] != AUTHORITY:
            raise ValueError("tool action plan authority fields are invalid")
        if plan["trace_contract"] != TRACE_CONTRACT:
            raise ValueError("tool action plan trace contract is invalid")
        expected = self._derive_gate_fields(
            tool_ref=plan["tool_ref"],
            action_type=plan["action_type"],
            contains_private_data=plan["contains_private_data"],
            sandbox_state=plan["sandbox_state"],
            operator_approved=plan["operator_approved"],
            evidence_refs=plan["evidence_refs"],
        )
        actual = {
            "findings": plan["findings"],
            "status": plan["status"],
            "execution_allowed": plan["execution_allowed"],
            "operator_confirmation_required": plan["operator_confirmation_required"],
        }
        if actual != expected:
            raise ValueError("tool action plan derived fields do not match inputs")
        if "artifact_path" in payload:
            plan["artifact_path"] = self._validate_string("artifact_path", payload["artifact_path"])
        return plan

    def _derive_gate_fields(
        self,
        *,
        tool_ref: str,
        action_type: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = self._derive_findings(
            tool_ref=tool_ref,
            action_type=action_type,
            contains_private_data=contains_private_data,
            sandbox_state=sandbox_state,
            operator_approved=operator_approved,
            evidence_refs=evidence_refs,
        )
        return {
            "findings": findings,
            "status": "blocked" if findings else "planned-shadow",
            "execution_allowed": False,
            "operator_confirmation_required": self._is_mutating_action(
                tool_ref=tool_ref,
                action_type=action_type,
            )
            or contains_private_data,
        }

    def _derive_findings(
        self,
        *,
        tool_ref: str,
        action_type: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> list[str]:
        findings = []
        mutating = self._is_mutating_action(tool_ref=tool_ref, action_type=action_type)
        if not evidence_refs:
            findings.append("tool_action_requires_evidence_refs")
        if mutating and not self._sandbox_ready(sandbox_state):
            findings.append("mutating_tool_action_requires_sandbox")
        if mutating and not operator_approved:
            findings.append("mutating_tool_action_requires_operator_confirmation")
        if contains_private_data and not operator_approved:
            findings.append("private_tool_context_requires_operator_confirmation")
        return findings

    def _is_mutating_action(self, *, tool_ref: str, action_type: str) -> bool:
        tool_tokens = self._identifier_tokens(tool_ref)
        action_tokens = self._identifier_tokens(action_type)
        if any(token in MUTATING_ACTION_TOKENS for token in action_tokens + tool_tokens):
            return True
        if any(token in ELEVATED_TOOL_REFS for token in tool_tokens):
            return True
        return False

    def _identifier_tokens(self, value: str) -> list[str]:
        return [token for token in re.split(r"[^A-Za-z0-9]+", value.lower()) if token]

    def _sandbox_ready(self, sandbox_state: str) -> bool:
        return sandbox_state.strip().lower() in READY_SANDBOX_STATES

    def _record_digest(self, plan: dict[str, Any]) -> str:
        digest_payload = {
            key: plan[key]
            for key in sorted(REQUIRED_PLAN_KEYS - {"record_digest"})
            if key in plan
        }
        payload = json.dumps(digest_payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
        return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

    def _record_digest_matches(self, plan: dict[str, Any]) -> bool:
        return plan["record_digest"] == self._record_digest(plan)

    def _validate_string_list(self, name: str, values: Any) -> list[str]:
        if not isinstance(values, list):
            raise ValueError(f"{name} must be a list")
        try:
            return [self._validate_string(name, value) for value in values]
        except ValueError as exc:
            if "non-empty string" in str(exc):
                raise ValueError(f"{name} must contain non-empty strings") from exc
            raise

    def _validate_string(self, name: str, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string")
        if not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
        return value

    def _validate_bool(self, name: str, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean")
        return value

    def _validate_sequence(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("sequence must be a positive integer")
        return value
