from __future__ import annotations

from statistics import mean
from typing import Any

from nexus.dreaming import DreamShadowPool
from nexus.experiments import ExperimentService
from nexus.governance import GovernanceService
from nexus.schemas import ExperimentRecord, new_id
from nexus.storage import NexusStore

from ..memory import NeuralMemoryCortex
from ..schemas import DreamCycleRequest, DreamEpisode, DreamVariant, SessionContext


class RecursiveDreamEngine:
    def __init__(
        self,
        *,
        store: NexusStore,
        shadow_pool: DreamShadowPool,
        memory: NeuralMemoryCortex,
        experiments: ExperimentService,
        governance: GovernanceService,
    ):
        self.store = store
        self.shadow_pool = shadow_pool
        self.memory = memory
        self.experiments = experiments
        self.governance = governance

    def run_cycle(self, *, brain, request: DreamCycleRequest) -> DreamEpisode:
        base_trace = self._select_trace(request.trace_id)
        seed = request.seed or self._seed_from_trace(base_trace) or "nexusnet recursive dreaming seed"
        source_trace_id = base_trace.get("trace_id") if base_trace else request.trace_id
        expert = (base_trace or {}).get("selected_expert") or "researcher"
        model_hint = request.model_hint or (base_trace or {}).get("model_id") or "mock/default"

        variants: list[DreamVariant] = []
        for mode, prompt in self._build_variants(seed, request.variant_count):
            result = brain.generate(
                session_context=SessionContext(
                    session_id=f"dream::{source_trace_id or new_id('seed')}",
                    expert=expert,
                    task_type="dream",
                    use_retrieval=False,
                    metadata={"dream_mode": mode, "source_trace_id": source_trace_id, "shadow_only": True},
                ),
                prompt=prompt,
                model_hint=model_hint,
            )
            scores = self._score_variant(result, mode)
            variants.append(
                DreamVariant(
                    mode=mode,
                    prompt=prompt,
                    output_preview=result.output[:240],
                    latency_ms=result.inference_trace.latency_ms,
                    critique_status=result.critique.status if result.critique else "ok",
                    scores=scores,
                )
            )

        aggregate_score = round(mean([mean(variant.scores.values()) for variant in variants]) if variants else 0.0, 3)
        findings = self._findings_from_variants(variants)
        payload = self.shadow_pool.record_episode(
            seed=seed,
            scenario={
                "source_trace_id": source_trace_id,
                "model_hint": model_hint,
                "variant_count": len(variants),
            },
            outcome={"variants": [variant.model_dump(mode="json") for variant in variants], "aggregate_score": aggregate_score},
            critique={"findings": findings, "shadow_only": True},
        )
        episode = DreamEpisode(
            dream_id=payload["dream_id"],
            seed=seed,
            source_trace_id=source_trace_id,
            status="shadow",
            variants=variants,
            aggregate_score=aggregate_score,
            findings=findings,
            artifact_path=payload.get("artifact_path"),
        )
        self.memory.record_dream_episode(
            subject=f"dream::{source_trace_id or payload['dream_id']}",
            detail=episode.model_dump(mode="json"),
        )
        self.experiments.record(
            ExperimentRecord(
                kind="dream_cycle",
                name=episode.dream_id,
                status="shadow",
                lineage={"source_trace_id": source_trace_id, "seed": seed},
                metrics={"aggregate_score": aggregate_score, "variant_count": len(variants)},
                artifacts=[payload.get("artifact_path")] if payload.get("artifact_path") else [],
            )
        )
        self.governance.record_event(
            "nexusnet.dream.recorded",
            {"dream_id": episode.dream_id, "source_trace_id": source_trace_id, "aggregate_score": aggregate_score, "status": "shadow"},
        )
        return episode

    def _select_trace(self, trace_id: str | None) -> dict[str, Any] | None:
        if trace_id:
            return self.store.get_trace(trace_id)
        warnings = self.store.list_traces(limit=1, status="warning")
        if warnings:
            return warnings[0]
        traces = self.store.list_traces(limit=1)
        return traces[0] if traces else None

    def _seed_from_trace(self, trace: dict[str, Any] | None) -> str | None:
        if not trace:
            return None
        request = trace.get("request", {})
        return request.get("prompt") or request.get("message")

    def _build_variants(self, seed: str, count: int) -> list[tuple[str, str]]:
        templates = [
            ("failure_replay", f"Failure replay: answer the original task more rigorously.\nTask: {seed}"),
            ("counterfactual", f"Counterfactual branch: if the first answer failed, what stronger evidence-backed response should replace it?\nTask: {seed}"),
            ("adversarial", f"Adversarial scenario: stress test the reasoning path and produce a more robust answer.\nTask: {seed}"),
            ("future_rehearsal", f"Future rehearsal: solve this task as if NexusNet were defending its answer before a review board.\nTask: {seed}"),
        ]
        return templates[: max(1, min(count, len(templates)))]

    def _score_variant(self, result, mode: str) -> dict[str, float]:
        critique = result.critique
        correctness = critique.critic_score if critique else 0.5
        robustness = 1.0 - (critique.hallucination_risk if critique else 0.5)
        efficiency = max(0.0, 1.0 - (result.inference_trace.latency_ms / 2000))
        coherence = min(1.0, len(result.output.strip()) / 160) if result.output.strip() else 0.0
        novelty = {"failure_replay": 0.45, "counterfactual": 0.7, "adversarial": 0.8, "future_rehearsal": 0.65}.get(mode, 0.5)
        return {
            "correctness": round(correctness, 3),
            "robustness": round(robustness, 3),
            "efficiency": round(efficiency, 3),
            "coherence": round(coherence, 3),
            "novelty": round(novelty, 3),
        }

    def _findings_from_variants(self, variants: list[DreamVariant]) -> list[str]:
        findings = []
        if any(variant.critique_status != "ok" for variant in variants):
            findings.append("Some dream variants still fail critique; keep outputs in shadow pool.")
        if any(variant.scores.get("robustness", 0.0) < 0.5 for variant in variants):
            findings.append("Robustness remains weak under adversarial or counterfactual rehearsal.")
        if any(variant.scores.get("efficiency", 0.0) < 0.7 for variant in variants):
            findings.append("Latency headroom should be improved before promotion.")
        if not findings:
            findings.append("Dream cycle produced shadow candidates suitable for benchmark review.")
        return findings
