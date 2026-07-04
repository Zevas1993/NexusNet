"""Canon Aspect 13: real read-only screen/UI parsing + instruction grounding (no OS control)."""
from __future__ import annotations

from nexusnet.vision.screen_parse import parse_ui_tree, ground_instruction, ocr_reading_order


def _tree():
    return [
        {"role": "heading", "text": "Settings", "bbox": [0, 0, 200, 20]},
        {"role": "button", "text": "Save changes", "bbox": [10, 40, 100, 30]},
        {"role": "link", "text": "Cancel", "bbox": [120, 40, 60, 30]},
        {"role": "textbox", "text": "Email", "bbox": [10, 80, 200, 30]},
        {"role": "label", "text": "Notifications", "bbox": [10, 120, 100, 20]},
    ]


def test_parse_classifies_clickable_and_indexes_text():
    parse = parse_ui_tree(_tree())
    assert parse["count"] == 5
    assert parse["clickable_count"] == 3              # button + link + textbox
    assert parse["read_only"] is True
    assert parse["text_index"]["save changes"] == 1   # text lookup built
    assert parse["elements"][4]["clickable"] is False  # label is not clickable


def test_ground_instruction_finds_the_right_element():
    parse = parse_ui_tree(_tree())
    g = ground_instruction(parse, "click the save changes button")
    assert g["grounded"] is True
    assert g["target_id"] == 1 and g["target_role"] == "button"
    assert g["confidence"] > 0.0
    assert g["action_allowed"] is False              # perception only, action stays gated


def test_ground_prefers_matching_text():
    parse = parse_ui_tree(_tree())
    g = ground_instruction(parse, "cancel")
    assert g["target_id"] == 2 and g["target_text"] == "Cancel"


def test_ground_returns_ungrounded_when_no_match():
    parse = parse_ui_tree(_tree())
    g = ground_instruction(parse, "purchase a spaceship")
    assert g["grounded"] is False and g["target_id"] is None and g["confidence"] == 0.0


def test_ocr_reading_order_is_top_to_bottom_left_to_right():
    regions = [
        {"text": "world", "bbox": [120, 10, 50, 20]},
        {"text": "hello", "bbox": [10, 10, 50, 20]},     # same row, left of "world"
        {"text": "second", "bbox": [10, 60, 80, 20]},    # next row
    ]
    out = ocr_reading_order(regions)
    assert out["text"] == "hello world second"
    assert out["rows"] == 2 and out["regions"] == 3


def test_empty_inputs_are_safe():
    parse = parse_ui_tree([])
    assert parse["count"] == 0
    assert ground_instruction(parse, "anything")["grounded"] is False
    assert ocr_reading_order([])["text"] == ""
