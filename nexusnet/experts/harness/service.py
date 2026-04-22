from __future__ import annotations

from itertools import combinations
from typing import Any

from ...moe.adapter_registry import AdapterRegistry


class InternalExpertHarnessService:
    def __init__(self, *, registry: AdapterRegistry | None = None):
        self.registry = registry or AdapterRegistry()

    def preview(
        self,
        *,
        native_execution_plan: dict[str, Any],
        selected_expert: str | None,
    ) -> dict[str, Any]:
        contracts = self._contracts(
            selected_expert=selected_expert,
            expert_ids=native_execution_plan.get("selected_internal_experts", []),
        )
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "execution_id": native_execution_plan.get("execution_id"),
            "enabled": native_execution_plan.get("enabled", False),
            "execution_mode": native_execution_plan.get("execution_mode"),
            "legacy_execution_mode": native_execution_plan.get("legacy_execution_mode"),
            "selected_internal_experts": native_execution_plan.get("selected_internal_experts", []),
            "primary_expert_id": native_execution_plan.get("primary_expert_id"),
            "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
            "fallback_triggers": native_execution_plan.get("fallback_triggers", []),
            "challenger_compare_required": native_execution_plan.get("challenger_compare_required", False),
            "guarded_live_enabled": native_execution_plan.get("guarded_live_enabled", False),
            "live_guidance_enabled": native_execution_plan.get("live_guidance_enabled", False),
            "contracts": contracts,
            "enabled_contract_count": sum(1 for item in contracts if item["capability_gate"]["enabled"]),
            "preview_only": True,
        }

    def execute(
        self,
        *,
        prompt: str,
        selected_expert: str | None,
        native_execution_plan: dict[str, Any],
        execution_policy: dict[str, Any],
        evidence_feeds: dict[str, Any],
    ) -> dict[str, Any]:
        preview = self.preview(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
        )
        execution_mode = native_execution_plan.get("execution_mode")
        alignment_hold_required = bool(native_execution_plan.get("alignment_hold_required"))
        alignment_blockers = list(native_execution_plan.get("alignment_blockers") or [])
        outputs = []
        for contract in preview["contracts"]:
            if not contract["capability_gate"]["enabled"]:
                continue
            outputs.append(
                {
                    "output_id": f"{native_execution_plan.get('execution_id')}::{contract['expert_id']}",
                    "expert_id": contract["expert_id"],
                    "family": contract["family"],
                    "stance": contract["stance"],
                    "execution_role": "challenger"
                    if execution_mode in {"native_challenger_shadow", "native_live_guarded"}
                    else "planner",
                    "confidence": contract["capability_gate"]["confidence"],
                    "teacher_anchor_bundle_id": ((evidence_feeds.get("teacher_evidence") or {}).get("latest_bundle_id")),
                    "candidate_id": ((evidence_feeds.get("foundry") or {}).get("latest_native_takeover_candidate_id")),
                    "active_planes": native_execution_plan.get("memory_planes", []),
                    "summary": self._bounded_summary(
                        expert_id=contract["expert_id"],
                        stance=contract["stance"],
                        prompt=prompt,
                        evidence_feeds=evidence_feeds,
                    ),
                }
            )
        disagreements = self._disagreements(outputs)
        policy_fallback_triggers = list(native_execution_plan.get("fallback_triggers") or [])
        runtime_fallback_triggers: list[str] = []
        teacher_bundle_id = ((evidence_feeds.get("teacher_evidence") or {}).get("latest_bundle_id")) or "no-teacher-bundle"
        teacher_anchor_present = teacher_bundle_id != "no-teacher-bundle"
        if execution_mode == "native_live_guarded":
            if not teacher_anchor_present:
                runtime_fallback_triggers.append("teacher_anchor_missing")
            if alignment_hold_required:
                runtime_fallback_triggers.append("alignment_hold_runtime")
            if disagreements:
                runtime_fallback_triggers.append("guarded_live_disagreement")
            if any(float(item.get("confidence", 0.0)) < 0.78 for item in outputs):
                runtime_fallback_triggers.append("guarded_live_confidence_low")
        elif execution_mode == "native_challenger_shadow" and not outputs:
            runtime_fallback_triggers.append("challenger_outputs_unavailable")
        elif execution_mode == "native_planner_live" and alignment_hold_required:
            runtime_fallback_triggers.append("alignment_hold_runtime")
        fallback_triggers = list(dict.fromkeys(policy_fallback_triggers + runtime_fallback_triggers))
        fallback_triggers = list(dict.fromkeys(fallback_triggers))
        guarded_live_allowed = execution_mode == "native_live_guarded" and not runtime_fallback_triggers and teacher_anchor_present
        fallback_triggered = bool(runtime_fallback_triggers)
        challenger_vs_teacher = {
            "required": bool(native_execution_plan.get("challenger_compare_required")),
            "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
            "teacher_anchor_present": teacher_anchor_present,
            "teacher_bundle_id": teacher_bundle_id,
            "challenger_output_count": len(outputs),
            "disagreement_count": len(disagreements),
            "fallback_triggered": fallback_triggered,
        }
        teacher_comparison = self._teacher_comparison(
            execution_mode=execution_mode,
            outputs=outputs,
            disagreements=disagreements,
            teacher_anchor_present=teacher_anchor_present,
            teacher_bundle_id=teacher_bundle_id,
            guarded_live_allowed=guarded_live_allowed,
            alignment_hold_required=alignment_hold_required,
            alignment_blockers=alignment_blockers,
        )
        native_candidate = self._native_candidate(
            native_execution_plan=native_execution_plan,
            outputs=outputs,
            disagreements=disagreements,
            teacher_comparison=teacher_comparison,
            fallback_triggered=fallback_triggered,
            alignment_hold_required=alignment_hold_required,
            alignment_blockers=alignment_blockers,
        )
        prompt_guidance = [
            f"{item['expert_id']} ({item['stance']}, confidence={item['confidence']}) => {item['summary']}"
            for item in outputs[:3]
        ]
        if disagreements:
            prompt_guidance.append(f"Disagreement capture: {disagreements[0]['summary']}")
        prompt_guidance.append(f"Teacher comparison: {teacher_comparison['summary']}")
        if native_candidate.get("activation_allowed"):
            prompt_guidance.append(
                f"Native candidate {native_candidate['candidate_id']} is active in {native_candidate['activation_mode']} mode."
            )
        if guarded_live_allowed:
            prompt_guidance.append("Guarded live remains bounded: verify challenger outputs against the teacher-attached path before finalization.")
        elif alignment_hold_required:
            prompt_guidance.append(
                f"Alignment hold remains active: {', '.join(alignment_blockers or ['alignment work pending'])}."
            )
        elif fallback_triggers:
            prompt_guidance.append(f"Teacher fallback trigger(s): {', '.join(fallback_triggers)}")
        return {
            **preview,
            "preview_only": False,
            "outputs": outputs,
            "output_count": len(outputs),
            "disagreements": disagreements,
            "disagreement_count": len(disagreements),
            "prompt_guidance": prompt_guidance,
            "execution_policy_ref": execution_policy.get("policy_id"),
            "evidence_refs": execution_policy.get("evidence_refs", {}),
            "challenger_vs_teacher": challenger_vs_teacher,
            "teacher_comparison": teacher_comparison,
            "native_candidate": native_candidate,
            "native_response_outline": self._native_response_outline(
                outputs=outputs,
                teacher_comparison=teacher_comparison,
                native_candidate=native_candidate,
            ),
            "guarded_live_allowed": guarded_live_allowed,
            "fallback_triggered": fallback_triggered,
            "policy_fallback_triggers": policy_fallback_triggers,
            "runtime_fallback_triggers": runtime_fallback_triggers,
            "fallback_triggers": fallback_triggers,
            "alignment_hold_required": alignment_hold_required,
            "alignment_blockers": alignment_blockers,
            "recommended_execution_mode": teacher_comparison["recommended_execution_mode"],
            "fallback_recommendation": native_execution_plan.get("teacher_fallback_path"),
        }

    def _contracts(self, *, selected_expert: str | None, expert_ids: list[str]) -> list[dict[str, Any]]:
        contracts = []
        normalized_expert = (selected_expert or "general").lower()
        for expert_id in expert_ids:
            spec = self.registry.resolve(expert_id)
            confidence = self._capability_confidence(expert_id=expert_id, selected_expert=normalized_expert)
            stance = self._stance(expert_id)
            contracts.append(
                {
                    "expert_id": expert_id,
                    "family": spec.get("family"),
                    "role_tags": spec.get("role_tags", []),
                    "stance": stance,
                    "capability_gate": {
                        "enabled": confidence >= 0.6,
                        "confidence": confidence,
                        "selected_expert": selected_expert,
                    },
                }
            )
        return contracts

    def _capability_confidence(self, *, expert_id: str, selected_expert: str) -> float:
        normalized = expert_id.lower()
        if selected_expert in {"coder", "coding"}:
            return 0.95 if ("devstral" in normalized or "coder" in normalized) else 0.72
        if selected_expert in {"researcher", "research"}:
            return 0.95 if "research" in normalized else 0.74
        if "general" in normalized:
            return 0.82
        return 0.68

    def _stance(self, expert_id: str) -> str:
        normalized = expert_id.lower()
        if "devstral" in normalized:
            return "implementation-first"
        if "research" in normalized:
            return "evidence-first"
        return "synthesis-first"

    def _bounded_summary(
        self,
        *,
        expert_id: str,
        stance: str,
        prompt: str,
        evidence_feeds: dict[str, Any],
    ) -> str:
        teacher_bundle_id = ((evidence_feeds.get("teacher_evidence") or {}).get("latest_bundle_id")) or "no-teacher-bundle"
        candidate_id = ((evidence_feeds.get("foundry") or {}).get("latest_native_takeover_candidate_id")) or "no-takeover-candidate"
        subject = prompt.strip().replace("\n", " ")[:88]
        return (
            f"Use {stance} reasoning for '{subject}', anchor on teacher bundle {teacher_bundle_id}, "
            f"and keep takeover ref {candidate_id} bounded behind teacher fallback."
        )

    def _disagreements(self, outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        disagreements = []
        for left, right in combinations(outputs, 2):
            if left["stance"] == right["stance"]:
                continue
            disagreements.append(
                {
                    "left_expert_id": left["expert_id"],
                    "right_expert_id": right["expert_id"],
                    "summary": f"{left['expert_id']} prefers {left['stance']} while {right['expert_id']} prefers {right['stance']}.",
                }
            )
        return disagreements

    def _teacher_comparison(
        self,
        *,
        execution_mode: str | None,
        outputs: list[dict[str, Any]],
        disagreements: list[dict[str, Any]],
        teacher_anchor_present: bool,
        teacher_bundle_id: str,
        guarded_live_allowed: bool,
        alignment_hold_required: bool,
        alignment_blockers: list[str],
    ) -> dict[str, Any]:
        if not teacher_anchor_present:
            return {
                "verdict": "teacher-anchor-required",
                "summary": f"Teacher anchor {teacher_bundle_id} is missing, so native execution must fall back to the teacher path.",
                "recommended_execution_mode": "teacher_fallback",
            }
        if alignment_hold_required and execution_mode in {"native_challenger_shadow", "native_planner_live", "native_live_guarded"}:
            return {
                "verdict": "alignment-hold",
                "summary": f"Alignment hold restricts execution to bounded shadow behavior until {', '.join(alignment_blockers or ['alignment work'])} is resolved.",
                "recommended_execution_mode": "native_shadow" if outputs else "teacher_fallback",
            }
        if execution_mode == "native_live_guarded":
            if guarded_live_allowed:
                return {
                    "verdict": "guarded-live-supported",
                    "summary": f"Teacher bundle {teacher_bundle_id} remains present and challenger outputs stay bounded enough for guarded live verification.",
                    "recommended_execution_mode": "native_live_guarded",
                }
            return {
                "verdict": "guarded-live-blocked",
                "summary": f"Teacher bundle {teacher_bundle_id} remains primary because guarded live checks detected disagreement or low-confidence challenger output.",
                "recommended_execution_mode": "teacher_fallback",
            }
        if execution_mode == "native_challenger_shadow":
            return {
                "verdict": "challenger-shadow-compare",
                "summary": f"Challenger shadow execution is bounded against teacher bundle {teacher_bundle_id} with {len(disagreements)} disagreement artifact(s).",
                "recommended_execution_mode": "native_challenger_shadow" if outputs else "teacher_fallback",
            }
        if execution_mode == "native_planner_live":
            return {
                "verdict": "planner-live-guidance",
                "summary": f"Live planner guidance remains bounded behind teacher bundle {teacher_bundle_id}.",
                "recommended_execution_mode": "native_planner_live" if outputs else "teacher_fallback",
            }
        if execution_mode == "native_shadow":
            return {
                "verdict": "shadow-advisory",
                "summary": f"Native shadow outputs remain advisory while teacher bundle {teacher_bundle_id} stays authoritative.",
                "recommended_execution_mode": "native_shadow" if outputs else "teacher_fallback",
            }
        return {
            "verdict": "teacher-fallback",
            "summary": f"Teacher bundle {teacher_bundle_id} remains the primary execution path.",
            "recommended_execution_mode": "teacher_fallback",
        }

    def _native_candidate(
        self,
        *,
        native_execution_plan: dict[str, Any],
        outputs: list[dict[str, Any]],
        disagreements: list[dict[str, Any]],
        teacher_comparison: dict[str, Any],
        fallback_triggered: bool,
        alignment_hold_required: bool,
        alignment_blockers: list[str],
    ) -> dict[str, Any]:
        execution_id = native_execution_plan.get("execution_id")
        execution_mode = native_execution_plan.get("execution_mode")
        if not outputs:
            return {
                "candidate_id": f"{execution_id}::candidate",
                "activation_mode": "teacher-fallback-only",
                "activation_allowed": False,
                "teacher_verification_required": True,
                "confidence": 0.0,
                "content": teacher_comparison["summary"],
                "blocked_reason": "no-native-outputs",
                "source_expert_ids": [],
            }

        confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    (sum(float(item.get("confidence", 0.0)) for item in outputs) / len(outputs))
                    - (0.05 * len(disagreements)),
                ),
            ),
            3,
        )
        activation_mode = {
            "native_shadow": "shadow-advisory-draft",
            "native_challenger_shadow": "challenger-shadow-draft",
            "native_planner_live": "planner-live-draft",
            "native_live_guarded": "guarded-live-draft",
        }.get(execution_mode, "teacher-fallback-only")
        activation_allowed = (
            execution_mode in {"native_shadow", "native_challenger_shadow", "native_planner_live", "native_live_guarded"}
            and not fallback_triggered
            and not (alignment_hold_required and execution_mode in {"native_planner_live", "native_live_guarded"})
        )
        blocked_reason = None
        if not activation_allowed:
            if alignment_hold_required:
                blocked_reason = "alignment-hold-active"
            elif fallback_triggered:
                blocked_reason = "runtime-fallback-triggered"
            else:
                blocked_reason = "teacher-fallback-required"
        synthesis = "; ".join(item["summary"] for item in outputs[:2])
        content = (
            f"Teacher-verifiable native draft: {synthesis}. "
            f"Teacher comparison verdict: {teacher_comparison['verdict']}."
        )
        if alignment_hold_required:
            content += f" Alignment blockers: {', '.join(alignment_blockers or ['alignment work pending'])}."
        return {
            "candidate_id": f"{execution_id}::candidate",
            "activation_mode": activation_mode,
            "activation_allowed": activation_allowed,
            "teacher_verification_required": True,
            "confidence": confidence,
            "content": content,
            "blocked_reason": blocked_reason,
            "source_expert_ids": [item["expert_id"] for item in outputs],
        }

    def _native_response_outline(
        self,
        *,
        outputs: list[dict[str, Any]],
        teacher_comparison: dict[str, Any],
        native_candidate: dict[str, Any],
    ) -> str:
        if native_candidate.get("content"):
            return native_candidate["content"]
        if not outputs:
            return teacher_comparison["summary"]
        previews = "; ".join(item["summary"] for item in outputs[:2])
        return f"{teacher_comparison['summary']} Native bounded output preview: {previews}"
