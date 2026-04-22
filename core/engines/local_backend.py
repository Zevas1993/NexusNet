from __future__ import annotations

class Engine:
    """Legacy selector shim for the local transformers backend."""

    name = "transformers"

    def generate(self, prompt: str, **_: object) -> str:
        return f"[transformers:dry] {prompt}"
