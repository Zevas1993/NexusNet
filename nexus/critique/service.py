from __future__ import annotations

from ..schemas import CritiqueReport, OperatorRequest, RetrievalHit
from ..storage import NexusStore


class CritiqueEngine:
    def __init__(self, store: NexusStore):
        self.store = store

    def assess(self, *, trace_id: str, request: OperatorRequest, output: str, runtime_name: str, retrieval_hits: list[RetrievalHit]) -> CritiqueReport:
        issues = []
        groundedness = 0.7
        hallucination_risk = 0.2

        if not output.strip():
            issues.append("Empty output")
            groundedness = 0.0
            hallucination_risk = 1.0

        if request.use_retrieval and not retrieval_hits:
            issues.append("Retrieval requested but no supporting context was found")
            groundedness -= 0.3
            hallucination_risk += 0.3

        if runtime_name == "mock":
            issues.append("Response came from deterministic mock runtime")
            groundedness -= 0.2
            hallucination_risk += 0.1

        critic_score = max(0.0, min(1.0, groundedness - (hallucination_risk / 2)))
        status = "ok"
        if issues:
            status = "warning"
        if not output.strip():
            status = "error"

        report = CritiqueReport(
            trace_id=trace_id,
            status=status,
            critic_score=round(critic_score, 3),
            groundedness=round(max(0.0, groundedness), 3),
            hallucination_risk=round(min(1.0, hallucination_risk), 3),
            issues=issues,
            recommendations=self._recommendations(issues),
        )
        self.store.save_critique(report.critique_id, trace_id, report.model_dump(mode="json"), report.created_at.isoformat())
        return report

    def _recommendations(self, issues: list[str]) -> list[str]:
        recommendations = []
        for issue in issues:
            if "Retrieval requested" in issue:
                recommendations.append("Ingest relevant local documents or lower retrieval requirements for this session.")
            if "mock runtime" in issue:
                recommendations.append("Configure a live local runtime such as Ollama or llama.cpp before production use.")
            if "Empty output" in issue:
                recommendations.append("Inspect runtime health and fallback policy for this model path.")
        return recommendations

