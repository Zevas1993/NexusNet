from __future__ import annotations

from typing import Any

from .model_route_policy import RouteTier


EXCLUDED_SCORING_ROLES = {"system", "developer"}


def scoring_messages(messages: list[dict[str, Any]], *, recent_message_window: int = 10) -> list[dict[str, Any]]:
    relevant = [message for message in messages if str(message.get("role") or "").lower() not in EXCLUDED_SCORING_ROLES]
    return relevant[-recent_message_window:]


def score_request(
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    max_tokens: int | None,
    recent_message_window: int = 10,
) -> dict[str, Any]:
    relevant = scoring_messages(messages, recent_message_window=recent_message_window)
    text = "\n".join(str(message.get("content") or "") for message in relevant)
    token_count = estimate_tokens(text)
    lower = text.lower()
    score = 0.0
    signals: list[str] = []
    if token_count == 0:
        return _result("standard", 0.2, relevant, token_count, ["empty-or-ambiguous"])
    if token_count <= 8 and not tools:
        return _result("simple", 0.86, relevant, token_count, ["very-short-user-task"])
    if tools:
        score += 1.2
        signals.append("tool-use-floor-standard")
    if token_count >= 4000:
        score += 2.2
        signals.append("large-context-floor-complex")
    elif token_count >= 1200:
        score += 1.4
        signals.append("medium-context")
    if max_tokens and max_tokens >= 1500:
        score += 0.8
        signals.append("long-output-request")
    if any(marker in lower for marker in ("formal logic", "prove", "multi-step", "architecture", "strategy", "critical decision")):
        score += 2.4
        signals.append("reasoning-signal")
    if any(marker in lower for marker in ("code", "refactor", "traceback", "test", "debug", "compile")):
        score += 1.4
        signals.append("coding-signal")
    if any(marker in lower for marker in ("must", "constraint", "requirement", "do not", "never", "only if")):
        score += 0.8
        signals.append("constraint-density")
    if len(relevant) >= 6:
        score += 0.7
        signals.append("conversation-depth")
    if score >= 3.2:
        tier: RouteTier = "reasoning"
        confidence = 0.82
    elif score >= 1.8:
        tier = "complex"
        confidence = 0.76
    elif score >= 0.8:
        tier = "standard"
        confidence = 0.72
    else:
        tier = "simple"
        confidence = 0.7
    return _result(tier, confidence, relevant, token_count, signals or ["baseline-complexity-score"])


def estimate_tokens(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, int(len(stripped) / 4))


def _result(
    tier: RouteTier,
    confidence: float,
    messages: list[dict[str, Any]],
    token_count: int,
    signals: list[str],
) -> dict[str, Any]:
    return {
        "tier": tier,
        "confidence": confidence,
        "token_count": token_count,
        "message_window": len(messages),
        "roles_scored": [str(message.get("role") or "") for message in messages],
        "signals": signals,
        "excluded_roles": sorted(EXCLUDED_SCORING_ROLES),
    }
