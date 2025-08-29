
from __future__ import annotations
import re
PROMPT_PREFIX = (
    "You are NexusNet Code Expert. Provide precise, minimal, working answers.\n"
    "When relevant, include short code blocks. Avoid verbose prose.\n"
)

def infer(prompt: str) -> str:
    # Minimal linter-like triage: detect Python function signature or error keywords
    issues = []
    if "Traceback" in prompt or "error:" in prompt.lower():
        issues.append("Detected error/traceback context; suggest reproducer and fix.")
    if re.search(r"def\s+\w+\(", prompt):
        issues.append("Detected Python function definition.")
    header = "[Code Expert]"
    if issues:
        header += " " + " | ".join(issues)
    return f"{header}\n{prompt}"
