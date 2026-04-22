from __future__ import annotations

from ..schemas import TeacherAssignment, TeacherProfile, TeacherRoutingDecision


class TeacherEnsemblePolicy:
    def choose(
        self,
        *,
        subject: str,
        assignment: TeacherAssignment,
        profiles: dict[str, TeacherProfile],
        active_teacher_id: str | None = None,
    ) -> TeacherRoutingDecision:
        candidates = [teacher_id for teacher_id in assignment.teacher_ids if teacher_id in profiles]
        if active_teacher_id and active_teacher_id in candidates:
            selected = active_teacher_id
            rationale = "Retaining the wrapper-selected active teacher inside the canonical ensemble lane."
        else:
            ranked = sorted(
                (profiles[teacher_id] for teacher_id in candidates),
                key=lambda profile: (profile.available, not profile.retired, profile.arbitration_weight, profile.mentor),
                reverse=True,
            )
            selected = ranked[0].teacher_id if ranked else assignment.teacher_ids[0]
            rationale = (
                f"Selected '{selected}' via policy '{assignment.arbitration_policy}' using canonical teacher availability, "
                "retirement state, and arbitration weight."
            )
        return TeacherRoutingDecision(
            subject=subject,
            registry_layer=assignment.registry_layer,
            candidates=candidates or assignment.teacher_ids,
            selected_teacher_id=selected,
            selected_teacher_ids=[selected],
            selected_roles={"primary": selected},
            policy=assignment.arbitration_policy,
            locality_preference=assignment.locality_preference,
            budget_class="STANDARD",
            output_form="SHORT_ANSWER",
            risk_tier="medium",
            teacher_confidence=0.8 if selected == active_teacher_id else 0.75,
            rationale=rationale,
            status_label=assignment.status_label,
        )
