__all__ = ["PromotionService", "PromotionTrendGate", "PromotionCohortGate", "TeacherEvidenceService"]


def __getattr__(name):
    if name == "PromotionService":
        from .service import PromotionService

        return PromotionService
    if name == "PromotionTrendGate":
        from .trend_gating import PromotionTrendGate

        return PromotionTrendGate
    if name == "PromotionCohortGate":
        from .cohort_gating import PromotionCohortGate

        return PromotionCohortGate
    if name == "TeacherEvidenceService":
        from .teacher_evidence import TeacherEvidenceService

        return TeacherEvidenceService
    raise AttributeError(name)
