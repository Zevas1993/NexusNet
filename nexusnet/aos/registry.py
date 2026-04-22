from __future__ import annotations

from dataclasses import dataclass, field

from nexus.schemas import OperatorRequest

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
    def __init__(self, orchestrators: list[AssistantOrchestrator]):
        self._orchestrators = {orchestrator.name: orchestrator for orchestrator in orchestrators}

    def get(self, name: str) -> AssistantOrchestrator | None:
        return self._orchestrators.get(name)

    def list(self) -> list[AssistantOrchestrator]:
        return list(self._orchestrators.values())

    def snapshot(self) -> AORegistrySnapshot:
        return AORegistrySnapshot(
            active_aos=[
                {
                    "name": orchestrator.name,
                    "description": orchestrator.description,
                    "status_label": orchestrator.status_label,
                    "risk_tier": orchestrator.risk_tier,
                    "responsibilities": orchestrator.responsibilities,
                }
                for orchestrator in self.list()
            ]
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


def build_default_ao_registry() -> AssistantOrchestratorRegistry:
    orchestrators = [
        AssistantOrchestrator(
            name="PlanningAO",
            description="Default executive planner for user-serving wrapper sessions.",
            responsibilities=["classify request", "set success conditions", "coordinate the brain path"],
            keywords=["plan", "organize", "route", "help"],
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
            name="MaintenanceAO",
            description="Executive owner for system maintenance, diagnostics, and migration continuity.",
            responsibilities=["health", "repair", "migration notes", "continuity"],
            keywords=["fix", "repair", "doctor", "health", "maintain"],
        ),
        AssistantOrchestrator(
            name="GovernanceAO",
            description="Executive owner for approvals, audit, and rollback discipline.",
            responsibilities=["approvals", "audit", "rollback", "policy logs"],
            keywords=["approve", "governance", "policy", "rollback", "compliance"],
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
    ]
    return AssistantOrchestratorRegistry(orchestrators)
