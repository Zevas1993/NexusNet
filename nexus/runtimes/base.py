from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..schemas import Message, RuntimeProfile


def prompt_from_messages(messages: list[Message], prompt: str | None = None) -> str:
    if prompt:
        return prompt
    if not messages:
        return ""
    parts = []
    for message in messages:
        parts.append(f"{message.role.upper()}: {message.content}")
    return "\n".join(parts)


class RuntimeAdapter(ABC):
    runtime_name = "runtime"
    backend_type = "abstract"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str | None,
        messages: list[Message],
        model_id: str,
        expert: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError

    def profile(self) -> RuntimeProfile:
        health = self.health()
        return RuntimeProfile(
            runtime_name=self.runtime_name,
            backend_type=self.backend_type,
            available=bool(health.get("available", False)),
            health=health,
            capabilities=health.get("capabilities", {}),
            metrics=health.get("metrics", {}),
        )

