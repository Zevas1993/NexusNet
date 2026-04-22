from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..schemas import BackendCapabilityCard


class BrainRuntimeBackend(ABC):
    runtime_name: str = "runtime"
    backend_type: str = "generic"
    status_label: str = "STRONG ACCEPTED DIRECTION"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def capability_card(self) -> BackendCapabilityCard:
        raise NotImplementedError
