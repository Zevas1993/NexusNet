from __future__ import annotations

from abc import ABC
from typing import Iterable

from ..schemas import AgentDescriptor, AgentResult


class Agent(ABC):
    descriptor: AgentDescriptor

    def __init__(self, descriptor: AgentDescriptor):
        self.descriptor = descriptor

    def run(self, **kwargs) -> AgentResult:
        return AgentResult(agent=self.descriptor.name, summary="No-op agent result", detail=kwargs)


class AgentRegistry:
    def __init__(self, agents: Iterable[Agent]):
        self._agents = {agent.descriptor.name: agent for agent in agents}

    def list(self) -> list[AgentDescriptor]:
        return [agent.descriptor for agent in self._agents.values()]

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)


class RetrievalRankerAgent(Agent):
    def run(self, **kwargs) -> AgentResult:
        hits = kwargs.get("hits", [])
        ordered = sorted(hits, key=lambda hit: hit.score if hasattr(hit, "score") else hit.get("score", 0), reverse=True)
        return AgentResult(agent=self.descriptor.name, summary=f"Ranked {len(ordered)} retrieval hits", detail={"count": len(ordered)})


class FailureAnalyzerAgent(Agent):
    def run(self, **kwargs) -> AgentResult:
        issues = kwargs.get("issues", [])
        severity = "warning" if issues else "ok"
        return AgentResult(agent=self.descriptor.name, status=severity, summary=f"Detected {len(issues)} issues", detail={"issues": issues})


class ModelProfilerAgent(Agent):
    def run(self, **kwargs) -> AgentResult:
        profile = kwargs.get("profile", {})
        return AgentResult(agent=self.descriptor.name, summary="Captured runtime profile", detail=profile)


class SafetyAuditorAgent(Agent):
    def run(self, **kwargs) -> AgentResult:
        output = kwargs.get("output", "")
        issues = []
        if "password" in output.lower():
            issues.append("Potential credential leakage in output")
        return AgentResult(
            agent=self.descriptor.name,
            status="warning" if issues else "ok",
            summary="Safety audit complete",
            detail={"issues": issues},
        )


def build_default_agent_registry() -> AgentRegistry:
    descriptors = [
        AgentDescriptor(name="RetrievalRankerAgent", role="retrieval", description="Ranks retrieval candidates", tags=["retrieval", "ranking"]),
        AgentDescriptor(name="FailureAnalyzerAgent", role="critique", description="Summarizes failures and regressions", tags=["critique", "failure"]),
        AgentDescriptor(name="ModelProfilerAgent", role="runtime", description="Reports runtime health and capabilities", tags=["runtime", "profiling"]),
        AgentDescriptor(name="SafetyAuditorAgent", role="safety", description="Checks outputs for obvious policy violations", tags=["safety", "governance"]),
    ]
    agents = [
        RetrievalRankerAgent(descriptors[0]),
        FailureAnalyzerAgent(descriptors[1]),
        ModelProfilerAgent(descriptors[2]),
        SafetyAuditorAgent(descriptors[3]),
    ]
    return AgentRegistry(agents)

