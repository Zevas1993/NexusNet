from __future__ import annotations

from pathlib import Path
from typing import Mapping

from nexus.runtimes.worker import WorkerRuntimeAdapter

from .contracts import RuntimePackManifest
from .supervisor import WorkerSupervisor


class WorkerFactoryError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class WorkerAdapterFactory:
    def __init__(self, *, interpreter: str | Path) -> None:
        self.interpreter = Path(interpreter)

    def create(
        self,
        manifest: RuntimePackManifest,
        *,
        environment: Mapping[str, str] | None = None,
    ) -> WorkerRuntimeAdapter:
        declared = manifest.launch.command
        if not declared or declared[0] != "python":
            raise WorkerFactoryError("worker-launch-token-unsupported")
        supplied = dict(environment or {})
        allowed = {name.casefold() for name in manifest.launch.environment_allowlist}
        if any(name.casefold() not in allowed for name in supplied):
            raise WorkerFactoryError("worker-environment-not-allowed")
        supervisor = WorkerSupervisor(
            command=[str(self.interpreter), *declared[1:]],
            environment=supplied,
            request_timeout_s=max(manifest.self_test_probe.timeout_ms / 1000.0, 1.0),
        )
        return WorkerRuntimeAdapter(manifest=manifest, supervisor=supervisor)
