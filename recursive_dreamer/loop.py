from __future__ import annotations

import re


_MAX_PROMPT_CHARS = 8192
_MAX_RESULT_CHARS = 32768
_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{2,}", re.IGNORECASE)
_STOP_WORDS = frozenset(
    {
        "and",
        "answer",
        "are",
        "for",
        "from",
        "give",
        "how",
        "into",
        "the",
        "this",
        "with",
    }
)


def dream_once(prompt: str, draft: str) -> str:
    """Run one bounded, deterministic critique pass over a generated draft.

    The legacy orchestrator expects a text-in/text-out hook. This compatibility
    lane preserves the generated draft and adds only actionable, prompt-grounded
    critique. It performs no network access, persistence, training, or production
    mutation; governed DreamLab promotion remains in the current NexusNet lanes.
    """

    if not isinstance(prompt, str) or not isinstance(draft, str):
        raise TypeError("prompt and draft must be strings")

    bounded_prompt = prompt[:_MAX_PROMPT_CHARS]
    base = _normalize_text(draft)
    if not base:
        base = "No usable draft was produced."

    missing_concepts = _missing_prompt_concepts(bounded_prompt, base)
    findings: list[str] = []
    if missing_concepts:
        findings.append(f"Address missing prompt concepts: {', '.join(missing_concepts[:4])}.")
    if len(base) < 120:
        findings.append("Strengthen the reasoning with explicit assumptions, evidence, and a verifiable conclusion.")
    elif "evidence" in bounded_prompt.lower() and "evidence" not in base.lower():
        findings.append("Identify the evidence supporting the conclusion and distinguish it from assumptions.")

    if not findings:
        return base[:_MAX_RESULT_CHARS]

    refinement = "\n".join(f"- {finding}" for finding in findings)
    result = f"{base}\n\nDream refinement:\n{refinement}"
    return result[:_MAX_RESULT_CHARS].rstrip()


def _missing_prompt_concepts(prompt: str, draft: str) -> list[str]:
    draft_terms = {token.lower() for token in _TOKEN_PATTERN.findall(draft)}
    missing: list[str] = []
    seen: set[str] = set()
    for token in _TOKEN_PATTERN.findall(prompt):
        normalized = token.lower()
        if normalized in _STOP_WORDS or normalized in draft_terms or normalized in seen:
            continue
        seen.add(normalized)
        missing.append(normalized)
    return missing


def _normalize_text(value: str) -> str:
    paragraphs = [" ".join(paragraph.split()) for paragraph in re.split(r"\n\s*\n", value.strip())]
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph)
