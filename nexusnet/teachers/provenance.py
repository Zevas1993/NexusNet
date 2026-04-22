from __future__ import annotations

from ..schemas import AttachedTeacher, TeacherArbitrationRecord, TeacherProfile, TeacherRoutingDecision


def teacher_provenance_payload(
    *,
    profile: TeacherProfile,
    model_id: str,
    attach_role: str,
    capability_profile: dict,
    registry_layer: str,
    routing_decision: TeacherRoutingDecision | None = None,
    arbitration: TeacherArbitrationRecord | None = None,
    lineage: str = "live-derived",
    benchmark_family: str | None = None,
    threshold_set_id: str | None = None,
    native_takeover_candidate_id: str | None = None,
) -> dict:
    decision = routing_decision.model_dump(mode="json") if routing_decision is not None else {}
    arbitration_payload = arbitration.model_dump(mode="json") if arbitration is not None else {}
    selected_roles = decision.get("selected_roles", {})
    selected_teacher_ids = decision.get("selected_teacher_ids") or ([profile.teacher_id] if not selected_roles else list(selected_roles.values()))
    return {
        "teacher_id": profile.teacher_id,
        "canonical_name": profile.canonical_name,
        "status_label": profile.status_label,
        "lineage": profile.lineage,
        "canonical_teacher_lineage": profile.lineage,
        "role": profile.role,
        "role_tags": profile.role_tags,
        "mentor": profile.mentor,
        "model_id": model_id,
        "attach_role": attach_role,
        "registry_layer": registry_layer,
        "registry_layers": profile.registry_layers,
        "selected_teachers": selected_teacher_ids,
        "selected_teacher_roles": selected_roles or {"primary": profile.teacher_id},
        "local_vs_remote": _local_vs_remote(profile=profile, model_id=model_id),
        "reasoning_mode": _reasoning_mode(profile),
        "arbitration_result": arbitration_payload.get("arbitration_result") or "SELECT_BEST",
        "benchmark_family": benchmark_family or decision.get("benchmark_family"),
        "threshold_set_id": threshold_set_id,
        "dream_derived": lineage == "dream-derived",
        "live_derived": lineage == "live-derived",
        "teacher_confidence": arbitration_payload.get("teacher_confidence") or decision.get("teacher_confidence", 0.0),
        "native_takeover_candidate_id": native_takeover_candidate_id,
        "capability_card": profile.capability_card.model_dump(mode="json") if profile.capability_card else {},
        "capability_profile": capability_profile,
        "retirement": profile.retirement,
        "historical_anchor_ref": decision.get("historical_anchor_ref"),
        "routing_decision": decision,
        "arbitration": arbitration_payload,
    }


def attached_teacher_snapshot(attached: AttachedTeacher, profile: TeacherProfile | None) -> dict:
    return {
        "teacher_id": attached.teacher_id,
        "model_id": attached.model_id,
        "attach_role": attached.attach_role,
        "active": attached.active,
        "status_label": attached.status_label,
        "role": profile.role if profile else attached.provenance.get("role"),
        "role_tags": profile.role_tags if profile else attached.provenance.get("role_tags", []),
        "mentor": profile.mentor if profile else attached.provenance.get("mentor", False),
        "registry_layers": profile.registry_layers if profile else attached.provenance.get("registry_layers", []),
        "provenance": attached.provenance,
    }


def _local_vs_remote(*, profile: TeacherProfile, model_id: str) -> str:
    locality = profile.capability_card.locality if profile.capability_card else "local_first"
    if locality == "remote_only":
        return "remote"
    if locality == "mixed_local_then_remote":
        return "mixed"
    if model_id.startswith("openai/"):
        return "remote"
    return "local"


def _reasoning_mode(profile: TeacherProfile) -> str | None:
    if not profile.capability_card or not profile.capability_card.reasoning_modes:
        return None
    return profile.capability_card.reasoning_modes[0]
