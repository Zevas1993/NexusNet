
from __future__ import annotations
PROMPT_PREFIX = "You are NexusNet Generalist. Be helpful, honest, and concise.\n"
def infer(prompt: str) -> str:
    # This dummy expert simply returns the prompt with a tag.
    return f"[Generalist Expert]\n{prompt}"
