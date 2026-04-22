from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from nexus.schemas import Message, RuntimeProfile

from ..schemas import CapabilityProfile, SessionContext


class RuntimeBackend(Protocol):
    runtime_name: str

    def profile(self) -> RuntimeProfile:
        ...

    def generate(
        self,
        *,
        prompt: str | None,
        messages: list[Message],
        model_id: str,
        expert: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        ...


class BaseModelAdapter(ABC):
    adapter_role = "teacher"

    def __init__(self, *, model_id: str, runtime_backend: RuntimeBackend, profile: CapabilityProfile):
        self.model_id = model_id
        self.runtime_backend = runtime_backend
        self.profile = profile
        self.adapter_id = f"{self.adapter_role}:{self.model_id}"

    @abstractmethod
    def generate(self, *, session_context: SessionContext, prompt: str, messages: list[Message]) -> str:
        raise NotImplementedError

    def capability_profile(self) -> CapabilityProfile:
        return self.profile


class TeacherModelAdapter(BaseModelAdapter):
    adapter_role = "teacher"


class SpecialistModelAdapter(BaseModelAdapter):
    adapter_role = "specialist"
