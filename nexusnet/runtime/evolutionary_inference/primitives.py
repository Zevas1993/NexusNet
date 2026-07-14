from __future__ import annotations

import importlib.util

from .schemas import InferencePrimitive


class InferencePrimitiveRegistry:
    def __init__(self, primitives: list[InferencePrimitive]) -> None:
        self._primitives = {primitive.primitive_id: primitive for primitive in primitives}

    @classmethod
    def default(cls) -> "InferencePrimitiveRegistry":
        moe_path = "nexusnet.runtime.moe_residency"
        moe_available = importlib.util.find_spec(moe_path) is not None
        return cls(
            [
                InferencePrimitive(
                    primitive_id="portable.cpu-reference",
                    description="Portable CPU and system-memory reference execution fallback.",
                    compatible_model_families=["all"],
                    required_resources=["cpu", "system-ram"],
                    effects=["portable-execution", "baseline-correctness"],
                    implementation_state="available",
                    evidence_state="portable-reference",
                    adapter_path=None,
                ),
                InferencePrimitive(
                    primitive_id="moe.selective-residency",
                    description="Existing tiered expert residency and selective MoE execution path.",
                    compatible_model_families=["moe"],
                    required_resources=["cpu", "system-ram", "gpu"],
                    effects=["tiered-expert-residency", "limited-vram-execution", "expert-prefetch"],
                    implementation_state="available" if moe_available else "unavailable",
                    evidence_state="existing-implementation" if moe_available else "unverified",
                    adapter_path=moe_path,
                ),
            ]
        )

    def get(self, primitive_id: str) -> InferencePrimitive:
        return self._primitives[primitive_id]

    def list(self) -> list[InferencePrimitive]:
        return [self._primitives[key] for key in sorted(self._primitives)]

    def list_ids(self) -> list[str]:
        return sorted(self._primitives)
