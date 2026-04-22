from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class RecipeParameter(BaseModel):
    name: str
    type: Literal["string", "integer", "boolean", "list", "object"] = "string"
    required: bool = False
    default: Any | None = None
    description: str = ""


class RecipeSchedule(BaseModel):
    cadence: str
    timezone: str = "UTC"
    persistent_state: bool = True


class RecipeStep(BaseModel):
    step_id: str
    action: Literal["ao-dispatch", "skill-bundle", "gateway-policy", "tool-bundle", "review", "schedule", "subagent"]
    description: str
    ao_id: str | None = None
    skill_ids: list[str] = Field(default_factory=list)
    approved_tools: list[str] = Field(default_factory=list)
    gateway_policy: str | None = None
    subagent_mode: Literal["sequential", "parallel"] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecipeDefinition(BaseModel):
    recipe_id: str
    kind: Literal["recipe", "runbook"] = "recipe"
    label: str
    description: str
    version: str = "1.0"
    status_label: str = "STRONG ACCEPTED DIRECTION"
    parameters: list[RecipeParameter] = Field(default_factory=list)
    ao_targets: list[str] = Field(default_factory=list)
    skill_ids: list[str] = Field(default_factory=list)
    gateway_policy: str | None = None
    approved_tool_sets: list[str] = Field(default_factory=list)
    approved_tools: list[str] = Field(default_factory=list)
    roots_scope: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    schedule: RecipeSchedule | None = None
    steps: list[RecipeStep] = Field(default_factory=list)
    source_path: str | None = None

    @property
    def schedule_compatible(self) -> bool:
        return self.schedule is not None or any(step.action == "schedule" for step in self.steps)

    @property
    def parameterized(self) -> bool:
        return bool(self.parameters)

    @classmethod
    def from_payload(cls, payload: dict[str, Any], *, source_path: Path) -> "RecipeDefinition":
        enriched = dict(payload)
        enriched["source_path"] = str(source_path)
        return cls.model_validate(enriched)
