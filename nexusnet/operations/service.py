from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any

from nexus.schemas import OperatorRequest
from nexus.storage import NexusStore


SIGNAL_CONTRACT = [
    "receives_orders",
    "local_reasoning",
    "evidence_response",
    "veto_escalation",
    "consensus_contribution",
    "execution_status",
]

CANON_BINDING = {
    "source_document": "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
    "binding_rule": "capabilities must be source-bound, observable at runtime, eval-scored, policy-gated, and audit-reversible",
    "state_taxonomy": [
        "live_state",
        "simulated_state",
        "roadmap_state",
        "research_candidate_state",
    ],
}


class BrainOperationsService:
    def __init__(
        self,
        *,
        store: NexusStore,
        ao_registry: Any,
        agent_registry: Any,
        teacher_registry: Any,
    ):
        self.store = store
        self.ao_registry = ao_registry
        self.agent_registry = agent_registry
        self.teacher_registry = teacher_registry

    def issue_command(
        self,
        *,
        session_id: str | None,
        command_text: str,
        priority: str = "normal",
        target_surface: str = "mission-control-cockpit",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_session_id = session_id or "default"
        now = _utcnow()
        command_id = f"braincmd::{_slug(normalized_session_id)}::{int(time.time() * 1000)}"
        command = {
            "command_id": command_id,
            "session_id": normalized_session_id,
            "authority": "NexusBrain",
            "lifecycle_state": "issued",
            "priority": priority,
            "target_surface": target_surface,
            "command_text": command_text,
            "source_status": "canon-bound",
            "created_at": now,
            "control_refs": {
                "control_panel": "/ui/control-panel/",
                "visualizer_state": "/ops/brain/visualizer/state",
                "operations_summary": "/ops/brain/operations",
            },
            "context": context or {},
        }
        self.store.save_brain_operation_command(command)

        ao_signals = self._build_ao_signals(command=command)
        expert_signals = self._build_expert_signals(command=command)
        consensus = {
            "state": "pending-consensus",
            "veto_state": "clear",
            "authority": "NexusBrain",
            "decision_style": "commanded collective intelligence",
            "required_responses": ["AO evidence", "expert evidence", "security/governance veto", "execution status"],
        }
        timeline = self._persist_timeline(
            command=command,
            ao_signals=ao_signals,
            expert_signals=expert_signals,
            consensus=consensus,
        )
        payload = {
            "status_label": "LOCKED CANON",
            "command": command,
            "signal_contract": SIGNAL_CONTRACT,
            "canon_binding": CANON_BINDING,
            "ao_signals": ao_signals,
            "expert_signals": expert_signals,
            "consensus": consensus,
            "timeline": timeline,
        }
        self.store.save_audit_event(
            event_id=f"audit::{command_id}",
            action="brain_operation_command_issued",
            detail={
                "command_id": command_id,
                "session_id": normalized_session_id,
                "target_surface": target_surface,
                "canon_binding": CANON_BINDING,
            },
            created_at=now,
        )
        return payload

    def summary(self, *, session_id: str | None = None, limit: int = 25) -> dict[str, Any]:
        commands = self.store.list_brain_operation_commands(session_id=session_id, limit=limit)
        events = self.store.list_brain_operation_events(session_id=session_id, limit=max(limit * 6, 1))
        latest = commands[0] if commands else None
        active_command_id = latest.get("command_id") if latest else None
        active_events = [event for event in events if not active_command_id or event.get("command_id") == active_command_id]
        return {
            "status_label": "LOCKED CANON",
            "state": "live-bound" if latest else "standby",
            "session_id": session_id,
            "command_count": len(commands),
            "latest_command": latest,
            "commands": commands,
            "timeline": list(reversed(active_events or events)),
            "signal_contract": SIGNAL_CONTRACT,
            "canon_binding": CANON_BINDING,
        }

    def record_event(
        self,
        *,
        command_id: str,
        session_id: str | None,
        event_type: str,
        actor: str,
        detail: str,
        lifecycle_state: str | None = None,
        signal_type: str | None = None,
        state: str = "live_state",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        command = self.store.get_brain_operation_command(command_id)
        if command is None:
            raise KeyError(command_id)
        normalized_session_id = session_id or command.get("session_id") or "default"
        now = _utcnow()
        if lifecycle_state:
            command["lifecycle_state"] = lifecycle_state
            command["updated_at"] = now
            self.store.save_brain_operation_command(command)
        event_count = len(self.store.list_brain_operation_events(command_id=command_id, limit=500))
        event = {
            "event_id": f"{command_id}::event::{event_count + 1:02d}-{_slug(event_type)}",
            "command_id": command_id,
            "session_id": normalized_session_id,
            "event_type": event_type,
            "signal_type": signal_type or event_type,
            "actor": actor,
            "label": _event_label(event_type),
            "detail": detail,
            "state": state,
            "lifecycle_state": command.get("lifecycle_state"),
            "metadata": metadata or {},
            "created_at": now,
        }
        if event_type == "veto_escalation":
            event["consensus"] = {
                "state": "escalated",
                "veto_state": "active",
                "authority": actor,
                "required_response": "NexusBrain or GovernanceAO must clear the gate before execution can proceed.",
            }
        self.store.save_brain_operation_event(event)
        self.store.save_audit_event(
            event_id=f"audit::{event['event_id']}",
            action="brain_operation_event_recorded",
            detail={
                "command_id": command_id,
                "session_id": normalized_session_id,
                "event_type": event_type,
                "lifecycle_state": command.get("lifecycle_state"),
            },
            created_at=now,
        )
        return {
            "status_label": "LOCKED CANON",
            "command": command,
            "event": event,
            "summary": self.summary(session_id=normalized_session_id),
        }

    def _build_ao_signals(self, *, command: dict[str, Any]) -> list[dict[str, Any]]:
        request = OperatorRequest(
            session_id=command["session_id"],
            prompt=command["command_text"],
            metadata=command.get("context") or {},
            success_conditions=["respond with evidence", "preserve traceability", "surface vetoes"],
        )
        try:
            selected = self.ao_registry.select_request(request).model_dump(mode="json")
        except Exception:
            selected = {
                "ao_name": "PlanningAO",
                "status_label": "LOCKED CANON",
                "risk_tier": "medium",
                "responsibilities": ["classify request", "coordinate the brain path"],
            }
        selected_name = selected.get("ao_name") or selected.get("name") or "PlanningAO"
        signals = [
            {
                "signal_id": f"{command['command_id']}::ao::{selected_name}",
                "command_id": command["command_id"],
                "session_id": command["session_id"],
                "actor": selected_name,
                "role": "AO mini-brain",
                "reports_to": "NexusBrain",
                "signal_type": "receives_orders",
                "lifecycle_state": "ordered",
                "status_label": selected.get("status_label", "LOCKED CANON"),
                "risk_tier": selected.get("risk_tier", "medium"),
                "summary": selected.get("reason") or "AO received NexusBrain command and opened local reasoning.",
                "responsibilities": selected.get("responsibilities") or [],
            }
        ]
        for ao in self._ao_roster()[:3]:
            name = ao.get("name") or ao.get("ao_name")
            if not name or name == selected_name:
                continue
            signals.append(
                {
                    "signal_id": f"{command['command_id']}::ao::{name}",
                    "command_id": command["command_id"],
                    "session_id": command["session_id"],
                    "actor": name,
                    "role": "AO mini-brain",
                    "reports_to": "NexusBrain",
                    "signal_type": "local_reasoning",
                    "lifecycle_state": "standing-by",
                    "status_label": ao.get("status_label", "LOCKED CANON"),
                    "risk_tier": ao.get("risk_tier", "medium"),
                    "summary": "AO is available for local reasoning, evidence, veto, or execution routing.",
                    "responsibilities": ao.get("responsibilities") or [],
                }
            )
        return signals

    def _build_expert_signals(self, *, command: dict[str, Any]) -> list[dict[str, Any]]:
        assignments = [
            assignment.model_dump(mode="json")
            for assignment in self.teacher_registry.list_assignments()
            if not assignment.auxiliary and assignment.registry_layer == "v2026_live"
        ]
        if not assignments:
            assignments = [
                {"subject": "core-brain", "subject_display_name": "Core Brain", "status_label": "LOCKED CANON"},
                {"subject": "coding", "subject_display_name": "Coding Expert", "status_label": "LOCKED CANON"},
            ]
        signals = []
        for assignment in assignments[:4]:
            subject = assignment.get("subject") or "expert"
            signals.append(
                {
                    "signal_id": f"{command['command_id']}::expert::{subject}",
                    "command_id": command["command_id"],
                    "session_id": command["session_id"],
                    "actor": assignment.get("subject_display_name") or subject,
                    "subject": subject,
                    "role": "Expert mini-brain",
                    "reports_to": "AO Hive",
                    "signal_type": "evidence_response",
                    "lifecycle_state": "ready-for-evidence",
                    "status_label": assignment.get("status_label", "LOCKED CANON"),
                    "summary": "Expert mini-brain is ready to return domain evidence, uncertainty, and execution constraints.",
                    "benchmark_families": assignment.get("benchmark_families") or [],
                }
            )
        return signals

    def _ao_roster(self) -> list[dict[str, Any]]:
        snapshot = self.ao_registry.snapshot()
        if hasattr(snapshot, "model_dump"):
            snapshot = snapshot.model_dump(mode="json")
        return list(snapshot.get("active_aos") or [])

    def _persist_timeline(
        self,
        *,
        command: dict[str, Any],
        ao_signals: list[dict[str, Any]],
        expert_signals: list[dict[str, Any]],
        consensus: dict[str, Any],
    ) -> list[dict[str, Any]]:
        now = _utcnow()
        raw_events = [
            {
                "event_type": "command_issued",
                "actor": "NexusBrain",
                "label": "NexusBrain issued command",
                "detail": command["command_text"],
                "state": "live_state",
            },
            {
                "event_type": "ao_signal",
                "actor": ", ".join(signal["actor"] for signal in ao_signals[:2]),
                "label": "AO hive received command",
                "detail": "AO mini-brains opened local reasoning and routing.",
                "state": "live_state",
                "signals": ao_signals,
            },
            {
                "event_type": "expert_signal",
                "actor": ", ".join(signal["actor"] for signal in expert_signals[:2]),
                "label": "Experts prepared evidence response",
                "detail": "Expert mini-brains are ready for evidence and execution constraints.",
                "state": "live_state",
                "signals": expert_signals,
            },
            {
                "event_type": "consensus_state",
                "actor": "Commanded Collective Hive",
                "label": "Consensus/veto state opened",
                "detail": consensus["state"],
                "state": "live_state",
                "consensus": consensus,
            },
        ]
        events = []
        for index, event in enumerate(raw_events, start=1):
            payload = {
                "event_id": f"{command['command_id']}::event::{index:02d}",
                "command_id": command["command_id"],
                "session_id": command["session_id"],
                "created_at": now,
                **event,
            }
            self.store.save_brain_operation_event(payload)
            events.append(payload)
        return events


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "default"


def _event_label(event_type: str) -> str:
    labels = {
        "ao_signal": "AO hive signal recorded",
        "expert_signal": "Expert evidence signal recorded",
        "veto_escalation": "Veto or escalation recorded",
        "execution_status": "Execution status recorded",
        "memory_feedback": "Memory feedback recorded",
    }
    return labels.get(event_type, event_type.replace("_", " ").title())
