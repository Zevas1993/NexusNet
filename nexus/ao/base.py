from __future__ import annotations

from abc import ABC
from typing import Iterable

from ..schemas import AODescriptor, OperatorRequest


class AO(ABC):
    descriptor: AODescriptor

    def __init__(self, descriptor: AODescriptor):
        self.descriptor = descriptor

    def can_handle(self, request: OperatorRequest) -> bool:
        return True

    def plan(self, request: OperatorRequest) -> dict:
        return {
            "ao": self.descriptor.name,
            "success_conditions": request.success_conditions or ["respond coherently", "record trace", "persist memory"],
        }


class AORegistry:
    def __init__(self, aos: Iterable[AO]):
        self._aos = {ao.descriptor.name: ao for ao in aos}

    def list(self) -> list[AODescriptor]:
        return [ao.descriptor for ao in self._aos.values()]

    def get(self, name: str) -> AO | None:
        return self._aos.get(name)

    def select(self, request: OperatorRequest) -> AODescriptor:
        for ao in self._aos.values():
            if ao.can_handle(request):
                return ao.descriptor
        return next(iter(self._aos.values())).descriptor


class NamedAO(AO):
    pass


def build_default_ao_registry() -> AORegistry:
    descriptors = [
        AODescriptor(name="PlanningAO", description="Coordinates user-facing execution plans", responsibilities=["classify request", "choose path", "set success conditions"]),
        AODescriptor(name="MemoryAO", description="Owns memory reads, writes, and compression hooks", responsibilities=["working memory", "episodic writes", "semantic distillation"]),
        AODescriptor(name="CritiqueAO", description="Scores quality and failure modes", responsibilities=["groundedness", "critique", "reflection"]),
        AODescriptor(name="ToolAO", description="Owns tool manifests and execution policies", responsibilities=["tool routing", "permissions", "health"]),
        AODescriptor(name="RuntimeAO", description="Selects runtime and model execution paths", responsibilities=["runtime selection", "fallbacks", "profiling"]),
        AODescriptor(name="GovernanceAO", description="Enforces approval and audit policy", responsibilities=["approvals", "audit", "rollback"]),
        AODescriptor(name="FoundryAO", description="Tracks foundry-facing datasets and experiments", responsibilities=["dataset lineage", "shadow artifacts", "native promotion gates"]),
    ]
    return AORegistry([NamedAO(descriptor) for descriptor in descriptors])

