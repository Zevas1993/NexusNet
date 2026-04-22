from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..schemas import TeacherAssignment, TeacherProfile, TeacherRoutingDecision
from .ensemble import TeacherEnsemblePolicy


@dataclass(frozen=True)
class TeacherRoutingContext:
    subject: str
    task_type: str
    budget_class: str = "STANDARD"
    output_form: str = "SHORT_ANSWER"
    risk_tier: str = "medium"
    modality: str = "text"
    local_vs_remote_availability: str = "local_first"
    coding_tool_need: bool = False
    thinking_vs_nonthinking_need: str = "adaptive"
    hardware_device_constraints: list[str] = field(default_factory=list)
    registry_layer_preference: str | None = None
    allow_remote: bool = False
    lineage: str = "live-derived"
    benchmark_family: str | None = None
    native_takeover_candidate_id: str | None = None


class TeacherRoutingPolicyEngine:
    def __init__(self, routing_policy: dict[str, Any]):
        self.routing_policy = routing_policy
        self._ensemble = TeacherEnsemblePolicy()

    def route(
        self,
        *,
        context: TeacherRoutingContext,
        assignments: dict[tuple[str, str], TeacherAssignment],
        profiles: dict[str, TeacherProfile],
        active_teacher_id: str | None = None,
    ) -> TeacherRoutingDecision:
        preferred_layer = context.registry_layer_preference or self.routing_policy.get("default_registry_layer", "v2026_live")
        assignment = assignments.get((context.subject, preferred_layer))
        if assignment is None:
            assignment = assignments.get((context.subject, "v2026_live")) or assignments.get((context.subject, "historical"))
        if assignment is None:
            assignment = assignments.get(("core-brain", preferred_layer)) or assignments[("core-brain", "historical")]

        if assignment.registry_layer == "historical":
            decision = self._ensemble.choose(
                subject=assignment.subject,
                assignment=assignment,
                profiles=profiles,
                active_teacher_id=active_teacher_id,
            )
            return decision.model_copy(
                update={
                    "registry_layer": "historical",
                    "selected_teacher_ids": [decision.selected_teacher_id],
                    "selected_roles": {"primary": decision.selected_teacher_id},
                    "budget_class": context.budget_class,
                    "output_form": context.output_form,
                    "risk_tier": context.risk_tier,
                    "modality": context.modality,
                    "teacher_confidence": 0.82,
                    "benchmark_family": context.benchmark_family,
                }
            )

        selected_roles = self._selected_roles(assignment=assignment, assignments=assignments)
        selected_teacher_id = selected_roles["primary"]
        candidates = list(assignment.teacher_ids)
        fallback_chain = list(assignment.fallback_teacher_ids)
        arbitration_needed = False
        arbitration_trigger = None

        if active_teacher_id and active_teacher_id in candidates:
            selected_teacher_id = active_teacher_id
        else:
            selected_teacher_id = self._select_live_teacher(context=context, assignment=assignment, profiles=profiles, selected_roles=selected_roles)

        if context.risk_tier.lower() == "high":
            arbitration_needed = True
            arbitration_trigger = "high_risk"
        elif context.output_form == "EVAL_JUDGE":
            arbitration_needed = True
            arbitration_trigger = "teacher_disagreement"
        elif selected_teacher_id != assignment.primary_teacher_id:
            arbitration_needed = True
            arbitration_trigger = "remote_escalation"

        selected_ids = _dedupe(
            [
                selected_teacher_id,
                selected_roles.get("secondary"),
                selected_roles.get("critique"),
                selected_roles.get("efficiency"),
            ]
        )
        rationale = self._build_rationale(context=context, assignment=assignment, selected_teacher_id=selected_teacher_id, selected_roles=selected_roles)
        return TeacherRoutingDecision(
            subject=assignment.subject,
            registry_layer="v2026_live",
            candidates=candidates,
            selected_teacher_id=selected_teacher_id,
            selected_teacher_ids=selected_ids,
            selected_roles={key: value for key, value in selected_roles.items() if value},
            policy=assignment.routing_mode,
            fallback_chain=fallback_chain,
            arbitration_needed=arbitration_needed,
            arbitration_trigger=arbitration_trigger,
            locality_preference=assignment.locality_preference,
            budget_class=context.budget_class,
            output_form=context.output_form,
            risk_tier=context.risk_tier,
            modality=context.modality,
            teacher_confidence=self._confidence(selected_teacher_id, assignment),
            benchmark_family=context.benchmark_family,
            historical_anchor_ref=assignment.historical_anchor_ref,
            rationale=rationale,
            status_label=assignment.status_label,
        )

    def arbitration_result(self, decision: TeacherRoutingDecision) -> str:
        if decision.selected_roles.get("efficiency"):
            return "PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY"
        if decision.output_form == "TOOL_CALL_STRICT_JSON":
            return "DUAL_PASS_TOOL_THEN_FINAL"
        return "SELECT_BEST"

    def _selected_roles(self, *, assignment: TeacherAssignment, assignments: dict[tuple[str, str], TeacherAssignment]) -> dict[str, str | None]:
        critique_assignment = assignments.get((assignment.critique_arbiter_subject or "critique", "v2026_live")) or assignments.get(
            (assignment.critique_arbiter_subject or "critique", "historical")
        )
        critique_teacher_id = critique_assignment.primary_teacher_id if critique_assignment else None
        return {
            "primary": assignment.primary_teacher_id or (assignment.teacher_ids[0] if assignment.teacher_ids else None),
            "secondary": assignment.secondary_teacher_id,
            "critique": critique_teacher_id,
            "efficiency": assignment.optional_efficiency_coach_id if self._allow_efficiency_coach(assignment.subject) else None,
        }

    def _select_live_teacher(
        self,
        *,
        context: TeacherRoutingContext,
        assignment: TeacherAssignment,
        profiles: dict[str, TeacherProfile],
        selected_roles: dict[str, str | None],
    ) -> str:
        primary_id = selected_roles["primary"] or assignment.primary_teacher_id
        secondary_id = selected_roles.get("secondary") or assignment.secondary_teacher_id
        if not primary_id:
            return assignment.teacher_ids[0]

        primary = profiles.get(primary_id)
        secondary = profiles.get(secondary_id) if secondary_id else None
        if context.local_vs_remote_availability == "remote_preferred" and secondary and secondary.capability_card and secondary.capability_card.locality == "remote_only":
            return secondary.teacher_id
        if context.budget_class == "EDGE_CONSTRAINED" and secondary and secondary.capability_card and secondary.capability_card.budget_class == "edge_constrained":
            return secondary.teacher_id
        if any(flag in {"low_vram", "cpu_only"} for flag in context.hardware_device_constraints):
            edge_candidates = [teacher_id for teacher_id in assignment.teacher_ids if profiles.get(teacher_id) and profiles[teacher_id].capability_card and profiles[teacher_id].capability_card.budget_class == "edge_constrained"]
            if edge_candidates:
                return edge_candidates[0]
        return primary.teacher_id if primary else primary_id

    def _allow_efficiency_coach(self, subject: str) -> bool:
        defaults = self.routing_policy.get("domain_defaults", {})
        lane = defaults.get(subject, {}).get("lfm2_lane")
        if not lane:
            return False
        allowed = self.routing_policy.get("lfm2", {}).get("allowed_lanes", [])
        return lane in allowed

    def _build_rationale(
        self,
        *,
        context: TeacherRoutingContext,
        assignment: TeacherAssignment,
        selected_teacher_id: str,
        selected_roles: dict[str, str | None],
    ) -> str:
        parts = [
            f"Selected '{selected_teacher_id}' for subject '{assignment.subject}' from registry layer '{assignment.registry_layer}'.",
            f"budget={context.budget_class}",
            f"output={context.output_form}",
            f"risk={context.risk_tier}",
        ]
        if selected_roles.get("secondary"):
            parts.append(f"secondary='{selected_roles['secondary']}'")
        if selected_roles.get("efficiency"):
            parts.append(f"bounded-efficiency='{selected_roles['efficiency']}'")
        if assignment.historical_anchor_ref:
            parts.append(f"historical-anchor='{assignment.historical_anchor_ref}'")
        return " ".join(parts)

    def _confidence(self, selected_teacher_id: str, assignment: TeacherAssignment) -> float:
        if selected_teacher_id == assignment.primary_teacher_id:
            return 0.92
        if selected_teacher_id == assignment.secondary_teacher_id:
            return 0.84
        if selected_teacher_id == assignment.optional_efficiency_coach_id:
            return 0.73
        return 0.68


def _dedupe(values: list[str | None]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.append(value)
    return seen
