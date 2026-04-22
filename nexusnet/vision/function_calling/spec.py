from __future__ import annotations

from pydantic import BaseModel, Field


class VisualFunctionSpec(BaseModel):
    function_name: str
    description: str
    arguments: dict[str, str] = Field(default_factory=dict)


def default_visual_functions() -> list[VisualFunctionSpec]:
    return [
        VisualFunctionSpec(
            function_name="inspect_bounding_boxes",
            description="Return normalized grounding boxes for the requested labels.",
            arguments={"labels": "array[string]"},
        ),
        VisualFunctionSpec(
            function_name="summarize_document_layout",
            description="Return structured sections, reading order, and layout notes.",
            arguments={"language_hint": "string"},
        ),
        VisualFunctionSpec(
            function_name="propose_visual_tool_call",
            description="Recommend a downstream visual tool or policy-safe function call for the current image task.",
            arguments={"task_intent": "string"},
        ),
    ]
