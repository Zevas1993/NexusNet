from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from nexus.schemas import new_id


class ProductSweepPhaseGate(BaseModel):
    phase_id: str
    title: str
    status: str
    acceptance_tests: list[str] = Field(default_factory=list)
    operator_surfaces: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)


class ProductSweepGatekeeper:
    """Plan-level gate matrix for the NexusNet full product sweep."""

    def __init__(
        self,
        *,
        canon: Any,
        memory_os: Any,
        protocol_security: Any,
        runtime_profiles: Any,
        trace_evals: Any,
    ):
        self.canon = canon
        self.memory_os = memory_os
        self.protocol_security = protocol_security
        self.runtime_profiles = runtime_profiles
        self.trace_evals = trace_evals

    def phase_gates(self) -> list[ProductSweepPhaseGate]:
        return [
            ProductSweepPhaseGate(
                phase_id="phase-0",
                title="Baseline Rescue",
                status="implemented",
                acceptance_tests=["tests/test_model_registry.py", "python -m pytest --collect-only -q"],
                operator_surfaces=["/ops/models", "/status"],
                evidence=["nexus.models.ModelRegistry", "service construction regression coverage"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-1",
                title="Canon And Research Lock",
                status="implemented_living",
                acceptance_tests=["tests/test_full_product_sweep_scaffold.py", "tests/test_product_sweep_deepening.py"],
                operator_surfaces=["/ops/brain/canon", "/ops/brain/research-candidates"],
                evidence=["NexusNetCanonRegistry", "audited Assimilation Registry overlays"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-2",
                title="Core Schemas And Registries",
                status="implemented",
                acceptance_tests=["tests/test_full_product_sweep_scaffold.py"],
                operator_surfaces=["/ops/brain/canon"],
                evidence=["ExpertCapsule", "TeacherCapability", "RuntimeCandidate", "SecurityPolicy", "TraceEvent"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-3",
                title="Brain Path Unification",
                status="implemented_diagnostic",
                acceptance_tests=["tests/test_full_product_sweep_scaffold.py", "tests/test_nexusnet_core_pivot.py"],
                operator_surfaces=["/ops/brain/core", "/ops/brain/ebt/*"],
                evidence=["NexusBrain.generate product_trace", "EBTScoringContract"],
                blocked_by=["ebt_formula_weights_unresolved"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-4",
                title="Memory Operating System",
                status="implemented_persistent",
                acceptance_tests=["tests/test_product_sweep_operationalization.py", "tests/test_product_sweep_deepening.py"],
                operator_surfaces=["/ops/brain/memory-os/*"],
                evidence=["MemoryOperatingSystem persistence", "dereferenceable provenance"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-5",
                title="Secure Protocol Stack",
                status="implemented_gated",
                acceptance_tests=["tests/test_product_sweep_operationalization.py", "tests/test_product_sweep_deepening.py"],
                operator_surfaces=["/ops/brain/security/protocol/*"],
                evidence=["ProtocolSecurityLayer", "signed server registration", "accept/decline/cancel consent"],
                blocked_by=["external_protocols_disabled_until_policy_allows"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-6",
                title="Expert Hive, Council, And Critique",
                status="implemented_shadow",
                acceptance_tests=["tests/test_product_sweep_gatekeeper.py"],
                operator_surfaces=["/ops/brain/expert-council/deliberate"],
                evidence=["ExpertCouncil shadow deliberation", "NexusBrain remains decision authority"],
                blocked_by=["shadow_mode_until_eval_benefit_proven"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-7",
                title="Runtime, Hardware, And Long Context",
                status="implemented_candidate_profiles",
                acceptance_tests=["tests/test_product_sweep_deepening.py"],
                operator_surfaces=["/ops/brain/runtime/context-assembly", "/ops/runtimes"],
                evidence=["ProductRuntimeProfileRegistry", "effective context assembly"],
                blocked_by=["raw_million_token_context_unresolved", "runtime_health_required"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-8",
                title="Training And Assimilation",
                status="gated",
                acceptance_tests=["tests/test_product_sweep_operationalization.py", "tests/test_product_sweep_deepening.py"],
                operator_surfaces=["/ops/brain/training/export-record", "/ops/brain/training/export-dataset"],
                evidence=["TrainingDataExportRecord", "TrainingDatasetExporter artifacts"],
                blocked_by=["eval_report_required", "approved_license_required", "security_gate_pass_required"],
            ),
            ProductSweepPhaseGate(
                phase_id="phase-9",
                title="Product Surface And Docs",
                status="implemented_truthful_status",
                acceptance_tests=["tests/test_product_sweep_gatekeeper.py", "tests/test_product_sweep_operationalization.py"],
                operator_surfaces=["/ops/brain/product-status", "/ops/brain/product-sweep/status"],
                evidence=["NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md", "product sweep gate matrix"],
            ),
        ]

    def gate_payload(self) -> dict[str, Any]:
        gates = self.phase_gates()
        blocked = [gate for gate in gates if gate.blocked_by]
        return {
            "status": "active_gated_buildout",
            "phase_count": len(gates),
            "ready_for_real_training": False,
            "safe_to_promote_checkpoint": False,
            "blocked_phase_count": len(blocked),
            "phase_gates": [gate.model_dump(mode="json") for gate in gates],
        }

    def status_payload(self) -> dict[str, Any]:
        gate_payload = self.gate_payload()
        memory_summary = self.memory_os.summarize()
        eval_summary = self.trace_evals.summary()
        runtime_summary = self.runtime_profiles.summary()
        product_status = self.canon.product_status()
        return {
            "status": "active_gated_buildout",
            "product_status": product_status,
            "gate_summary": {
                "phase_count": gate_payload["phase_count"],
                "blocked_phase_count": gate_payload["blocked_phase_count"],
                "ready_for_real_training": gate_payload["ready_for_real_training"],
                "safe_to_promote_checkpoint": gate_payload["safe_to_promote_checkpoint"],
            },
            "status_surfaces": {
                "canon": {
                    "status": product_status["canon"]["status"],
                    "unresolved_count": product_status["canon"]["unresolved_count"],
                },
                "memory_os": {
                    "persistent": bool(memory_summary.get("persistence_path")),
                    "persistence_path": memory_summary.get("persistence_path"),
                    "fact_count": memory_summary.get("fact_count", 0),
                },
                "protocol_security": self.protocol_security.summary(),
                "runtime": {
                    "status": runtime_summary["status"],
                    "raw_million_token_context": runtime_summary["raw_million_token_context"],
                    "profile_count": len(runtime_summary["profiles"]),
                },
                "evals": {
                    "status": eval_summary["status"],
                    "scenario_count": eval_summary["scenario_count"],
                    "training_gate": eval_summary["training_gate"],
                },
            },
        }

    def shadow_simulation(self, *, name: str, target: str) -> dict[str, Any]:
        return {
            "simulation_id": new_id("sweep_shadow"),
            "name": name,
            "target": target,
            "status": "shadow_only",
            "can_mutate_memory": False,
            "can_mutate_models": False,
            "promotion_allowed": False,
            "decision_authority": "NexusBrain",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
