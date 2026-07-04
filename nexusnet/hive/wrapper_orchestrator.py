"""The wrapper's multi-agent ORCHESTRATION layer (replace teachers ASAP; multiplex; many capabilities).

Canon: NexusNet operates as a WRAPPER that does NOT cling to teacher models - the goal is to REPLACE
them as soon as the native experts can stand alone. Until then, the wrapper:
  - pools MULTIPLE external agents concurrently,
  - MULTIPLEXES one agent across MULTIPLE expert nodes (one agent serves many roles),
  - must encompass MANY CAPABILITIES (the union of the agent pool's skills covers the node roster),
  - and RELEASES each teacher binding the moment its native expert surpasses it (Teacher Replacement
    Protocol), driving the dependency ratio toward 0 (full native independence = birth-ready).

This is the live binding/release orchestrator (deterministic, governed); it tracks who serves whom,
capability coverage, and replacement progress.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WrapperAgent:
    """An external agent/model temporarily wrapped. Holds capabilities; not a permanent dependency."""
    agent_id: str
    capabilities: list[str] = field(default_factory=list)   # expert domains/skills it can serve
    max_nodes: int = 8                                       # how many nodes it may multiplex across


class WrapperAgentOrchestrator:
    """Pool of concurrent agents, multiplexed across expert nodes, released as natives replace them."""

    mutates_production = False

    def __init__(self) -> None:
        self._agents: dict[str, WrapperAgent] = {}
        self._binding: dict[str, str] = {}        # node_id -> agent_id (the temporary teacher)
        self._native: set[str] = set()            # nodes that have replaced their teacher (native)
        self._all_nodes: set[str] = set()
        self._user_pref: dict[str, str] = {}      # node_id -> end-user-chosen model (overrides default)

    # --- agent pool (multiple concurrent agents) ---

    def register_agent(self, agent: WrapperAgent) -> None:
        self._agents[agent.agent_id] = agent

    def active_agents(self) -> list[str]:
        """Agents currently serving at least one node (concurrently active in the wrapper)."""
        return sorted(set(self._binding.values()))

    def agent_load(self) -> dict[str, int]:
        loads = {a: 0 for a in self._agents}
        for ag in self._binding.values():
            loads[ag] = loads.get(ag, 0) + 1
        return loads

    # --- multiplex: one agent serves many nodes ---

    def assign(self, node_id: str, capability: str) -> str | None:
        """Bind a node to an agent that HAS the capability and spare capacity. Returns agent_id or None.

        One agent can be assigned to MANY nodes (multiplexing) until it hits `max_nodes`.
        """
        self._all_nodes.add(node_id)
        if node_id in self._native:
            return None                            # already native: no teacher needed
        loads = self.agent_load()
        # prefer the LEAST-loaded capable agent (balance the multiplex)
        candidates = sorted(
            (a for a in self._agents.values()
             if capability in a.capabilities and loads.get(a.agent_id, 0) < a.max_nodes),
            key=lambda a: loads.get(a.agent_id, 0),
        )
        if not candidates:
            return None
        chosen = candidates[0].agent_id
        self._binding[node_id] = chosen
        return chosen

    def multiplex_map(self) -> dict[str, list[str]]:
        """agent_id -> the list of nodes it currently serves (the multiplex fan-out)."""
        out: dict[str, list[str]] = {}
        for node, agent in self._binding.items():
            out.setdefault(agent, []).append(node)
        return {a: sorted(ns) for a, ns in out.items()}

    # --- replace teachers ASAP (Teacher Replacement Protocol) ---

    def record_competence(self, node_id: str, *, native_score: float, teacher_score: float,
                          margin: float = 0.0) -> dict[str, Any]:
        """When the native expert matches/beats its teacher, RELEASE the binding - replace, don't hold."""
        self._all_nodes.add(node_id)
        replaced = native_score >= teacher_score + margin
        if replaced:
            self._native.add(node_id)
            agent = self._binding.pop(node_id, None)   # drop the temporary teacher immediately
            return {"node_id": node_id, "replaced": True, "released_agent": agent,
                    "now_native": True}
        return {"node_id": node_id, "replaced": False, "still_depends_on": self._binding.get(node_id)}

    def release_idle_agents(self) -> list[str]:
        """Agents no longer serving any node are dropped from the pool (teacher no longer needed)."""
        serving = set(self._binding.values())
        idle = [a for a in self._agents if a not in serving]
        for a in idle:
            del self._agents[a]
        return sorted(idle)

    # --- routing preference: native expert preferred after eviction, unless the user overrides ---

    def set_user_preference(self, node_id: str, model_id: str) -> None:
        """End-user explicitly chooses a model for a node - overrides the default native preference."""
        self._user_pref[node_id] = model_id

    def clear_user_preference(self, node_id: str) -> None:
        """Remove the user override - routing reverts to the default (native if formed, else teacher)."""
        self._user_pref.pop(node_id, None)

    def route(self, node_id: str, capability: str | None = None) -> dict[str, Any]:
        """Resolve the preferred provider for a node.

        Precedence: (1) explicit END-USER choice overrides everything; (2) once the native expert has
        formed (teacher evicted), the NATIVE expert is the preferred default; (3) otherwise the
        temporary teacher agent serves (auto-assigning a capable one if needed).
        """
        if node_id in self._user_pref:
            return {"node_id": node_id, "provider": self._user_pref[node_id],
                    "source": "user_override", "preferred": True,
                    "overrides_native": node_id in self._native}
        if node_id in self._native:
            return {"node_id": node_id, "provider": f"native::{node_id}",
                    "source": "native_expert", "preferred": True, "overrides_native": False}
        agent = self._binding.get(node_id)
        if agent is None and capability is not None:
            agent = self.assign(node_id, capability)
        if agent is not None:
            return {"node_id": node_id, "provider": agent, "source": "teacher_agent",
                    "preferred": False, "overrides_native": False}
        return {"node_id": node_id, "provider": None, "source": "unrouted", "preferred": False}

    # --- coverage + replacement progress ---

    def capability_coverage(self, required: list[str]) -> dict[str, Any]:
        """Does the agent pool encompass all required capabilities?"""
        union: set[str] = set()
        for a in self._agents.values():
            union |= set(a.capabilities)
        covered = [c for c in required if c in union]
        missing = [c for c in required if c not in union]
        return {"covered": covered, "missing": missing,
                "coverage": (len(covered) / len(required)) if required else 1.0,
                "pool_capabilities": sorted(union)}

    def dependency_ratio(self) -> float:
        """Fraction of nodes still depending on a teacher (0.0 = fully native = birth-ready)."""
        if not self._all_nodes:
            return 0.0
        depending = len([n for n in self._all_nodes if n in self._binding])
        return depending / len(self._all_nodes)

    def status(self) -> dict[str, Any]:
        return {
            "agents_in_pool": sorted(self._agents),
            "active_agents": self.active_agents(),
            "multiplex_map": self.multiplex_map(),
            "agent_load": self.agent_load(),
            "native_nodes": sorted(self._native),
            "depending_nodes": sorted(self._binding),
            "user_overrides": dict(self._user_pref),
            "dependency_ratio": self.dependency_ratio(),
            "fully_native": self.dependency_ratio() == 0.0 and bool(self._all_nodes),
        }
