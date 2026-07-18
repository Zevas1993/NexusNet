from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable
from urllib.parse import urlsplit

from .acquisition import AcquisitionError, ArtifactAcquirer
from .contracts import PackLifecycleState, PackType, RuntimePackManifest
from .registry import RegistryError, RuntimePackRecord, RuntimePackRegistry


_IDENTITY = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_REASON = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")


class EnvironmentBuildError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class PackInstallError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class PackVerification:
    health_passed: bool
    self_test_passed: bool
    reason_code: str

    def __post_init__(self) -> None:
        if not _REASON.fullmatch(self.reason_code):
            raise ValueError("verification reason_code must be sanitized")


CommandRunner = Callable[..., object]
PackVerifier = Callable[[RuntimePackManifest, Path], PackVerification]


def _subprocess_runner(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=False, **kwargs)


class PrivateEnvironmentBuilder:
    def __init__(
        self,
        *,
        interpreter: str | Path,
        command_runner: CommandRunner = _subprocess_runner,
        platform_name: str | None = None,
    ) -> None:
        self.interpreter = Path(interpreter)
        self._command_runner = command_runner
        self._platform_name = platform_name

    @staticmethod
    def _validate_identity(value: str) -> None:
        if not _IDENTITY.fullmatch(value):
            raise EnvironmentBuildError("environment-identity-invalid")

    def _run(self, command: list[str]) -> None:
        try:
            result = self._command_runner(
                command,
                timeout=900,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            raise EnvironmentBuildError("environment-command-failed") from None
        return_code = result if isinstance(result, int) else getattr(result, "returncode", 1)
        if return_code != 0:
            raise EnvironmentBuildError("environment-command-failed")

    def build(
        self,
        *,
        root: str | Path,
        pack_id: str,
        version: str,
        requirements_lock: str | Path | None,
    ) -> Path:
        self._validate_identity(pack_id)
        self._validate_identity(version)
        root_path = Path(root).resolve(strict=False)
        environment = root_path / pack_id / version / "venv"
        environment.parent.mkdir(parents=True, exist_ok=True)
        self._run([str(self.interpreter), "-m", "venv", str(environment)])
        platform_name = (self._platform_name or ("windows" if os.name == "nt" else "posix")).casefold()
        environment_python = environment / ("Scripts/python.exe" if platform_name == "windows" else "bin/python")
        if requirements_lock is not None:
            lock_path = Path(requirements_lock).resolve(strict=True)
            self._run(
                [
                    str(environment_python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    "--require-hashes",
                    "--no-deps",
                    "-r",
                    str(lock_path),
                ]
            )
        return environment


class PackInstaller:
    def __init__(
        self,
        *,
        registry: RuntimePackRegistry,
        install_root: str | Path,
        acquirer: ArtifactAcquirer | None,
        verifier: PackVerifier,
        environment_builder: PrivateEnvironmentBuilder | None = None,
        requirements_locks: dict[str, Path] | None = None,
    ) -> None:
        self.registry = registry
        self.install_root = Path(install_root).resolve(strict=False)
        self.acquirer = acquirer
        self.verifier = verifier
        self.environment_builder = environment_builder
        self.requirements_locks = dict(requirements_locks or {})

    @staticmethod
    def _install_ref(manifest: RuntimePackManifest) -> str:
        return f"packs/{manifest.pack_id}/{manifest.version}"

    def _install_path(self, manifest: RuntimePackManifest) -> Path:
        return self.install_root / "packs" / manifest.pack_id / manifest.version

    @staticmethod
    def _artifact_name(url: str, index: int) -> str:
        name = Path(urlsplit(url).path).name
        return name if index == 0 else f"{index}-{name}"

    def _quarantine(self, manifest: RuntimePackManifest, reason_code: str) -> None:
        try:
            record = self.registry.get(manifest.pack_id, manifest.version)
            if record.state in {
                PackLifecycleState.DOWNLOADING,
                PackLifecycleState.STAGED,
                PackLifecycleState.VERIFYING,
                PackLifecycleState.ACTIVE,
                PackLifecycleState.DEGRADED,
            }:
                self.registry.transition(
                    manifest.pack_id,
                    manifest.version,
                    PackLifecycleState.QUARANTINED,
                    reason_code=reason_code,
                )
        except RegistryError:
            pass

    def install(self, manifest: RuntimePackManifest, *, consent: bool) -> RuntimePackRecord:
        if manifest.artifacts and not consent:
            raise PackInstallError("pack-download-consent-required")
        if manifest.artifacts and self.acquirer is None:
            raise PackInstallError("pack-acquirer-unavailable")

        self.registry.register_manifest(manifest)
        self.registry.transition(manifest.pack_id, manifest.version, PackLifecycleState.DOWNLOADING)
        install_path = self._install_path(manifest)
        artifact_root = install_path / "artifacts"
        try:
            artifact_root.mkdir(parents=True, exist_ok=True)
            for index, descriptor in enumerate(manifest.artifacts):
                assert self.acquirer is not None
                acquired = self.acquirer.acquire(
                    descriptor,
                    artifact_name=self._artifact_name(descriptor.url, index),
                )
                shutil.copyfile(acquired.path, artifact_root / acquired.path.name)
            if manifest.pack_type == PackType.PYTHON_WORKER:
                if self.environment_builder is None:
                    raise PackInstallError("environment-builder-unavailable")
                self.environment_builder.build(
                    root=self.install_root / "environments",
                    pack_id=manifest.pack_id,
                    version=manifest.version,
                    requirements_lock=self.requirements_locks.get(manifest.pack_id),
                )
            self.registry.transition(
                manifest.pack_id,
                manifest.version,
                PackLifecycleState.STAGED,
                install_ref=self._install_ref(manifest),
            )
            self.registry.transition(manifest.pack_id, manifest.version, PackLifecycleState.VERIFYING)
            verification = self.verifier(manifest, install_path)
            if not verification.health_passed or not verification.self_test_passed:
                self._quarantine(manifest, verification.reason_code)
                raise PackInstallError(verification.reason_code)
            return self.registry.activate(manifest.pack_id, manifest.version)
        except PackInstallError:
            raise
        except AcquisitionError as error:
            self._quarantine(manifest, error.reason_code)
            raise PackInstallError(error.reason_code) from None
        except EnvironmentBuildError as error:
            self._quarantine(manifest, error.reason_code)
            raise PackInstallError(error.reason_code) from None
        except RegistryError as error:
            raise PackInstallError(error.reason_code) from None
        except Exception:
            self._quarantine(manifest, "pack-install-failed")
            raise PackInstallError("pack-install-failed") from None

    def repair(self, pack_id: str, version: str) -> RuntimePackRecord:
        record = self.registry.get(pack_id, version)
        if record.state != PackLifecycleState.QUARANTINED or record.install_ref is None:
            raise PackInstallError("pack-repair-unavailable")
        self.registry.transition(pack_id, version, PackLifecycleState.STAGED)
        self.registry.transition(pack_id, version, PackLifecycleState.VERIFYING)
        verification = self.verifier(record.manifest, self.install_root / record.install_ref)
        if not verification.health_passed or not verification.self_test_passed:
            self._quarantine(record.manifest, verification.reason_code)
            raise PackInstallError(verification.reason_code)
        return self.registry.activate(pack_id, version)

    def uninstall(self, pack_id: str, version: str) -> RuntimePackRecord:
        record = self.registry.get(pack_id, version)
        if record.state in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
            record = self.registry.transition(
                pack_id,
                version,
                PackLifecycleState.QUARANTINED,
                reason_code="pack-uninstall-requested",
            )
        if record.state not in {
            PackLifecycleState.AVAILABLE,
            PackLifecycleState.QUARANTINED,
            PackLifecycleState.ROLLBACK_AVAILABLE,
        }:
            raise PackInstallError("pack-uninstall-unavailable")
        install_ref = record.install_ref
        removed = self.registry.transition(pack_id, version, PackLifecycleState.REMOVED)
        if install_ref is not None:
            target = (self.install_root / install_ref).resolve(strict=False)
            if target != self.install_root and self.install_root in target.parents:
                shutil.rmtree(target, ignore_errors=True)
        return removed
