from __future__ import annotations

import json
from pathlib import Path

from ..schemas import AgentCapabilityCard, AgentExecutionRecord, SessionAgentProvenance


def default_agent_capability_cards() -> list[AgentCapabilityCard]:
    return [
        AgentCapabilityCard(
            agent_id="standard-wrapper-agent",
            label="Standard Wrapper Agent",
            description="Default wrapper-serving execution path inside the NexusNet cognition layer.",
            modes=["standard-chat"],
            policy_hooks=["trace-preservation", "teacher-lineage", "brain-first-generate"],
            status_label="LOCKED CANON",
            tags=["wrapper", "default"],
        ),
        AgentCapabilityCard(
            agent_id="openclaw-agent",
            label="OpenClaw Agent",
            description="Tool-heavy wrapper execution surface for operator-style task flows.",
            modes=["openclaw"],
            policy_hooks=["tool-discipline", "trace-preservation", "ao-visibility"],
            status_label="STRONG ACCEPTED DIRECTION",
            tags=["wrapper", "agent-surface", "tools"],
        ),
        AgentCapabilityCard(
            agent_id="hermes-agent",
            label="Hermes Agent",
            description="Guided assistant-manager execution surface for broader delegated workflows.",
            modes=["hermes-agent"],
            policy_hooks=["session-provenance", "ao-visibility", "teacher-lineage"],
            status_label="STRONG ACCEPTED DIRECTION",
            tags=["wrapper", "agent-surface", "assistant"],
        ),
        AgentCapabilityCard(
            agent_id="monitor-operative-agent",
            label="Monitor Operative Agent",
            description="Persistent scheduled-monitor execution surface with memory, traceability, and governed approvals.",
            modes=["scheduled-monitor"],
            policy_hooks=["trace-preservation", "memory-lineage", "governed-schedule"],
            status_label="STRONG ACCEPTED DIRECTION",
            tags=["wrapper", "scheduled", "monitoring"],
        ),
    ]


class BrainAgentRegistry:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self._cards = {card.agent_id: card for card in default_agent_capability_cards()}
        self._executions: dict[str, list[AgentExecutionRecord]] = {}

    def list_capabilities(self) -> list[AgentCapabilityCard]:
        return list(self._cards.values())

    def select_for_mode(self, wrapper_mode: str | None) -> AgentCapabilityCard:
        mode = wrapper_mode or "standard-chat"
        for card in self._cards.values():
            if mode in card.modes:
                return card
        return self._cards["standard-wrapper-agent"]

    def record_execution(
        self,
        *,
        session_id: str,
        trace_id: str,
        wrapper_mode: str,
        selected_ao: str | None,
        selected_runtime: str | None,
        selected_backend: str | None,
        metadata: dict | None = None,
    ) -> AgentExecutionRecord:
        card = self.select_for_mode(wrapper_mode)
        record = AgentExecutionRecord(
            agent_id=card.agent_id,
            session_id=session_id,
            trace_id=trace_id,
            wrapper_mode=wrapper_mode,
            selected_ao=selected_ao,
            selected_runtime=selected_runtime,
            selected_backend=selected_backend,
            policy_hooks=card.policy_hooks,
            metadata=metadata or {},
            status_label=card.status_label,
        )
        self._executions.setdefault(session_id, []).append(record)
        self._write_artifact(record)
        return record

    def session_provenance(self, session_id: str) -> SessionAgentProvenance:
        executions = self._executions.get(session_id, [])
        active_agent = executions[-1].agent_id if executions else None
        return SessionAgentProvenance(session_id=session_id, active_agent_id=active_agent, executions=executions)

    def _write_artifact(self, record: AgentExecutionRecord) -> None:
        destination = self.artifacts_dir / "agents" / f"{record.execution_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(record.model_dump(mode="json"), indent=2), encoding="utf-8")
