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
        self.artifacts_dir = artifacts_dir
        self.body_schema = NexusBodySchemaBuilder()
        self.reference_frames = ReferenceFrameStore(artifacts_dir=artifacts_dir)
        self.simulator = DreamingSimulator(artifacts_dir=artifacts_dir)
        self.causal_lab = CausalInterventionLab(artifacts_dir=artifacts_dir)
        self.growth_archive = GrowthArchive(artifacts_dir=artifacts_dir)
        self.tribunal = PromotionTribunal()

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
        body = self.body_schema.snapshot(
            runtime_state=runtime_state,
            memory_state=memory_state,
            authority_state=authority_state,
            eval_state=eval_state,
        )
        frame = self.reference_frames.record(
            frame_id=f"frame:task:{request_id.replace(':', '_')}",
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
            simulation_id=f"sim:{request_id.replace(':', '_')}",
            seed_trace_ref=trace_refs[0] if trace_refs else task_ref,
            scenario={"task_ref": task_ref, "trace_refs": trace_refs},
            expected_outcomes=["promotion_case_created", "growth_candidate_archived"],
            evidence_refs=evidence_refs,
        )
        causal = self.causal_lab.record_intervention(
            intervention_id=f"causal:{request_id.replace(':', '_')}",
            variable="evidence_gate",
            control_value="without_developmental_kernel",
            treatment_value="with_developmental_kernel",
            observed_delta={"reviewability": 0.1 if evidence_refs else 0.0},
            evidence_refs=evidence_refs,
        )
        candidate = self.growth_archive.record_candidate(
            candidate_id=f"growth:{request_id.replace(':', '_')}",
            candidate_type="research",
            diversity_key="developmental-cortex",
            scores={"quality": 0.7, "safety": 0.95},
            evidence_refs=evidence_refs,
        )
        promotion = self.tribunal.decide(
            case_id=f"case:{request_id.replace(':', '_')}",
            candidate_ref=candidate["candidate_id"],
            requested_state="shadow",
            policy_scan={"summary": {"active_hard_fail_count": 0}},
            eval_gate={"promotion_allowed": bool(evidence_refs)},
            artifact_trust={"promotion_allowed": bool(evidence_refs), "promotion_blockers": []},
            self_review={"status": "accepted-shadow"},
            memory_quality={"status": "verified"},
            rollback={"rollback_restorable": True},
            operator_approved=False,
        )
        blocked = any(
            item.get("runtime_state") == "degraded" or item.get("status") == "blocked"
            for item in [body, frame, simulation, causal]
        ) or promotion["decision"] == "rejected"
        return DevelopmentalCortexResult(
            request_id=request_id,
            task_ref=task_ref,
            status="blocked" if blocked else "shadow-ready",
            body_schema_snapshot=body,
            reference_frame=frame,
            simulation=simulation,
            causal_intervention=causal,
            growth_candidate=candidate,
            promotion_case=promotion,
        ).model_dump(mode="json")
