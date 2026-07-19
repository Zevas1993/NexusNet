from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import stat
import tempfile
import time
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


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
    "cp",
    "create",
    "edit",
    "exec",
    "execute",
    "merge",
    "mkdir",
    "move",
    "mv",
    "pull",
    "push",
    "remove",
    "reset",
    "rebase",
    "rename",
    "rm",
    "overwrite",
    "replace",
    "rmdir",
    "run",
    "save",
    "stage",
    "touch",
    "truncate",
    "unlink",
    "update",
}
ELEVATED_TOOL_REFS = {"cmd", "powershell", "shell", "terminal"}
UNKNOWN_SANDBOX_STATES = {"", "none", "unknown"}
RELEASE_WRAPPER_READY_SANDBOX_STATES = {
    "production-spine-lifecycle-rollback-quarantine",
    "production-spine-lifecycle-shadow-approved",
    "production-spine-lifecycle-shadow-artifact-sandbox",
    "release-wrapper-admin-approved-privacy-retention-passivation",
}
RELEASE_WRAPPER_SHADOW_SANDBOX_STATES = {
    "release-wrapper-privacy-retention-shadow-observation",
    "release-wrapper-runtime-growth-shadow-observation",
    "release-wrapper-shadow-observation",
}
READY_SANDBOX_STATES = (
    {"operator-sandbox-ready", "ready", "sandbox-ready", "session-shadow"}
    | RELEASE_WRAPPER_READY_SANDBOX_STATES
)
ALLOWED_SANDBOX_STATES = READY_SANDBOX_STATES | RELEASE_WRAPPER_SHADOW_SANDBOX_STATES | UNKNOWN_SANDBOX_STATES | {"session-readonly"}
SURFACE_ID = "tool-action-harness"
AUTHORITY = "NexusBrain"
TRACE_CONTRACT = "plan-only-replayable-no-direct-tool-execution"
EXECUTION_TRACE_CONTRACT = "lease-gated-sandboxed-readonly-tool-execution"
READ_ONLY_ACTIONS = {"read", "list", "hash"}
MAX_READ_BYTES = 1_048_576
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
    "previous_record_digest",
    "record_digest",
}
HASHED_PLAN_FILENAME = re.compile(r"^[0-9a-f]{64}\.json$")
EXECUTION_RECEIPT_KEYS = {
    "surface_id", "authority", "execution_id", "action_id", "tool_ref", "action_type",
    "target_digest", "sandbox_root_digest", "lease_id", "capability", "status", "executed",
    "execution_allowed", "findings", "execution_authority_reason", "evidence_ref_count",
    "evidence_digest", "result_digest", "result_metadata", "error_category",
    "raw_content_included", "trace_contract", "duration_ms", "recorded_at", "receipt_digest",
}
AUTHORITY_REASON_CATEGORIES = {
    "allowed", "authority_invalid_response", "authority_unavailable", "capability_mismatch",
    "denied", "lease_expired", "lease_not_found", "lease_not_granted", "lease_required",
    "mutation_not_available", "not_evaluated", "scope_mismatch",
}
AUTHORITY_DENIAL_REASONS = {
    "authority_invalid_response", "authority_unavailable", "capability_mismatch", "denied",
    "lease_expired", "lease_not_found", "lease_not_granted", "scope_mismatch",
}
SANDBOX_ERROR_CATEGORIES = {
    "FileNotFoundError", "IsADirectoryError", "NotADirectoryError", "OSError",
    "PermissionError", "UnicodeError", "ValueError",
}
EXECUTION_STATUS_FLAGS = {
    "blocked-plan-only": (False, False),
    "blocked-evidence": (False, False),
    "blocked-authority": (False, False),
    "blocked-sandbox": (False, True),
    "executed-readonly": (True, True),
}


class SafeReadOnlyToolbox:
    """Filesystem-only read/list/hash operations confined to one resolved root."""

    def __init__(self, sandbox_root: Path | str) -> None:
        self.root = Path(sandbox_root).resolve()
        if not self.root.is_dir():
            raise ValueError("sandbox_root must resolve to an existing directory")

    def run(self, action_type: str, target: str) -> dict[str, Any]:
        action = str(action_type).strip().lower()
        if action not in READ_ONLY_ACTIONS:
            raise ValueError("unsupported read-only tool action")
        path = self._resolve_target(target)
        if action == "read":
            with self._open_regular_file(path) as handle:
                if os.fstat(handle.fileno()).st_size > MAX_READ_BYTES:
                    raise ValueError("read target exceeds the read-only size limit")
                content = handle.read(MAX_READ_BYTES + 1)
            if len(content) > MAX_READ_BYTES:
                raise ValueError("read target exceeds the read-only size limit")
            return {"text": content.decode("utf-8")}
        if action == "list":
            if not path.is_dir():
                raise ValueError("list target must be a directory")
            return {"entries": sorted(item.name for item in path.iterdir())}
        digest = hashlib.sha256()
        with self._open_regular_file(path) as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
        return {"sha256": digest.hexdigest()}

    def _resolve_target(self, target: str) -> Path:
        candidate = Path(target)
        if candidate.is_absolute():
            raise PermissionError("absolute tool targets are not allowed")
        resolved = (self.root / candidate).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError("tool target escapes the sandbox root") from exc
        return resolved

    def _open_regular_file(self, path: Path) -> Any:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("read-only tool target must be a regular file")
            opened_path = self._opened_file_path(descriptor)
            if opened_path is not None:
                try:
                    opened_path.relative_to(self.root)
                except ValueError as exc:
                    raise PermissionError("opened tool target escapes the sandbox root") from exc
            return os.fdopen(descriptor, "rb")
        except Exception:
            os.close(descriptor)
            raise

    def _opened_file_path(self, descriptor: int) -> Path | None:
        if os.name == "nt":
            import ctypes
            import msvcrt

            handle = msvcrt.get_osfhandle(descriptor)
            buffer = ctypes.create_unicode_buffer(32_768)
            length = ctypes.windll.kernel32.GetFinalPathNameByHandleW(
                ctypes.c_void_p(handle), buffer, len(buffer), 0
            )
            if length == 0 or length >= len(buffer):
                raise OSError("unable to resolve opened Windows file handle")
            value = buffer.value
            if value.startswith("\\\\?\\UNC\\"):
                value = "\\\\" + value[8:]
            elif value.startswith("\\\\?\\"):
                value = value[4:]
            return Path(value).resolve()
        proc_handle = Path("/proc/self/fd") / str(descriptor)
        if proc_handle.exists():
            return proc_handle.resolve()
        return None


class ToolActionHarness:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "tools" / "action-harness" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.executions_dir = self.plans_dir / "executions" if self.plans_dir else None
        if self.executions_dir is not None:
            self.executions_dir.mkdir(parents=True, exist_ok=True)
        self._plans: list[dict[str, Any]] = []
        self._executions: list[dict[str, Any]] = []

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
        normalized_action_id = self._validate_string("action_id", action_id)
        normalized_action_type = self._validate_string("action_type", action_type)
        normalized_tool_ref = self._validate_string("tool_ref", tool_ref)
        normalized_sandbox_state = self._validate_sandbox_state(sandbox_state)
        normalized_private = self._validate_bool("contains_private_data", contains_private_data)
        normalized_operator_approved = self._validate_bool("operator_approved", operator_approved)
        normalized_evidence_refs = self._validate_string_list("evidence_refs", evidence_refs)
        mutating = self._is_mutating_action(
            action_id=normalized_action_id,
            tool_ref=normalized_tool_ref,
            action_type=normalized_action_type,
        )

        findings = self._derive_findings(
            action_id=normalized_action_id,
            tool_ref=normalized_tool_ref,
            action_type=normalized_action_type,
            contains_private_data=normalized_private,
            sandbox_state=normalized_sandbox_state,
            operator_approved=normalized_operator_approved,
            evidence_refs=normalized_evidence_refs,
        )
        existing_plans = self._list_plans()
        plan = {
            "surface_id": SURFACE_ID,
            "authority": AUTHORITY,
            "action_id": normalized_action_id,
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
            "sequence": self._next_sequence(existing_plans),
            "previous_record_digest": existing_plans[0]["record_digest"] if existing_plans else "",
        }
        plan["record_digest"] = self._record_digest(plan)
        self._persist(plan)
        return copy.deepcopy(plan)

    def execute_action(
        self, *, action_id: str, tool_ref: str, action_type: str, target: str,
        evidence_refs: list[str], sandbox_root: Path | str, execution_authority: Any | None = None,
        lease_id: str | None = None, capability: str = "deterministic_tool_boundary",
    ) -> dict[str, Any]:
        """Execute a safe filesystem observation after a matching authority lease check."""
        started = time.perf_counter()
        action_id = self._validate_string("action_id", action_id)
        tool_ref = self._validate_string("tool_ref", tool_ref)
        action_type = self._validate_string("action_type", action_type)
        target = self._validate_string("target", target)
        evidence_refs = self._validate_string_list("evidence_refs", evidence_refs)
        capability = self._validate_string("capability", capability)
        root = Path(sandbox_root).resolve()
        root_digest, target_digest = self._digest_text(str(root)), self._digest_text(target)
        lease_id = lease_id.strip() if isinstance(lease_id, str) else ""
        if self._is_mutating_action(action_id=action_id, tool_ref=tool_ref, action_type=action_type):
            return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
                "blocked-plan-only", False, False, ["mutating_action_not_executable_plan_only"], "mutation_not_available",
                evidence_refs, None, "", started)
        if not evidence_refs:
            return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
                "blocked-evidence", False, False, ["tool_action_requires_evidence_refs"], "not_evaluated", evidence_refs, None, "", started)
        if execution_authority is None or not lease_id:
            return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
                "blocked-authority", False, False, ["execution_authority_lease_required"], "lease_required", evidence_refs, None, "", started)
        scope = {"tool_ref": tool_ref, "action_type": action_type, "target": target,
                 "sandbox_root_digest": root_digest.removeprefix("sha256:")}
        authority_failure = ""
        try:
            evaluation = execution_authority.evaluate(lease_id=lease_id, capability=capability, scope=scope)
        except KeyError:
            authority_failure = "lease_not_found"
        except Exception:
            authority_failure = "authority_unavailable"
        else:
            try:
                if type(evaluation) is not dict or type(evaluation.get("decision")) is not dict:
                    raise TypeError("authority evaluation must contain a plain decision object")
                decision = evaluation["decision"]
                if decision.get("execution_allowed") is True:
                    if not self._authority_allow_decision_matches(
                            decision, lease_id=lease_id, capability=capability, scope=scope):
                        authority_failure = "authority_invalid_response"
                elif decision.get("execution_allowed") is False:
                    authority_failure = self._authority_reason_category(decision.get("reason"))
                else:
                    authority_failure = "authority_invalid_response"
            except Exception:
                authority_failure = "authority_invalid_response"
        if authority_failure:
            return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
                "blocked-authority", False, False, [f"execution_authority::{authority_failure}"], authority_failure,
                evidence_refs, None, "", started)
        try:
            result = SafeReadOnlyToolbox(root).run(action_type, target)
        except (OSError, PermissionError, UnicodeError, ValueError) as exc:
            return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
                "blocked-sandbox", False, True, ["execution_error"], "allowed", evidence_refs, None,
                self._sandbox_error_category(exc), started)
        return self._finish_execution(action_id, tool_ref, action_type, target_digest, root_digest, lease_id, capability,
            "executed-readonly", True, True, [], "allowed", evidence_refs, result, "", started)

    def summary(self) -> dict[str, Any]:
        plans = self._list_plans()
        executions = self._list_executions()
        return {
            "surface_id": SURFACE_ID,
            "authority": AUTHORITY,
            "runtime_state": "degraded"
            if any(plan.get("status") == "blocked" for plan in plans)
            or any(execution.get("status", "").startswith("blocked") for execution in executions)
            else ("live-bound" if plans or executions else "static-canon"),
            "plan_count": len(plans),
            "latest_plan": copy.deepcopy(plans[0]) if plans else None,
            "execution_count": len(executions),
            "latest_execution": copy.deepcopy(executions[0]) if executions else None,
        }

    def _finish_execution(self, action_id: str, tool_ref: str, action_type: str, target_digest: str,
                          sandbox_root_digest: str, lease_id: str, capability: str, status: str, executed: bool,
                          execution_allowed: bool, findings: list[str], authority_reason: str,
                          evidence_refs: list[str], result: dict[str, Any] | None, error_category: str,
                          started: float) -> dict[str, Any]:
        execution_id = self._execution_id(action_id, lease_id, target_digest, sandbox_root_digest)
        receipt = {"surface_id": SURFACE_ID, "authority": AUTHORITY, "execution_id": execution_id,
            "action_id": action_id, "tool_ref": tool_ref, "action_type": action_type, "target_digest": target_digest,
            "sandbox_root_digest": sandbox_root_digest, "lease_id": lease_id, "capability": capability, "status": status,
            "executed": bool(executed), "execution_allowed": bool(execution_allowed), "findings": list(findings),
            "execution_authority_reason": authority_reason, "evidence_ref_count": len(evidence_refs),
            "evidence_digest": self._digest_payload(evidence_refs), "result_digest": self._digest_payload(result) if result is not None else "",
            "result_metadata": self._result_metadata(result), "error_category": error_category, "raw_content_included": False,
            "trace_contract": EXECUTION_TRACE_CONTRACT, "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "recorded_at": utcnow().isoformat()}
        receipt["receipt_digest"] = self._receipt_digest(receipt)
        self._persist_execution(receipt)
        response = copy.deepcopy(receipt)
        if result is not None:
            response["result"] = copy.deepcopy(result)
        return response

    def _persist_execution(self, receipt: dict[str, Any]) -> None:
        if self.executions_dir is None:
            self._executions.insert(0, copy.deepcopy(receipt))
            return
        path = self._execution_artifact_path(receipt["execution_id"])
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.executions_dir, delete=False) as handle:
            temporary_path = Path(handle.name)
            handle.write(json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)
        self._validate_execution_receipt(json.loads(path.read_text(encoding="utf-8")), path=path)
        self._executions.insert(0, copy.deepcopy(receipt))

    def _execution_artifact_path(self, execution_id: str) -> Path:
        if self.executions_dir is None:
            raise ValueError("executions_dir is required for persisted tool execution receipts")
        path = self.executions_dir / f"{execution_id}.json"
        if path.resolve().parent != self.executions_dir.resolve():
            raise ValueError("tool execution receipt path escaped executions directory")
        return path

    def _list_executions(self) -> list[dict[str, Any]]:
        executions: dict[str, dict[str, Any]] = {}
        for receipt in self._executions:
            try: executions.setdefault(self._validate_execution_receipt(receipt)["execution_id"], self._validate_execution_receipt(receipt))
            except (TypeError, ValueError): pass
        if self.executions_dir is not None:
            for path in self.executions_dir.glob("*.json"):
                try:
                    receipt = self._validate_execution_receipt(json.loads(path.read_text(encoding="utf-8")), path=path)
                    executions.setdefault(receipt["execution_id"], receipt)
                except (OSError, TypeError, ValueError, json.JSONDecodeError): pass
        return sorted((copy.deepcopy(item) for item in executions.values()), key=lambda item: (item["recorded_at"], item["execution_id"]), reverse=True)

    def _validate_execution_receipt(self, payload: Any, *, path: Path | None = None) -> dict[str, Any]:
        if not isinstance(payload, dict) or set(payload) != EXECUTION_RECEIPT_KEYS:
            raise ValueError("tool execution receipt keys do not match the public schema")
        if path is not None and not HASHED_PLAN_FILENAME.fullmatch(path.name):
            raise ValueError("tool execution receipt filename must be a sha256 artifact name")
        receipt = {"surface_id": self._validate_string("surface_id", payload["surface_id"]),
            "authority": self._validate_string("authority", payload["authority"]),
            "execution_id": self._validate_string("execution_id", payload["execution_id"]),
            "action_id": self._validate_string("action_id", payload["action_id"]),
            "tool_ref": self._validate_string("tool_ref", payload["tool_ref"]),
            "action_type": self._validate_string("action_type", payload["action_type"]),
            "target_digest": self._validate_digest("target_digest", payload["target_digest"]),
            "sandbox_root_digest": self._validate_digest("sandbox_root_digest", payload["sandbox_root_digest"]),
            "lease_id": self._validate_optional_string("lease_id", payload["lease_id"]),
            "capability": self._validate_string("capability", payload["capability"]),
            "status": self._validate_string("status", payload["status"]),
            "executed": self._validate_bool("executed", payload["executed"]),
            "execution_allowed": self._validate_bool("execution_allowed", payload["execution_allowed"]),
            "findings": self._validate_string_list("findings", payload["findings"]),
            "execution_authority_reason": self._validate_string("execution_authority_reason", payload["execution_authority_reason"]),
            "evidence_ref_count": self._validate_nonnegative_int("evidence_ref_count", payload["evidence_ref_count"]),
            "evidence_digest": self._validate_digest("evidence_digest", payload["evidence_digest"]),
            "result_digest": self._validate_optional_digest("result_digest", payload["result_digest"]),
            "result_metadata": self._validate_result_metadata(payload["result_metadata"]),
            "error_category": self._validate_optional_string("error_category", payload["error_category"]),
            "raw_content_included": self._validate_bool("raw_content_included", payload["raw_content_included"]),
            "trace_contract": self._validate_string("trace_contract", payload["trace_contract"]),
            "duration_ms": self._validate_duration(payload["duration_ms"]),
            "recorded_at": self._validate_string("recorded_at", payload["recorded_at"]),
            "receipt_digest": self._validate_digest("receipt_digest", payload["receipt_digest"])}
        if receipt["surface_id"] != SURFACE_ID or receipt["authority"] != AUTHORITY or receipt["trace_contract"] != EXECUTION_TRACE_CONTRACT:
            raise ValueError("tool execution receipt authority fields are invalid")
        if receipt["raw_content_included"] is not False:
            raise ValueError("tool execution receipt must not contain raw content")
        if receipt["execution_authority_reason"] not in AUTHORITY_REASON_CATEGORIES:
            raise ValueError("tool execution receipt authority reason is not allowlisted")
        expected_flags = EXECUTION_STATUS_FLAGS.get(receipt["status"])
        if expected_flags is None or (receipt["executed"], receipt["execution_allowed"]) != expected_flags:
            raise ValueError("tool execution receipt status flags are inconsistent")
        self._validate_execution_semantics(receipt)
        if receipt["execution_id"] != self._execution_id(receipt["action_id"], receipt["lease_id"], receipt["target_digest"], receipt["sandbox_root_digest"]):
            raise ValueError("tool execution receipt id does not match its safe inputs")
        if receipt["receipt_digest"] != self._receipt_digest(receipt):
            raise ValueError("tool execution receipt digest does not match its safe fields")
        if path is not None and path.name != f"{receipt['execution_id']}.json":
            raise ValueError("tool execution receipt filename does not match receipt id")
        return receipt

    def _execution_id(self, action_id: str, lease_id: str, target_digest: str, sandbox_root_digest: str) -> str:
        return hashlib.sha256(json.dumps({"action_id": action_id, "lease_id": lease_id, "target_digest": target_digest,
            "sandbox_root_digest": sandbox_root_digest}, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

    def _receipt_digest(self, receipt: dict[str, Any]) -> str:
        return self._digest_payload({key: value for key, value in receipt.items() if key != "receipt_digest"})

    def _authority_allow_decision_matches(self, decision: dict[str, Any], *, lease_id: str,
                                          capability: str, scope: dict[str, Any]) -> bool:
        encoded_scope = json.dumps(scope, sort_keys=True, separators=(",", ":"), default=str)
        expected_scope_hash = hashlib.sha256(encoded_scope.encode("utf-8")).hexdigest()[:16]
        binding_values = tuple(decision.get(key) for key in ("lease_id", "capability", "scope_hash", "reason"))
        return (all(type(value) is str for value in binding_values)
                and decision.get("lease_id") == lease_id
                and decision.get("capability") == capability
                and decision.get("scope_hash") == expected_scope_hash
                and decision.get("reason") == "allowed")

    def _authority_reason_category(self, reason: Any) -> str:
        if type(reason) is not str:
            return "authority_invalid_response"
        normalized = reason.strip().lower() or "denied"
        return normalized if normalized in AUTHORITY_DENIAL_REASONS else "denied"

    def _sandbox_error_category(self, error: Exception) -> str:
        for error_type, category in (
            (PermissionError, "PermissionError"),
            (FileNotFoundError, "FileNotFoundError"),
            (IsADirectoryError, "IsADirectoryError"),
            (NotADirectoryError, "NotADirectoryError"),
            (UnicodeError, "UnicodeError"),
            (ValueError, "ValueError"),
            (OSError, "OSError"),
        ):
            if isinstance(error, error_type):
                return category
        return "OSError"

    def _validate_execution_semantics(self, receipt: dict[str, Any]) -> None:
        status = receipt["status"]
        reason = receipt["execution_authority_reason"]
        findings = receipt["findings"]
        error_category = receipt["error_category"]
        no_result = receipt["result_digest"] == "" and receipt["result_metadata"] == {
            "kind": "none", "item_count": 0,
        }

        if status == "executed-readonly":
            expected_kind = {"read": "text", "list": "entries", "hash": "sha256"}.get(receipt["action_type"])
            metadata = receipt["result_metadata"]
            valid_metadata = metadata.get("kind") == expected_kind
            if expected_kind in {"text", "sha256"}:
                valid_metadata = valid_metadata and metadata.get("item_count") == 1
            if expected_kind == "text":
                valid_metadata = valid_metadata and set(metadata) == {"kind", "item_count", "char_count"}
            elif expected_kind in {"entries", "sha256"}:
                valid_metadata = valid_metadata and set(metadata) == {"kind", "item_count"}
            if (reason != "allowed" or findings or error_category or not receipt["result_digest"]
                    or not valid_metadata):
                raise ValueError("executed tool receipt semantics are inconsistent")
            return

        if not no_result:
            raise ValueError("blocked tool receipt must not claim a result")
        if status == "blocked-plan-only":
            valid = (reason == "mutation_not_available"
                     and findings == ["mutating_action_not_executable_plan_only"]
                     and not error_category
                     and self._is_mutating_action(action_id=receipt["action_id"], tool_ref=receipt["tool_ref"],
                                                  action_type=receipt["action_type"]))
        elif status == "blocked-evidence":
            valid = reason == "not_evaluated" and findings == ["tool_action_requires_evidence_refs"] and not error_category
        elif status == "blocked-authority":
            expected_findings = (["execution_authority_lease_required"] if reason == "lease_required"
                                 else [f"execution_authority::{reason}"] if reason in AUTHORITY_DENIAL_REASONS else [])
            valid = bool(expected_findings) and findings == expected_findings and not error_category
        elif status == "blocked-sandbox":
            valid = (reason == "allowed" and findings == ["execution_error"]
                     and error_category in SANDBOX_ERROR_CATEGORIES)
        else:
            valid = False
        if not valid:
            raise ValueError("blocked tool receipt semantics are inconsistent")

    def _result_metadata(self, result: dict[str, Any] | None) -> dict[str, Any]:
        if result is None: return {"kind": "none", "item_count": 0}
        if "text" in result: return {"kind": "text", "item_count": 1, "char_count": len(str(result["text"]))}
        if "entries" in result: return {"kind": "entries", "item_count": len(list(result["entries"]))}
        if "sha256" in result: return {"kind": "sha256", "item_count": 1}
        return {"kind": "unknown", "item_count": len(result)}

    def _validate_result_metadata(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict): raise ValueError("result_metadata must be an object")
        metadata = {"kind": self._validate_string("result_metadata.kind", value.get("kind")),
            "item_count": self._validate_nonnegative_int("result_metadata.item_count", value.get("item_count"))}
        if "char_count" in value: metadata["char_count"] = self._validate_nonnegative_int("result_metadata.char_count", value["char_count"])
        if set(value) != set(metadata): raise ValueError("result_metadata contains unsupported fields")
        return metadata

    def _digest_text(self, value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    def _digest_payload(self, value: Any) -> str:
        return self._digest_text(json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True))

    def _persist(self, plan: dict[str, Any]) -> None:
        if self.plans_dir is None:
            self._plans.insert(0, copy.deepcopy(plan))
            return
        path = self._artifact_path_for_action_id(plan["action_id"])
        plan["artifact_path"] = path.name
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

    def _next_sequence(self, plans: list[dict[str, Any]] | None = None) -> int:
        plans = self._list_plans() if plans is None else plans
        sequences = [
            plan["sequence"]
            for plan in plans
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
        artifact_ref = plan["artifact_path"]
        if Path(artifact_ref).is_absolute() or Path(artifact_ref).name != artifact_ref:
            raise ValueError("tool action plan artifact_path must be a flat artifact ref")
        if "/" in artifact_ref or "\\" in artifact_ref or artifact_ref != expected_path.name:
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
            "sandbox_state": self._validate_sandbox_state(payload["sandbox_state"]),
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
            "previous_record_digest": self._validate_optional_string(
                "previous_record_digest",
                payload["previous_record_digest"],
            ),
            "record_digest": self._validate_string("record_digest", payload["record_digest"]),
        }
        if plan["sequence"] == 1 and plan["previous_record_digest"]:
            raise ValueError("first tool action plan cannot reference a previous digest")
        if plan["sequence"] > 1 and not plan["previous_record_digest"]:
            raise ValueError("tool action plan sequence requires previous digest")
        if plan["surface_id"] != SURFACE_ID or plan["authority"] != AUTHORITY:
            raise ValueError("tool action plan authority fields are invalid")
        if plan["trace_contract"] != TRACE_CONTRACT:
            raise ValueError("tool action plan trace contract is invalid")
        expected = self._derive_gate_fields(
            action_id=plan["action_id"],
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
        action_id: str,
        tool_ref: str,
        action_type: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = self._derive_findings(
            action_id=action_id,
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
                action_id=action_id,
                tool_ref=tool_ref,
                action_type=action_type,
            )
            or contains_private_data,
        }

    def _derive_findings(
        self,
        *,
        action_id: str,
        tool_ref: str,
        action_type: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> list[str]:
        findings = []
        mutating = self._is_mutating_action(action_id=action_id, tool_ref=tool_ref, action_type=action_type)
        if not evidence_refs:
            findings.append("tool_action_requires_evidence_refs")
        if mutating and not self._sandbox_ready(sandbox_state):
            findings.append("mutating_tool_action_requires_sandbox")
        if mutating and not operator_approved:
            findings.append("mutating_tool_action_requires_operator_confirmation")
        if contains_private_data and not operator_approved:
            findings.append("private_tool_context_requires_operator_confirmation")
        return findings

    def _is_mutating_action(self, *, action_id: str, tool_ref: str, action_type: str) -> bool:
        action_id_tokens = self._identifier_tokens(action_id)
        tool_tokens = self._identifier_tokens(tool_ref)
        action_tokens = self._identifier_tokens(action_type)
        all_tokens = action_id_tokens + action_tokens + tool_tokens
        if any(token in MUTATING_ACTION_TOKENS for token in all_tokens):
            return True
        if any(token in ELEVATED_TOOL_REFS for token in action_id_tokens + tool_tokens):
            return True
        return False

    def _identifier_tokens(self, value: str) -> list[str]:
        return [token for token in re.split(r"[^A-Za-z0-9]+", value.lower()) if token]

    def _sandbox_ready(self, sandbox_state: str) -> bool:
        return sandbox_state.strip().lower() in READY_SANDBOX_STATES

    def _validate_sandbox_state(self, value: Any) -> str:
        sandbox_state = self._validate_string("sandbox_state", value)
        if sandbox_state.strip().lower() not in ALLOWED_SANDBOX_STATES:
            raise ValueError("sandbox_state is not an allowed sandbox state")
        return sandbox_state

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

    def _validate_optional_string(self, name: str, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string")
        return value

    def _validate_bool(self, name: str, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean")
        return value

    def _validate_sequence(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("sequence must be a positive integer")
        return value

    def _validate_nonnegative_int(self, name: str, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
        return value

    def _validate_duration(self, value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError("duration_ms must be a non-negative number")
        return float(value)

    def _validate_digest(self, name: str, value: Any) -> str:
        digest = self._validate_string(name, value)
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"{name} must be a sha256 digest")
        return digest

    def _validate_optional_digest(self, name: str, value: Any) -> str:
        return "" if value == "" else self._validate_digest(name, value)
