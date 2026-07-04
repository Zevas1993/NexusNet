from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import OperatorRequest, utcnow

from ..schemas import AOPlan, AORegistrySnapshot


@dataclass
class AssistantOrchestrator:
    name: str
    description: str
    responsibilities: list[str]
    status_label: str = "LOCKED CANON"
    risk_tier: str = "medium"
    keywords: list[str] = field(default_factory=list)

    def score(self, text: str) -> int:
        lowered = text.lower()
        return sum(1 for keyword in self.keywords if keyword in lowered)

    def plan(self, *, request: OperatorRequest, expert: str | None, wrapper_mode: str | None) -> AOPlan:
        reason = f"{self.name} selected via heuristic routing."
        if wrapper_mode and wrapper_mode != "standard-chat":
            reason += f" Wrapper mode '{wrapper_mode}' remained inside the AO envelope."
        if expert:
            reason += f" Expert hint '{expert}' informed routing."
        return AOPlan(
            ao_name=self.name,
            status_label=self.status_label,
            reason=reason,
            risk_tier=self.risk_tier,
            goals=request.success_conditions or ["respond coherently", "preserve traceability", "update learning substrate"],
            responsibilities=self.responsibilities,
        )


class AssistantOrchestratorRegistry:
    def __init__(self, orchestrators: list[AssistantOrchestrator], *, artifacts_dir: Path | None = None):
        self._orchestrators = {orchestrator.name: orchestrator for orchestrator in orchestrators}
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.execution_receipts_dir = (
            self.artifacts_dir / "aos" / "execution-receipts" if self.artifacts_dir is not None else None
        )
        if self.execution_receipts_dir is not None:
            self.execution_receipts_dir.mkdir(parents=True, exist_ok=True)
        self._execution_receipts: list[dict[str, Any]] = self._load_execution_receipts()
        self._replay_status = {
            "status": "replayed" if self._execution_receipts else "no-persisted-receipts",
            "receipt_count": len(self._execution_receipts),
            "artifact_dir": str(self.execution_receipts_dir) if self.execution_receipts_dir is not None else "",
        }

    def get(self, name: str) -> AssistantOrchestrator | None:
        return self._orchestrators.get(name)

    def list(self) -> list[AssistantOrchestrator]:
        return list(self._orchestrators.values())

    def snapshot(self) -> AORegistrySnapshot:
        receipts = list(self._execution_receipts)
        latest_execution = next(
            (
                receipt
                for receipt in receipts
                if not str(receipt.get("wrapper_mode") or "").startswith("canonical-ao-coverage::")
            ),
            receipts[0] if receipts else None,
        )
        return AORegistrySnapshot(
            active_aos=[
                {
                    "name": orchestrator.name,
                    "description": orchestrator.description,
                    "status_label": orchestrator.status_label,
                    "risk_tier": orchestrator.risk_tier,
                    "responsibilities": orchestrator.responsibilities,
                    "execution_count": sum(1 for receipt in receipts if receipt.get("ao_name") == orchestrator.name),
                    "latest_trace_ref": next(
                        (
                            receipt.get("trace_ref")
                            for receipt in receipts
                            if receipt.get("ao_name") == orchestrator.name
                        ),
                        None,
                    ),
                }
                for orchestrator in self.list()
            ],
            execution_count=len(receipts),
            latest_execution=latest_execution,
            execution_receipts=receipts,
            replay=dict(self._replay_status),
        )

    def select_request(self, request: OperatorRequest, *, expert: str | None = None, wrapper_mode: str | None = None) -> AOPlan:
        explicit = request.metadata.get("ao")
        if explicit and explicit in self._orchestrators:
            return self._orchestrators[explicit].plan(request=request, expert=expert, wrapper_mode=wrapper_mode)

        text = " ".join(
            part
            for part in [
                request.prompt or "",
                " ".join(message.content for message in request.messages),
                expert or "",
                wrapper_mode or "",
            ]
            if part
        ).strip()
        if not text:
            return self._orchestrators["PlanningAO"].plan(request=request, expert=expert, wrapper_mode=wrapper_mode)

        ranked = sorted(
            self.list(),
            key=lambda orchestrator: (orchestrator.score(text), orchestrator.name == "PlanningAO"),
            reverse=True,
        )
        selected = ranked[0] if ranked and ranked[0].score(text) > 0 else self._orchestrators["PlanningAO"]
        return selected.plan(request=request, expert=expert, wrapper_mode=wrapper_mode)

    def record_execution(
        self,
        *,
        session_id: str,
        trace_id: str,
        plan: AOPlan,
        selected_expert: str | None,
        selected_teacher_id: str | None,
        wrapper_mode: str | None,
        session_ref_digest: str | None = None,
    ) -> dict[str, Any]:
        receipt = {
            "surface_id": "ao-execution-receipt",
            "execution_id": f"aoexec::{_safe_ref(trace_id)}",
            "ao_name": plan.ao_name,
            "trace_ref": f"trace::{trace_id}",
            "session_ref_digest": session_ref_digest or _privacy_digest(session_id),
            "selected_expert": selected_expert,
            "selected_teacher_ref": f"teacher::{selected_teacher_id}" if selected_teacher_id else None,
            "wrapper_mode": wrapper_mode or "standard-chat",
            "input_contract": "nexusbrain-command-envelope-and-trace-only",
            "consumed_refs": [f"trace::{trace_id}", f"ao-plan::{plan.ao_name}"],
            "direct_local_state_reads": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "plan": plan.model_dump(mode="json"),
            "created_at": utcnow().isoformat(),
        }
        self._persist_execution_receipt(receipt)
        self._execution_receipts.insert(0, receipt)
        self._execution_receipts = self._execution_receipts[:100]
        return receipt

    def _persist_execution_receipt(self, receipt: dict[str, Any]) -> None:
        if self.execution_receipts_dir is None:
            return
        path = self.execution_receipts_dir / f"{_safe_ref(str(receipt['execution_id']))}.json"
        receipt["artifact_path"] = str(path)
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")

    def _load_execution_receipts(self) -> list[dict[str, Any]]:
        if self.execution_receipts_dir is None:
            return []
        receipts: list[dict[str, Any]] = []
        for path in self.execution_receipts_dir.glob("*.json"):
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not _is_replayable_receipt(receipt):
                continue
            receipt["artifact_path"] = str(path)
            receipts.append(receipt)
        receipts.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return receipts[:100]


def build_default_ao_registry(*, artifacts_dir: Path | None = None) -> AssistantOrchestratorRegistry:
    orchestrators = [
        AssistantOrchestrator(
            name="PlanningAO",
            description="Default executive planner for user-serving wrapper sessions.",
            responsibilities=["classify request", "set success conditions", "coordinate the brain path"],
            keywords=["plan", "organize", "route", "help"],
        ),
        AssistantOrchestrator(
            name="OperatorAO",
            description="Executive owner for operator-facing task control and human handoff boundaries.",
            responsibilities=["operator intent", "handoff state", "approval prompts", "human-in-the-loop continuity"],
            keywords=["operator", "handoff", "human review", "manual control"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="RouterAO",
            description="Executive owner for route arbitration across experts, tools, providers, and fallback paths.",
            responsibilities=["expert routing", "provider routing", "fallback arbitration", "route telemetry"],
            keywords=["router", "route", "arbitrate", "fallback", "provider selection"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="MemoryAO",
            description="Executive owner for memory formation, compression, and recall.",
            responsibilities=["working memory", "episodic capture", "semantic distillation", "memory budgeting"],
            keywords=["memory", "remember", "recall", "context"],
        ),
        AssistantOrchestrator(
            name="DreamAO",
            description="Executive owner for recursive neural dreaming and scenario rehearsal.",
            responsibilities=["dream seeds", "failure replay", "counterfactual rehearsal", "promotion candidates"],
            keywords=["dream", "simulate", "what if", "scenario", "counterfactual"],
        ),
        AssistantOrchestrator(
            name="CritiqueAO",
            description="Executive owner for critique, verification, and skeptical review.",
            responsibilities=["hallucination checks", "evidence checks", "benchmark critique", "safety skepticism"],
            keywords=["critique", "verify", "evaluate", "audit", "benchmark", "review"],
        ),
        AssistantOrchestrator(
            name="SelfTrainingAO",
            description="Executive owner for curriculum, distillation, and self-improvement loops.",
            responsibilities=["curriculum", "teacher routing", "distillation", "improvement candidates"],
            keywords=["train", "learn", "curriculum", "study", "distill"],
        ),
        AssistantOrchestrator(
            name="TrainingAO",
            description="Executive owner for supervised training, distillation packages, and evaluation handoff.",
            responsibilities=["training package", "distillation handoff", "dataset readiness", "eval handoff"],
            keywords=["training", "fine tune", "distillation", "dataset", "trainer"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="EvolutionAO",
            description="Executive owner for governed architecture evolution and candidate mutation proposals.",
            responsibilities=["evolution candidates", "mutation proposals", "architecture deltas", "rollback-aware growth"],
            keywords=["evolution", "mutate", "architecture change", "candidate mutation", "growth proposal"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="MaintenanceAO",
            description="Executive owner for system maintenance, diagnostics, and migration continuity.",
            responsibilities=["health", "repair", "migration notes", "continuity"],
            keywords=["fix", "repair", "doctor", "health", "maintain"],
        ),
        AssistantOrchestrator(
            name="ReleaseAO",
            description="Executive owner for release readiness, product-surface evidence, and rollout gates.",
            responsibilities=["release readiness", "product entrypoint", "go/no-go evidence", "rollout receipts"],
            keywords=["release", "readiness", "ship", "go no go", "product surface"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="HardwareMonitorAO",
            description="Executive owner for hardware posture, local runtime health, and resource guardrails.",
            responsibilities=["hardware posture", "runtime health", "thermal awareness", "resource guardrails"],
            keywords=["hardware", "gpu", "cpu", "vram", "thermal", "resource"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="GovernanceAO",
            description="Executive owner for approvals, audit, and rollback discipline.",
            responsibilities=["approvals", "audit", "rollback", "policy logs"],
            keywords=["approve", "governance", "policy", "rollback", "compliance"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="AdminAO",
            description="Executive owner for operator approval, admin intent, and update authorization.",
            responsibilities=["admin approval", "operator intent", "safe apply authorization", "rollback signoff"],
            keywords=["admin", "operator", "approval", "apply", "rollback"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="SecurityAO",
            description="Executive owner for sandbox boundaries, privacy, and safe mutation scope.",
            responsibilities=["sandbox boundary", "safe file scope", "privacy guard", "mutation review"],
            keywords=["security", "sandbox", "safe", "mutation", "privacy"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="SafetyAO",
            description="Executive owner for risk containment and safe-mode behavior.",
            responsibilities=["safe mode", "risk escalation", "high-stakes containment"],
            keywords=["safety", "harm", "danger", "secure"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="MathAO",
            description="Domain AO for formal reasoning and quantitative problem-solving.",
            responsibilities=["math reasoning", "structured proofing", "quantitative tool discipline"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["math", "equation", "algebra", "proof", "calculate"],
        ),
        AssistantOrchestrator(
            name="CodingAO",
            description="Domain AO for code generation, repair, and tool-guided implementation.",
            responsibilities=["code reasoning", "debugging", "build discipline", "tool coordination"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["code", "python", "bug", "traceback", "function", "repo"],
        ),
        AssistantOrchestrator(
            name="MedicalAO",
            description="Domain AO for medically-sensitive reasoning under stronger caution gates.",
            responsibilities=["medical reasoning", "evidence restraint", "risk escalation"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["medical", "symptom", "diagnosis", "treatment", "patient"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="RuntimeAO",
            description="Executive owner for hardware-aware execution and quantization policy.",
            responsibilities=["runtime choice", "profiling", "quantization policy", "thermal awareness"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["runtime", "quantization", "latency", "gpu", "cpu", "memory budget"],
        ),
        AssistantOrchestrator(
            name="EvalsAO",
            description="External-style behavioral auditing surface for black-box evaluation.",
            responsibilities=["external evaluation", "report generation", "regression gates"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["eval", "smoke", "gate", "regression", "external auditor"],
        ),
        AssistantOrchestrator(
            name="EvaluationAO",
            description="Canonical evaluation authority for promotion, teacher replacement, and deployment gates.",
            responsibilities=["promotion evaluation", "teacher replacement gate", "deployment hold", "decision evidence"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["evaluation", "promotion", "teacher replacement", "deploy gate", "hold decision"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="ResearchAO",
            description="Executive owner for source-backed research, assimilation triage, and contradiction handling.",
            responsibilities=["source synthesis", "assimilation target triage", "contradiction review", "research evidence"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["research", "source", "assimilation", "cite", "evidence synthesis"],
        ),
        AssistantOrchestrator(
            name="DataIngestAO",
            description="Executive owner for dataset, document, and multimodal ingestion safety.",
            responsibilities=["data intake", "schema checks", "source provenance", "ingestion quarantine"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["ingest", "dataset", "document", "corpus", "source import"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="ProtocolAO",
            description="Executive owner for MCP, ACP, API, and tool protocol handshakes.",
            responsibilities=["protocol bridge", "tool handshake", "capability negotiation", "protocol trust"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["mcp", "acp", "protocol", "bridge", "handshake", "tool"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="VisualOpsAO",
            description="Executive owner for visualizer, control panel, and operator evidence clarity.",
            responsibilities=["visualizer posture", "control panel clarity", "operator proof", "replay visibility"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["visualops", "visualizer", "control panel", "dashboard", "replay visibility"],
        ),
        AssistantOrchestrator(
            name="FederationAO",
            description="Executive owner for sanitized federated learning packets and peer-trust review.",
            responsibilities=["federated packet review", "poisoning checks", "differential privacy", "peer quarantine"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["federated", "federation", "peer", "poisoning", "differential privacy"],
            risk_tier="high",
        ),
        AssistantOrchestrator(
            name="PackagingAO",
            description="Executive owner for wrapper packaging, installer evidence, and buyer-facing release bundles.",
            responsibilities=["packaging", "installer readiness", "buyer release evidence", "distribution manifest"],
            status_label="STRONG ACCEPTED DIRECTION",
            keywords=["packaging", "package", "bundle", "installer", "buyer"],
            risk_tier="high",
        ),
    ]
    return AssistantOrchestratorRegistry(orchestrators, artifacts_dir=artifacts_dir)


def _is_replayable_receipt(receipt: dict[str, Any]) -> bool:
    return (
        isinstance(receipt, dict)
        and receipt.get("surface_id") == "ao-execution-receipt"
        and receipt.get("raw_content_included") is False
        and isinstance(receipt.get("execution_id"), str)
        and isinstance(receipt.get("trace_ref"), str)
        and isinstance(receipt.get("ao_name"), str)
    )


def _privacy_digest(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _safe_ref(value: str) -> str:
    return str(value).replace(":", "_").replace("/", "_").replace("\\", "_")
