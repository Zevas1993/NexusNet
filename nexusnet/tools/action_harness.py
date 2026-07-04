from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


MUTATING_ACTIONS = {"click", "type", "write", "submit", "delete", "shell", "install"}
# read-only actions that MAY actually execute inside the sandbox (everything else stays plan-only)
READONLY_ACTIONS = {"read", "list", "stat", "hash", "inspect"}


class SafeReadOnlyToolbox:
    """Real read-only tool executors confined to a sandbox root (no writes, no traversal, no network)."""

    def __init__(self, sandbox_root: Path | str) -> None:
        self.root = Path(sandbox_root).resolve()

    def _resolve(self, rel_path: str) -> Path:
        target = (self.root / rel_path).resolve()
        if self.root not in target.parents and target != self.root:
            raise PermissionError(f"path escapes sandbox: {rel_path}")
        return target

    def run(self, action_type: str, target: str, *, max_bytes: int = 4096) -> dict[str, Any]:
        path = self._resolve(target)
        if action_type in ("read", "inspect"):
            data = path.read_bytes()[:max_bytes]
            return {"bytes": len(data), "text": data.decode("utf-8", "replace"),
                    "truncated": path.stat().st_size > max_bytes}
        if action_type == "list":
            return {"entries": sorted(p.name for p in path.iterdir())}
        if action_type == "stat":
            st = path.stat()
            return {"size": st.st_size, "is_dir": path.is_dir()}
        if action_type == "hash":
            return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        raise ValueError(f"unsupported read-only action: {action_type}")


class ToolActionHarness:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "tools" / "action-harness" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
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
        mutating = action_type in MUTATING_ACTIONS
        findings = []
        if not evidence_refs:
            findings.append("tool_action_requires_evidence_refs")
        if mutating and sandbox_state in {"", "none", "unknown"}:
            findings.append("mutating_tool_action_requires_sandbox")
        if mutating and not operator_approved:
            findings.append("mutating_tool_action_requires_operator_confirmation")
        if contains_private_data and not operator_approved:
            findings.append("private_tool_context_requires_operator_confirmation")
        plan = {
            "surface_id": "tool-action-harness",
            "authority": "NexusBrain",
            "action_id": action_id,
            "tool_ref": tool_ref,
            "action_type": action_type,
            "requested_effect": requested_effect,
            "contains_private_data": contains_private_data,
            "sandbox_state": sandbox_state,
            "operator_approved": operator_approved,
            "evidence_refs": evidence_refs,
            "status": "blocked" if findings else "planned-shadow",
            "execution_allowed": False,
            "operator_confirmation_required": mutating or contains_private_data,
            "findings": findings,
            "trace_contract": "plan-only-replayable-no-direct-tool-execution",
        }
        self._persist(plan)
        return plan

    def execute_action(
        self,
        *,
        action_id: str,
        tool_ref: str,
        action_type: str,
        target: str,
        evidence_refs: list[str],
        sandbox_root: Path | str,
    ) -> dict[str, Any]:
        """Actually EXECUTE a read-only action inside the sandbox, capturing a real result + trace.

        Mutating/unknown actions are refused (they stay plan-only via plan_action). Missing evidence
        refs block execution. The record is a real, replayable execution trace - not a plan stub.
        """
        findings: list[str] = []
        if action_type in MUTATING_ACTIONS:
            findings.append("mutating_action_not_executable_plan_only")
        elif action_type not in READONLY_ACTIONS:
            findings.append("unknown_action_type_not_executable")
        if not evidence_refs:
            findings.append("tool_action_requires_evidence_refs")

        result: dict[str, Any] | None = None
        error: str | None = None
        started = time.perf_counter_ns()
        executed = False
        if not findings:
            try:
                result = SafeReadOnlyToolbox(sandbox_root).run(action_type, target)
                executed = True
            except Exception as exc:               # sandbox/permission/io error -> recorded, not raised
                error = f"{type(exc).__name__}: {exc}"[:200]
                findings.append("execution_error")
        duration_ms = (time.perf_counter_ns() - started) / 1e6

        record = {
            "surface_id": "tool-action-harness",
            "authority": "NexusBrain",
            "action_id": action_id,
            "tool_ref": tool_ref,
            "action_type": action_type,
            "target": target,
            "evidence_refs": evidence_refs,
            "executed": executed,
            "execution_allowed": executed,
            "status": "executed-readonly" if executed else "blocked",
            "result": result,
            "error": error,
            "findings": findings,
            "duration_ms": duration_ms,
            "trace_contract": "real-readonly-execution-sandboxed-no-mutation",
        }
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "tool-action-harness",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(plan.get("status") == "blocked" for plan in self._plans) else ("live-bound" if self._plans else "static-canon"),
            "plan_count": len(self._plans),
            "latest_plan": self._plans[0] if self._plans else None,
        }

    def _persist(self, plan: dict[str, Any]) -> None:
        self._plans.insert(0, plan)
        if self.root is None:
            return
        path = self.root / f"{plan['action_id'].replace(':', '_').replace('/', '_')}.json"
        plan["artifact_path"] = str(path)
        path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
