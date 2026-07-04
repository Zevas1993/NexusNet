from __future__ import annotations

from typing import Any


SPECIFICITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "coding": (
        "code",
        "function",
        "class",
        "traceback",
        "pytest",
        "regression",
        "typescript",
        "python",
        "refactor",
        "compile",
    ),
    "web_browsing": ("browse", "website", "url", "search", "web page", "browser"),
    "data_analysis": ("csv", "dataframe", "analyze data", "chart", "statistics", "sql"),
    "image_generation": ("generate image", "illustration", "photo", "sprite", "render"),
    "video_generation": ("video", "clip", "caption", "reframe", "remotion"),
    "social_media": ("linkedin", "twitter", "x post", "social media", "carousel"),
    "email_management": ("email", "inbox", "draft reply", "gmail", "outlook"),
    "calendar_management": ("calendar", "meeting", "schedule", "appointment"),
    "trading": ("trading", "trade", "broker", "portfolio", "buy", "sell", "order"),
}

TOOL_PREFIXES: dict[str, str] = {
    "python": "coding",
    "filesystem": "coding",
    "git": "coding",
    "browser": "web_browsing",
    "web": "web_browsing",
    "image": "image_generation",
    "video": "video_generation",
    "email": "email_management",
    "calendar": "calendar_management",
    "broker": "trading",
    "market": "trading",
}


def detect_specificity(*, task_type: str | None, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    if task_type in SPECIFICITY_KEYWORDS:
        return {
            "category": task_type,
            "confidence": 1.0,
            "reason": f"explicit-task-type::{task_type}",
            "signals": [f"task_type::{task_type}"],
        }
    text = "\n".join(str(message.get("content") or "") for message in messages).lower()
    signals: list[str] = []
    scores: dict[str, float] = {}
    for category, keywords in SPECIFICITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] = scores.get(category, 0.0) + 1.0
                signals.append(f"keyword::{category}::{keyword}")
    for tool in tools:
        name = _tool_name(tool)
        prefix = name.split(".", 1)[0].split("/", 1)[0].lower()
        category = TOOL_PREFIXES.get(prefix)
        if category:
            scores[category] = scores.get(category, 0.0) + 1.25
            signals.append(f"tool::{category}::{name}")
    if not scores:
        return {"category": None, "confidence": 0.0, "reason": "no-specificity-match", "signals": []}
    category, score = sorted(scores.items(), key=lambda item: item[1], reverse=True)[0]
    confidence = min(0.99, 0.45 + (score * 0.14))
    return {
        "category": category,
        "confidence": round(confidence, 3),
        "reason": f"specificity::{category}",
        "signals": signals,
    }


def _tool_name(tool: dict[str, Any]) -> str:
    if "name" in tool:
        return str(tool["name"])
    function = tool.get("function") if isinstance(tool.get("function"), dict) else {}
    if "name" in function:
        return str(function["name"])
    return str(tool.get("type") or "")
