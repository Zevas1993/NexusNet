from __future__ import annotations

from collections import Counter
from statistics import mean

from nexus.storage import NexusStore

from ..schemas import ReflectionFinding, ReflectionReport


class MetaReflectionEngine:
    def __init__(self, *, store: NexusStore):
        self.store = store

    def summarize(self, *, limit: int = 25) -> ReflectionReport:
        traces = self.store.list_traces(limit=limit)
        critiques = self.store.list_critiques(limit=limit)
        findings: list[ReflectionFinding] = []
        issue_counter: Counter[str] = Counter()
        latencies: list[int] = []
        mock_count = 0

        for trace in traces:
            runtime_name = trace.get("runtime_name")
            latency = int(trace.get("metrics", {}).get("brain_latency_ms", 0) or 0)
            latencies.append(latency)
            if runtime_name == "mock":
                mock_count += 1
                findings.append(
                    ReflectionFinding(
                        category="runtime",
                        severity="warning",
                        detail="Mock runtime is still serving requests; attach a stronger live teacher for real evaluations.",
                        trace_id=trace.get("trace_id"),
                    )
                )
            if latency > 1200:
                findings.append(
                    ReflectionFinding(
                        category="latency",
                        severity="warning",
                        detail=f"Trace latency reached {latency}ms, which should enter runtime optimization review.",
                        trace_id=trace.get("trace_id"),
                    )
                )
            if trace.get("metrics", {}).get("retrieval_hits", 0) == 0 and trace.get("request", {}).get("use_retrieval"):
                findings.append(
                    ReflectionFinding(
                        category="retrieval",
                        severity="warning",
                        detail="Retrieval was requested but no support hits were found.",
                        trace_id=trace.get("trace_id"),
                    )
                )

        for critique in critiques:
            for issue in critique.get("issues", []):
                issue_counter[issue] += 1
                category = self._categorize_issue(issue)
                severity = "critical" if "Empty output" in issue else "warning"
                findings.append(
                    ReflectionFinding(
                        category=category,
                        severity=severity,
                        detail=issue,
                        trace_id=critique.get("trace_id"),
                        critique_id=critique.get("critique_id"),
                    )
                )

        metrics = {
            "trace_count": len(traces),
            "critique_count": len(critiques),
            "avg_latency_ms": round(mean(latencies), 3) if latencies else 0.0,
            "mock_trace_rate": round(mock_count / max(len(traces), 1), 3),
            "top_issues": issue_counter.most_common(5),
        }
        recommendations = self._recommendations(metrics, issue_counter)
        return ReflectionReport(scope=f"recent:{limit}", findings=findings[:50], metrics=metrics, recommendations=recommendations)

    def _categorize_issue(self, issue: str) -> str:
        low = issue.lower()
        if "retrieval" in low:
            return "retrieval"
        if "mock runtime" in low:
            return "runtime"
        if "empty output" in low:
            return "hallucination"
        return "benchmark"

    def _recommendations(self, metrics: dict, issue_counter: Counter[str]) -> list[str]:
        recommendations = []
        if metrics.get("mock_trace_rate", 0.0) > 0.25:
            recommendations.append("Prioritize attaching stronger live teacher models before trusting benchmark movement.")
        if any("Retrieval requested" in issue for issue in issue_counter):
            recommendations.append("Add retrieval-focused curriculum and ingest more local corpora before enabling retrieval-heavy prompts by default.")
        if metrics.get("avg_latency_ms", 0.0) > 900:
            recommendations.append("Feed recent traces into the runtime profiler and quantization search loop.")
        if not recommendations:
            recommendations.append("Current traces are stable enough to enter dream and curriculum expansion with shadow-only promotion.")
        return recommendations
