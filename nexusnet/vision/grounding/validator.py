from __future__ import annotations

from typing import Any


def validate_grounding_payload(*, schema: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    boxes = list(payload.get("boxes", []))
    coordinates = schema.get("coordinates", "xyxy")
    normalized = bool(schema.get("normalized", True))
    valid_boxes = 0
    for box in boxes:
        values = box.get("bbox", [])
        if coordinates != "xyxy" or len(values) != 4:
            continue
        if normalized and any(not isinstance(value, (int, float)) or value < 0 or value > 1 for value in values):
            continue
        valid_boxes += 1
    return {
        "valid": valid_boxes == len(boxes),
        "box_count": len(boxes),
        "valid_box_count": valid_boxes,
        "schema_format": schema.get("format"),
    }
