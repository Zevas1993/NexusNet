from __future__ import annotations

from ..schemas import IndependenceMetrics, TeacherProfile, TeacherRetirementDecision


class TeacherRetirementAdvisor:
    def evaluate(self, profile: TeacherProfile, independence: IndependenceMetrics | None = None) -> TeacherRetirementDecision:
        independence = independence or IndependenceMetrics()
        if "historical" in profile.registry_layers:
            return TeacherRetirementDecision(
                teacher_id=profile.teacher_id,
                registry_layer="historical",
                decision="hold",
                rationale=f"Historical teacher '{profile.teacher_id}' remains immutable canon and cannot enter retirement shadow review.",
                evidence={
                    "historical_immutable": True,
                    "dependency_ratio": independence.dependency_ratio,
                    "native_generation": independence.native_generation,
                    "teacher_replacement_ready": independence.teacher_replacement_ready,
                    "external_evaluation_passed": False,
                    "rollback_path_exists": False,
                    "governance_signed_off": False,
                },
                rollback_required=True,
                governance_required=True,
                external_evaluation_required=True,
            )
        threshold = float(profile.retirement.get("minimum_native_takeover_score", 0.85))
        native_score = max(independence.native_generation, 1.0 - independence.dependency_ratio)
        if independence.teacher_replacement_ready and native_score >= threshold:
            decision = "shadow"
            rationale = (
                f"Internal capability for '{profile.teacher_id}' has crossed the configured threshold "
                f"({native_score:.2f} >= {threshold:.2f}); keep replacement shadow-only until benchmark surpass evidence, "
                "EvalsAO approval, rollback readiness, and governance sign-off exist."
            )
        else:
            decision = "hold"
            rationale = (
                f"Teacher '{profile.teacher_id}' remains active because native takeover evidence "
                f"({native_score:.2f}) has not cleared the configured threshold ({threshold:.2f})."
            )
        return TeacherRetirementDecision(
            teacher_id=profile.teacher_id,
            registry_layer="historical" if "historical" in profile.registry_layers else "v2026_live",
            decision=decision,
            rationale=rationale,
            evidence={
                "dependency_ratio": independence.dependency_ratio,
                "native_generation": independence.native_generation,
                "teacher_replacement_ready": independence.teacher_replacement_ready,
                "threshold": threshold,
                "external_evaluation_passed": False,
                "rollback_path_exists": False,
                "governance_signed_off": False,
            },
            rollback_required=True,
            governance_required=True,
            external_evaluation_required=True,
        )
