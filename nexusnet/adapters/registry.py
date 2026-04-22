from __future__ import annotations

from nexus.schemas import Message, ModelRegistration

from ..schemas import CapabilityProfile, SessionContext
from .base import RuntimeBackend, SpecialistModelAdapter, TeacherModelAdapter


class RegistryModelAdapter(TeacherModelAdapter):
    def __init__(self, registration: ModelRegistration, runtime_backend: RuntimeBackend, *, adapter_role: str = "teacher"):
        profile = CapabilityProfile(
            model_id=registration.model_id,
            runtime_name=registration.runtime_name,
            adapter_role=adapter_role,
            modalities=registration.capability_card.modalities,
            context_window=registration.capability_card.context_window,
            supports_tools=registration.capability_card.supports_tools,
            supports_streaming=False,
            supports_multimodal=any(mode != "text" for mode in registration.capability_card.modalities),
            preferred_domains=list(registration.capability_card.preferred_tasks),
            known_limits=list(registration.capability_card.known_weaknesses),
            telemetry={"available": registration.available, "tags": list(registration.tags)},
        )
        super().__init__(model_id=registration.model_id, runtime_backend=runtime_backend, profile=profile)
        self.registration = registration
        self.adapter_role = adapter_role
        self.adapter_id = f"{self.adapter_role}:{registration.model_id}"

    def generate(self, *, session_context: SessionContext, prompt: str, messages: list[Message]) -> str:
        return self.runtime_backend.generate(
            prompt=prompt,
            messages=messages,
            model_id=self.registration.model_id,
            expert=session_context.expert,
            metadata=session_context.metadata,
        )


class RegistrySpecialistAdapter(RegistryModelAdapter, SpecialistModelAdapter):
    adapter_role = "specialist"


def make_registry_adapter(registration: ModelRegistration, runtime_backend: RuntimeBackend, *, adapter_role: str = "teacher") -> RegistryModelAdapter:
    if adapter_role == "specialist":
        return RegistrySpecialistAdapter(registration, runtime_backend, adapter_role=adapter_role)
    return RegistryModelAdapter(registration, runtime_backend, adapter_role=adapter_role)
