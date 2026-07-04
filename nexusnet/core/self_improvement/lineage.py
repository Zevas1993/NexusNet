from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ReviewerDecision = Literal[
    "proposed",
    "built-in-sandbox",
    "eval-failed",
    "safety-blocked",
    "shadow-passed",
    "teacher-approved",
    "operator-approved",
    "merged",
    "rolled-back",
]


class LineageCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    parent_ids: list[str] = Field(default_factory=list)
    mutation_prompt: str
    touched_files: list[str] = Field(default_factory=list)
    eval_suite_refs: list[str] = Field(default_factory=list)
    command_receipts: list[dict[str, Any]] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)
    transfer_results: dict[str, Any] = Field(default_factory=dict)
    safety_flags: list[str] = Field(default_factory=list)
    reviewer_decision: ReviewerDecision = "proposed"
    rollback_plan: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SelfImprovementLineageRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "self-improvement" / "lineage" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def record_candidate(self, request: LineageCandidateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, LineageCandidateRequest) else LineageCandidateRequest.model_validate(request)
        findings = _findings(normalized)
        missing_hashes = any(
            finding["rule_id"] == "lineage_candidate_requires_hashable_command_receipts" for finding in findings
        )
        anti_cheat_gate = {
            "real_receipts_present": bool(normalized.command_receipts) and not missing_hashes,
            "receipt_count": len(normalized.command_receipts),
        }
        promotion_allowed = (
            normalized.reviewer_decision in {"operator-approved", "merged"} and not findings and bool(normalized.rollback_plan)
        )
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "self-improvement-lineage",
            "candidate_id": normalized.candidate_id,
            "status": normalized.reviewer_decision,
            "runtime_state": "degraded" if findings or normalized.safety_flags else "live-bound",
            "created_at": utcnow().isoformat(),
            "lineage": {"parent_ids": normalized.parent_ids, "candidate_id": normalized.candidate_id},
            "mutation_prompt": normalized.mutation_prompt,
            "touched_files": normalized.touched_files,
            "eval_suite_refs": normalized.eval_suite_refs,
            "command_receipts": normalized.command_receipts,
            "scores": normalized.scores,
            "transfer_results": normalized.transfer_results,
            "safety_flags": normalized.safety_flags,
            "anti_cheat_gate": anti_cheat_gate,
            "findings": findings,
            "promotion_allowed": promotion_allowed,
            "promotion_boundary": "lineage-candidates-stay-shadow-until-eval-safety-transfer-rollback-and-operator-approval",
            "rollback_plan": normalized.rollback_plan,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "self-improvement-lineage",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(record.get("findings") or record.get("safety_flags") for record in records)
            else ("live-bound" if records else "static-canon"),
            "candidate_count": len(records),
            "latest_candidate": records[0] if records else None,
            "candidates": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{_safe_id(record['candidate_id'])}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("candidate_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("candidate_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _findings(request: LineageCandidateRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not request.eval_suite_refs:
        findings.append(
            {
                "rule_id": "lineage_candidate_requires_eval_suite_refs",
                "severity": "hard_fail",
                "message": "Lineage candidates require eval suite references.",
            }
        )
    if not request.command_receipts or any(not receipt.get("artifact_hash") for receipt in request.command_receipts):
        findings.append(
            {
                "rule_id": "lineage_candidate_requires_hashable_command_receipts",
                "severity": "hard_fail",
                "message": "Command receipts require artifact hashes.",
            }
        )
    if request.scores.get("safety", 1.0) < 0.85:
        findings.append(
            {
                "rule_id": "lineage_candidate_blocks_low_safety_score",
                "severity": "hard_fail",
                "message": "Safety score below 0.85 blocks promotion.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/self-improvement/lineage"},
        "record_candidate": {"method": "POST", "endpoint": "/ops/brain/self-improvement/lineage/candidates"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "candidate"
