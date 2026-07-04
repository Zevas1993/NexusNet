"""Canon Aspect 13: real read-only screen/UI PARSING + instruction grounding (OmniParser-style).

`MultimodalComputerUseController` is plan-only (it cannot execute, by safety design). What was missing
is the perception half: turning a provided UI structure / text regions into a normalized, grounded
parse. This is that - DETERMINISTIC, READ-ONLY, no OS control, no screen capture: it operates on a
provided accessibility/DOM-like element list (or OCR text regions) and produces:

  - parse_ui_tree: a normalized element index with clickable classification + a text lookup.
  - ground_instruction: map a natural-language instruction to the best-matching element (the grounding
    a computer-use planner needs before it proposes - still gated to plan-only downstream).
  - ocr_reading_order: order text regions into human reading order (top->bottom, left->right).

It produces perception evidence only; it never clicks, types, or controls anything.
"""
from __future__ import annotations

import re
from typing import Any

CLICKABLE_ROLES = {"button", "link", "textbox", "menuitem", "checkbox", "tab", "switch", "combobox"}
_STOP = {"the", "a", "an", "to", "on", "in", "of", "and", "click", "press", "tap", "select", "open"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP}


def parse_ui_tree(elements: list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize a provided UI element list into an indexed, clickable-classified parse."""
    parsed: list[dict[str, Any]] = []
    text_index: dict[str, int] = {}
    for i, e in enumerate(elements):
        role = str(e.get("role", "")).lower()
        text = str(e.get("text", ""))
        bbox = e.get("bbox", [0, 0, 0, 0])
        clickable = role in CLICKABLE_ROLES or bool(e.get("clickable"))
        parsed.append({"elem_id": i, "role": role, "text": text, "bbox": list(bbox),
                       "clickable": clickable})
        if text:
            text_index.setdefault(text.strip().lower(), i)
    return {
        "elements": parsed,
        "count": len(parsed),
        "clickable_count": sum(1 for p in parsed if p["clickable"]),
        "text_index": text_index,
        "read_only": True,
    }


def ground_instruction(parse: dict[str, Any], instruction: str) -> dict[str, Any]:
    """Find the element a natural-language instruction refers to (token-overlap grounding)."""
    instr = _tokens(instruction)
    best_id, best_score = None, 0.0
    for el in parse["elements"]:
        overlap = len(instr & _tokens(el["text"]))
        # prefer clickable targets for action-style instructions
        score = overlap + (0.25 if el["clickable"] else 0.0)
        if overlap > 0 and score > best_score:
            best_id, best_score = el["elem_id"], score
    confidence = (best_score / max(1, len(instr))) if best_id is not None else 0.0
    target = parse["elements"][best_id] if best_id is not None else None
    return {
        "grounded": best_id is not None,
        "target_id": best_id,
        "target_text": target["text"] if target else None,
        "target_role": target["role"] if target else None,
        "confidence": round(confidence, 4),
        "action_allowed": False,    # grounding is perception only; action stays plan-only/gated
    }


def perceive_screen(elements: list[dict[str, Any]], instruction: str) -> dict[str, Any]:
    """One perception bundle for a computer-use planner: parse the UI + ground the instruction.

    Read-only perception evidence the plan-only `MultimodalComputerUseController` can consume; the
    proposed action still flows through that controller's safety/sandbox gates (action_allowed=False).
    """
    parse = parse_ui_tree(elements)
    grounding = ground_instruction(parse, instruction)
    return {
        "parse": parse,
        "grounding": grounding,
        "instruction": instruction,
        "perception_only": True,
        "action_allowed": False,
    }


def ocr_reading_order(regions: list[dict[str, Any]], *, row_tol: int = 12) -> dict[str, Any]:
    """Order OCR text regions (each {text, bbox:[x,y,w,h]}) into human reading order and join them."""
    items = [(r.get("bbox", [0, 0, 0, 0]), str(r.get("text", ""))) for r in regions]
    # group into rows by y (within row_tol), then sort each row by x
    items.sort(key=lambda it: it[0][1])
    rows: list[list[tuple]] = []
    for bbox, text in items:
        if rows and abs(bbox[1] - rows[-1][0][0][1]) <= row_tol:
            rows[-1].append((bbox, text))
        else:
            rows.append([(bbox, text)])
    ordered: list[str] = []
    for row in rows:
        row.sort(key=lambda it: it[0][0])
        ordered.extend(text for _, text in row if text)
    return {"text": " ".join(ordered), "rows": len(rows), "regions": len(regions)}
