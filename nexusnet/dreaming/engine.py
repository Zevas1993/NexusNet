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
        compiled_knowledge_context = _compiled_knowledge_context(
            request.knowledge_artifact_refs,
            request.knowledge_artifact_runtime_contexts,
        )

        if compiled_knowledge_context["allowed"] is False:
            findings = ["kac_runtime_context_not_allowed", *compiled_knowledge_context["blocked_reasons"]]
            payload = self.shadow_pool.record_episode(
                seed=seed,
                scenario={
                    "source_trace_id": source_trace_id,
                    "model_hint": model_hint,
                    "variant_count": 0,
                    "compiled_knowledge_context": compiled_knowledge_context,
                },
                outcome={"variants": [], "aggregate_score": 0.0},
                critique={"findings": findings, "shadow_only": True, "blocked": True},
            )
            episode = DreamEpisode(
                dream_id=payload["dream_id"],
                seed=seed,
                source_trace_id=source_trace_id,
                status="rejected",
                variants=[],
                aggregate_score=0.0,
                findings=findings,
                knowledge_artifact_refs=request.knowledge_artifact_refs,
                compiled_knowledge_context=compiled_knowledge_context,
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
                    status="rejected",
                    lineage={
                        "source_trace_id": source_trace_id,
                        "seed": seed,
                        "knowledge_artifact_refs": request.knowledge_artifact_refs,
                        "compiled_knowledge_context": compiled_knowledge_context,
                    },
                    metrics={"aggregate_score": 0.0, "variant_count": 0},
                    artifacts=[payload.get("artifact_path")] if payload.get("artifact_path") else [],
                )
            )
            self.governance.record_event(
                "nexusnet.dream.rejected",
                {
                    "dream_id": episode.dream_id,
                    "source_trace_id": source_trace_id,
                    "aggregate_score": 0.0,
                    "status": "rejected",
                    "knowledge_artifact_refs": request.knowledge_artifact_refs,
                    "compiled_knowledge_context": compiled_knowledge_context,
                },
            )
            return episode

        variants: list[DreamVariant] = []
        for mode, prompt in self._build_variants(seed, request.variant_count):
            result = brain.generate(
                session_context=SessionContext(
                    session_id=f"dream::{source_trace_id or new_id('seed')}",
                    expert=expert,
                    task_type="dream",
                    use_retrieval=False,
                    metadata={
                        "dream_mode": mode,
                        "source_trace_id": source_trace_id,
                        "shadow_only": True,
                        "knowledge_artifact_refs": request.knowledge_artifact_refs,
                        "compiled_knowledge_context": compiled_knowledge_context,
                    },
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
                "compiled_knowledge_context": compiled_knowledge_context,
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
            knowledge_artifact_refs=request.knowledge_artifact_refs,
            compiled_knowledge_context=compiled_knowledge_context,
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
                lineage={
                    "source_trace_id": source_trace_id,
                    "seed": seed,
                    "knowledge_artifact_refs": request.knowledge_artifact_refs,
                    "compiled_knowledge_context": compiled_knowledge_context,
                },
                metrics={"aggregate_score": aggregate_score, "variant_count": len(variants)},
                artifacts=[payload.get("artifact_path")] if payload.get("artifact_path") else [],
            )
        )
        self.governance.record_event(
            "nexusnet.dream.recorded",
            {
                "dream_id": episode.dream_id,
                "source_trace_id": source_trace_id,
                "aggregate_score": aggregate_score,
                "status": "shadow",
                "knowledge_artifact_refs": request.knowledge_artifact_refs,
                "compiled_knowledge_context": compiled_knowledge_context,
            },
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


def _compiled_knowledge_context(
    artifact_refs: list[str],
    runtime_contexts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    runtime_gate = _knowledge_artifact_runtime_gate(runtime_contexts or [])
    return {
        "surface_id": "knowledge-artifact-compiler",
        "artifact_refs": artifact_refs,
        "access_rule": "artifact-refs-only-through-KRC",
        "mutation_allowed": False,
        "visibility": "recursive-dream-context" if artifact_refs else "none",
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "runtime_gate_source": "KnowledgeArtifactCompiler.query",
        "allowed": runtime_gate["allowed"],
        "runtime_context_evidence_count": runtime_gate["runtime_context_evidence_count"],
        "blocked_artifact_refs": runtime_gate["blocked_artifact_refs"],
        "blocked_reasons": runtime_gate["blocked_reasons"],
        "context_boundary": "compiled artifacts can seed dream scenarios only by explicit refs",
    }


def _knowledge_artifact_runtime_gate(runtime_contexts: list[dict[str, Any]]) -> dict[str, Any]:
    blocked_refs: list[str] = []
    blocked_reasons: list[str] = []
    for context in runtime_contexts:
        artifact_ref = str(context.get("artifact_id") or context.get("artifact_ref") or context.get("context") or "")
        fallback_state = str(context.get("fallback_state") or "")
        if context.get("runtime_context_allowed") is True and fallback_state == "compiled_artifact" and artifact_ref:
            continue
        if artifact_ref:
            blocked_refs.append(artifact_ref)
        reason = str(
            fallback_state
            or (context.get("quarantine_state") or {}).get("reason")
            or "krc_runtime_context_not_allowed"
        )
        blocked_reasons.append(reason)
    return {
        "allowed": not blocked_refs and not blocked_reasons,
        "runtime_context_evidence_count": len(runtime_contexts),
        "blocked_artifact_refs": sorted(set(blocked_refs)),
        "blocked_reasons": sorted(set(blocked_reasons)),
    }
