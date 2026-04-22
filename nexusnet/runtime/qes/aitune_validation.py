from __future__ import annotations

from typing import Any

from .aitune_matrix import AITuneSupportedLaneMatrix
from .aitune_runner import AITuneValidationRunner

class AITuneValidationMatrix:
    def __init__(self, *, config: dict[str, Any], artifacts: Any, adapter: Any | None = None):
        self.config = config
        self.artifacts = artifacts
        self.matrix_builder = AITuneSupportedLaneMatrix(config=config)
        self.runner = AITuneValidationRunner(config=config, artifacts=artifacts, matrix=self.matrix_builder, adapter=adapter)

    def matrix(
        self,
        *,
        capability: dict[str, Any] | None = None,
        applicability: dict[str, Any] | None = None,
        model_id: str = "unbound",
    ) -> dict[str, Any]:
        return self.matrix_builder.matrix(capability=capability, applicability=applicability, model_id=model_id)

    def readiness(self, *, capability: dict[str, Any], applicability: dict[str, Any] | None = None, model_id: str = "unbound") -> dict[str, Any]:
        return self.runner.readiness(capability=capability, applicability=applicability, model_id=model_id)

    def run(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any] | None = None,
        model_id: str = "unbound",
        simulate: bool = False,
    ) -> dict[str, Any]:
        return self.runner.run(capability=capability, applicability=applicability, model_id=model_id, simulate=simulate)
