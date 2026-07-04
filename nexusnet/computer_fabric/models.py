from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EnvironmentClass(str, Enum):
    EPHEMERAL = "ephemeral"
    PERSISTENT = "persistent"
    OPERATOR = "operator"


@dataclass(frozen=True)
class ComputerSessionRequest:
    goal: str
    task_type: str
    requested_tools: list[str] = field(default_factory=list)
    project_scope: str = "repo"
    privacy_class: str = "unknown"
    requested_environment: EnvironmentClass | None = None
    required_checks: list[str] = field(default_factory=list)
    schedule: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComputerSessionSummary:
    session_id: str
    environment_class: EnvironmentClass
    status: str
    session_dir: Path
    policy: dict[str, Any]
    event_types: list[str]
    artifact_count: int
    blocked_reasons: list[str]
    trust_summary: dict[str, Any]
