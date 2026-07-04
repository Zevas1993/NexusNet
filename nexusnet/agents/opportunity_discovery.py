from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


class WorkActivityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_id: str
    title: str
    description: str = ""
    frontstage: bool = False
    no_go_zone: bool = False
    repetitive: bool = False
    rule_based: bool = False
    high_volume: bool = False
    low_judgment: bool = False
    requires_relationship: bool = False
    requires_empathy: bool = False
    requires_physical_presence: bool = False
    requires_judgment: bool = False
    self_contained: bool = False
    error_recovery: bool = False
    hours_per_week: float = 0.0
    prep_hours_per_week: float = 0.0
    judgment_hours_per_week: float = 0.0
    occurrences_per_week: int = 1
    systems: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    measurable_outcome: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentOpportunityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activities: list[WorkActivityRequest] = Field(default_factory=list)
    requested_by: str = "NexusBrain"
    upstream_forward_radar_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentOpportunityDiscovery:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "agents" / "opportunity-discovery" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._latest_summary: dict[str, Any] | None = self._load_latest()

    def discover(self, request: AgentOpportunityRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AgentOpportunityRequest) else AgentOpportunityRequest.model_validate(request)
        upstream_forward_radar_gate = _upstream_forward_radar_gate(normalized)
        opportunities: list[dict[str, Any]] = []
        no_go_zones: list[dict[str, Any]] = []
        for activity in normalized.activities:
            if _is_no_go(activity):
                no_go_zones.append(_no_go_zone(activity))
                continue
            opportunity = _opportunity(activity, upstream_forward_radar_gate=upstream_forward_radar_gate)
            if opportunity:
                opportunities.append(opportunity)

        opportunities.sort(key=lambda item: (item["reclaimable_hours_per_week"], item["activity_id"]), reverse=True)
        blocked_opportunity_count = sum(1 for opportunity in opportunities if opportunity.get("ready_for_agent_build") is False)
        forward_radar_blocked = _forward_radar_blocked(upstream_forward_radar_gate)
        summary = {
            "status_label": "LOCKED CANON",
            "surface_id": "agent-opportunity-discovery",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if blocked_opportunity_count or forward_radar_blocked else ("live-bound" if normalized.activities else "static-canon"),
            "requested_by": normalized.requested_by,
            "created_at": utcnow().isoformat(),
            "activity_count": len(normalized.activities),
            "opportunity_count": len(opportunities),
            "blocked_opportunity_count": blocked_opportunity_count,
            "no_go_count": len(no_go_zones),
            "total_reclaimable_hours_per_week": round(sum(item["reclaimable_hours_per_week"] for item in opportunities), 2),
            "opportunities": opportunities,
            "no_go_zones": no_go_zones,
            "upstream_forward_radar_gate": upstream_forward_radar_gate,
            "aaa_layers": ["automation", "augmentation", "autonomy"],
            "frontstage_boundary": "relationships-judgment-empathy-physical-presence-and-human-taste-remain-human-owned",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._latest_summary = summary
        self._persist(summary)
        return summary

    def summary(self) -> dict[str, Any]:
        if self._latest_summary:
            return self._latest_summary
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "agent-opportunity-discovery",
            "authority": "NexusBrain",
            "runtime_state": "static-canon",
            "activity_count": 0,
            "opportunity_count": 0,
            "blocked_opportunity_count": 0,
            "no_go_count": 0,
            "total_reclaimable_hours_per_week": 0.0,
            "opportunities": [],
            "no_go_zones": [],
            "aaa_layers": ["automation", "augmentation", "autonomy"],
            "frontstage_boundary": "relationships-judgment-empathy-physical-presence-and-human-taste-remain-human-owned",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "control_panel_label": "Agent Opportunity Discovery",
            "source_documents": [
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md#ai-org-chart",
                "https://github.com/coleam00/ai-transformation-workshop",
            ],
            "operating_model": [
                "frontstage_backstage_map",
                "aaa_automation_augmentation_autonomy",
                "specialized_agents_not_monoliths",
                "metrics_and_boundaries_before_autonomy",
            ],
        }

    def _persist(self, summary: dict[str, Any]) -> None:
        if self.records_dir is None:
            return
        path = self.records_dir / "latest-summary.json"
        summary["artifact_path"] = str(path)
        path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    def _load_latest(self) -> dict[str, Any] | None:
        if self.records_dir is None:
            return None
        path = self.records_dir / "latest-summary.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None


def _is_no_go(activity: WorkActivityRequest) -> bool:
    return bool(
        activity.no_go_zone
        or (activity.frontstage and (activity.requires_relationship or activity.requires_empathy))
        or activity.requires_physical_presence
    )


def _no_go_zone(activity: WorkActivityRequest) -> dict[str, Any]:
    return {
        "activity_id": activity.activity_id,
        "title": activity.title,
        "automation_allowed": False,
        "human_owned_reasons": _human_reasons(activity),
        "safe_ai_role": "prep_assistant_only",
        "systems": activity.systems,
        "evidence_refs": activity.evidence_refs,
    }


def _opportunity(activity: WorkActivityRequest, *, upstream_forward_radar_gate: dict[str, Any] | None = None) -> dict[str, Any] | None:
    backstage_score = sum(
        1
        for value in [
            activity.repetitive,
            activity.rule_based,
            activity.high_volume,
            activity.low_judgment,
            activity.self_contained,
            bool(activity.measurable_outcome),
        ]
        if value
    )
    prep_heavy = activity.prep_hours_per_week > activity.judgment_hours_per_week and activity.prep_hours_per_week > 0
    if backstage_score < 2 and not prep_heavy:
        return None

    aaa_layer = _aaa_layer(activity, backstage_score, prep_heavy)
    reclaimable = activity.prep_hours_per_week if prep_heavy else activity.hours_per_week
    upstream_forward_radar_gate = upstream_forward_radar_gate or {}
    forward_radar_blocked = _forward_radar_blocked(upstream_forward_radar_gate)
    boundaries = _boundaries(activity, aaa_layer)
    if forward_radar_blocked:
        boundaries.append("forward_radar_promotion_gate_required")
    return {
        "activity_id": activity.activity_id,
        "title": activity.title,
        "aaa_layer": aaa_layer,
        "agent_title": f"{_title_case(activity.title)} Agent",
        "human_role": "decision_owner" if aaa_layer == "augmentation" else "exception_reviewer",
        "reclaimable_hours_per_week": round(reclaimable, 2),
        "systems": activity.systems,
        "skills": _skills(activity, aaa_layer),
        "tools_needed": activity.systems,
        "boundaries": boundaries,
        "success_metrics": _success_metrics(activity),
        "evidence_refs": activity.evidence_refs,
        "ready_for_agent_build": not forward_radar_blocked,
        "opportunity_gate_state": "blocked-by-forward-radar" if forward_radar_blocked else "build-ready",
        "upstream_forward_radar_gate": upstream_forward_radar_gate,
        "specialization_rule": "one-agent-one-job-with-clear-inputs-outputs-metrics-and-boundaries",
    }


def _aaa_layer(activity: WorkActivityRequest, backstage_score: int, prep_heavy: bool) -> str:
    if (
        activity.metadata.get("autonomy_candidate")
        and activity.self_contained
        and activity.error_recovery
        and bool(activity.measurable_outcome)
        and backstage_score >= 5
    ):
        return "autonomy"
    if prep_heavy or activity.requires_judgment:
        return "augmentation"
    return "automation"


def _human_reasons(activity: WorkActivityRequest) -> list[str]:
    reasons: list[str] = []
    if activity.requires_relationship:
        reasons.append("relationship_trust")
    if activity.requires_empathy:
        reasons.append("empathy")
    if activity.requires_physical_presence:
        reasons.append("physical_presence")
    if activity.requires_judgment:
        reasons.append("judgment")
    if activity.frontstage:
        reasons.append("frontstage")
    return reasons or ["operator_declared_no_go_zone"]


def _skills(activity: WorkActivityRequest, aaa_layer: str) -> list[str]:
    skills = ["evidence_collection", "structured_output"]
    if activity.rule_based:
        skills.append("rules_execution")
    if activity.high_volume:
        skills.append("queue_triage")
    if aaa_layer == "augmentation":
        skills.append("decision_briefing")
    if aaa_layer == "autonomy":
        skills.append("exception_recovery")
    return sorted(set(skills))


def _boundaries(activity: WorkActivityRequest, aaa_layer: str) -> list[str]:
    boundaries = [
        "human_review_for_external_commitments",
        "no_secret_exports",
        "audit_log_required",
    ]
    if activity.requires_judgment or aaa_layer == "augmentation":
        boundaries.append("human_retains_final_decision")
    if aaa_layer == "autonomy":
        boundaries.append("rollback_and_exception_queue_required")
    return boundaries


def _success_metrics(activity: WorkActivityRequest) -> list[str]:
    metrics = ["hours_reclaimed_per_week", "exception_rate", "human_acceptance_rate"]
    if activity.measurable_outcome:
        metrics.insert(0, activity.measurable_outcome)
    return metrics


def _upstream_forward_radar_gate(request: AgentOpportunityRequest) -> dict[str, Any]:
    gate = request.upstream_forward_radar_gate or {}
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "status": gate.get("status") or "not_provided",
        "radar_id": gate.get("radar_id") or "",
        "blockers": sorted(set(str(item) for item in gate.get("blockers") or [])),
        "source": gate.get("source") or "forward_radar",
    }


def _forward_radar_blocked(upstream_forward_radar_gate: dict[str, Any]) -> bool:
    return bool(
        upstream_forward_radar_gate.get("promotion_allowed") is False
        or upstream_forward_radar_gate.get("status") == "blocked"
        or upstream_forward_radar_gate.get("blockers")
    )


def _title_case(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value)
    return " ".join(word[:1].upper() + word[1:] for word in words) or "Backstage Work"


def _required_controls() -> list[str]:
    return [
        "frontstage_backstage_classification",
        "no_go_zone_gate",
        "aaa_layer_classification",
        "specialist_agent_boundary",
        "success_metrics",
        "human_review_boundary",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/agent-opportunities"},
        "discover": {"method": "POST", "endpoint": "/ops/brain/agent-opportunities/discover"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/agent-opportunities"},
    }
