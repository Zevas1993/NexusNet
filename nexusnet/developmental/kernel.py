from __future__ import annotations

from pathlib import Path
from typing import Any

from .body_schema import NexusBodySchemaBuilder
from .causal_lab import CausalInterventionLab
from .contracts import DevelopmentalCortexResult
from .growth_archive import GrowthArchive
from .promotion_tribunal import PromotionTribunal
from .reference_frames import ReferenceFrameStore
from .simulator import DreamingSimulator


class DevelopmentalCortexKernel:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.body_schema = NexusBodySchemaBuilder()
        self.reference_frames = ReferenceFrameStore(artifacts_dir=artifacts_dir)
        self.simulator = DreamingSimulator(artifacts_dir=artifacts_dir)
        self.causal_lab = CausalInterventionLab(artifacts_dir=artifacts_dir)
        self.growth_archive = GrowthArchive(artifacts_dir=artifacts_dir)
        self.promotion_tribunal = PromotionTribunal()

    def assess(
        self,
        *,
        request_id: str,
        task_ref: str,
        trace_refs: list[str],
        evidence_refs: list[str],
        runtime_state: dict[str, Any],
        memory_state: dict[str, Any],
        authority_state: dict[str, Any],
        eval_state: dict[str, Any],
    ) -> dict[str, Any]:
        stable_id = request_id.replace(":", "_")
        body_schema_snapshot = self.body_schema.snapshot(
            runtime_state=runtime_state,
            memory_state=memory_state,
            authority_state=authority_state,
            eval_state=eval_state,
        )
        body_schema_blocked = _body_schema_blocked(body_schema_snapshot)
        reference_frame = self.reference_frames.record(
            frame_id=f"frame:task:{stable_id}",
            frame_type="task",
            subject_ref=task_ref,
            facts=[
                {
                    "claim": "Developmental cortex assessment is shadow-only and evidence-gated.",
                    "source_ref": "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
                }
            ],
            evidence_refs=evidence_refs,
            uncertainty=0.15,
        )
        simulation = self.simulator.record_simulation(
            simulation_id=f"sim:{stable_id}",
            seed_trace_ref=trace_refs[0] if trace_refs else task_ref,
            scenario={"task_ref": task_ref, "trace_refs": trace_refs},
            expected_outcomes=["promotion_case_created", "growth_candidate_archived"],
            evidence_refs=evidence_refs,
        )
        causal_intervention = self.causal_lab.record_intervention(
            intervention_id=f"causal:{stable_id}",
            variable="evidence_gate",
            control_value="all_sources",
            treatment_value="trusted_sources_only",
            observed_delta={"reviewability": 0.1 if evidence_refs else 0.0},
            evidence_refs=evidence_refs,
        )
        growth_candidate = self.growth_archive.record_candidate(
            candidate_id=f"growth:{stable_id}",
            candidate_type="research",
            diversity_key="developmental-cortex",
            scores={"quality": 0.7, "safety": 0.95},
            evidence_refs=evidence_refs,
        )
        promotion_case = self.promotion_tribunal.decide(
            case_id=f"case:{stable_id}",
            candidate_ref=growth_candidate["candidate_id"],
            requested_state="shadow",
            policy_scan={"summary": {"active_hard_fail_count": 0}},
            eval_gate={"promotion_allowed": bool(evidence_refs) and not body_schema_blocked},
            artifact_trust={"promotion_allowed": bool(evidence_refs) and not body_schema_blocked},
            self_review={"status": "accepted-shadow"},
            memory_quality={"status": "verified"},
            rollback={"rollback_restorable": True},
            operator_approved=False,
        )
        status = "blocked" if _has_blocker(
            body_schema_snapshot=body_schema_snapshot,
            reference_frame=reference_frame,
            simulation=simulation,
            causal_intervention=causal_intervention,
            growth_candidate=growth_candidate,
            promotion_case=promotion_case,
        ) else "shadow-ready"
        return DevelopmentalCortexResult(
            request_id=request_id,
            task_ref=task_ref,
            status=status,
            body_schema_snapshot=body_schema_snapshot,
            reference_frame=reference_frame,
            simulation=simulation,
            causal_intervention=causal_intervention,
            growth_candidate=growth_candidate,
            promotion_case=promotion_case,
            production_mutation_allowed=False,
        ).model_dump(mode="json")


def _has_blocker(
    *,
    body_schema_snapshot: dict[str, Any],
    reference_frame: dict[str, Any],
    simulation: dict[str, Any],
    causal_intervention: dict[str, Any],
    growth_candidate: dict[str, Any],
    promotion_case: dict[str, Any],
) -> bool:
    return (
        _body_schema_blocked(body_schema_snapshot)
        or reference_frame.get("runtime_state") == "degraded"
        or simulation.get("status") == "blocked"
        or causal_intervention.get("status") == "blocked"
        or growth_candidate.get("promotion_state") == "blocked"
        or promotion_case.get("decision") == "rejected"
    )


def _body_schema_blocked(body_schema_snapshot: dict[str, Any]) -> bool:
    return body_schema_snapshot.get("runtime_state") == "degraded" or bool(
        body_schema_snapshot.get("blocked_surfaces")
    )
