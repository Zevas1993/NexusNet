from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from nexusnet.runtime.accelerator_packs.acquisition import AcquisitionPolicy, ArtifactAcquirer
from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, RuntimePackManifest
from nexusnet.runtime.accelerator_packs.installer import PackInstallError, PackInstaller, PackVerification, PrivateEnvironmentBuilder
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.registry import RegistryError, RuntimePackRegistry
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError
from nexusnet.runtime.evolutionary_inference.hardware import HardwareCapabilityDiscoverer


_IDENTITY = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_REASON = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_COMMAND_REASONS = {
    "install": "pack-installed",
    "repair": "pack-repaired",
    "rollback": "pack-rolled-back",
    "uninstall": "pack-uninstalled",
}


class RuntimePackCliError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nexusnet-runtime-packs")
    parser.add_argument("command", choices=("status", "plan", "install", "repair", "rollback", "uninstall"))
    parser.add_argument("--home", type=Path, default=Path.home() / ".nexusnet")
    parser.add_argument("--pack-id")
    parser.add_argument("--version")
    parser.add_argument("--consent", action="store_true")
    parser.add_argument("--reason-code", default="operator-requested")
    return parser


def _print(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


def _validate_identity(value: str | None, *, version: bool = False) -> str:
    if value is None or not _IDENTITY.fullmatch(value):
        raise RuntimePackCliError("pack-version-required" if version else "pack-id-required")
    return value


def _validate_reason(value: str) -> str:
    if not _REASON.fullmatch(value):
        raise RuntimePackCliError("reason-code-invalid")
    return value


def _discover_candidates() -> tuple[object, ...]:
    try:
        graph = HardwareCapabilityDiscoverer().discover()
        return tuple(BuiltInPackCatalog().candidates(graph))
    except Exception:
        raise RuntimePackCliError("hardware-discovery-failed") from None


def _candidate_manifest(pack_id: str, version: str) -> RuntimePackManifest:
    matches = [
        candidate.manifest
        for candidate in _discover_candidates()
        if candidate.manifest.pack_id == pack_id and candidate.manifest.version == version
    ]
    if not matches:
        raise RuntimePackCliError("pack-candidate-unavailable")
    manifest = matches[0]
    if any(candidate != manifest for candidate in matches[1:]):
        raise RuntimePackCliError("pack-candidate-ambiguous")
    return manifest


def _pack_environment(manifest: RuntimePackManifest, install_root: Path) -> tuple[Path, dict[str, str]]:
    lock_id = manifest.dependency_constraints.get("environment_lock_id")
    interpreter = Path(sys.executable)
    environment: dict[str, str] = {}
    if lock_id is not None:
        interpreter = (
            install_root
            / "environments"
            / manifest.pack_id
            / manifest.version
            / "venv"
            / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        )
        family_by_lock = {
            "torch-cpu": ("cpu", "torch-cpu"),
            "torch-cuda": ("cuda", "torch-cuda"),
            "torch-xpu": ("xpu", "torch-xpu"),
            "torch-rocm-windows": ("rocm-windows", "torch-rocm-windows"),
        }
        family = next((value for prefix, value in family_by_lock.items() if lock_id.startswith(prefix)), None)
        if family is None:
            raise RuntimePackCliError("environment-lock-family-unsupported")
        environment = {
            "NEXUSNET_TORCH_BACKEND": family[0],
            "NEXUSNET_TORCH_FAMILY": family[1],
        }
    elif "onnx_worker" in manifest.launch.command:
        provider = "DmlExecutionProvider" if "directml" in manifest.accelerator_apis else "CPUExecutionProvider"
        model_root = install_root / "models" / manifest.pack_id / manifest.version
        model_root.mkdir(parents=True, exist_ok=True)
        environment = {
            "NEXUSNET_MODEL_ROOT": str(model_root),
            "NEXUSNET_ONNX_PROVIDER": provider,
        }
    elif "native_worker" in manifest.launch.command:
        raise RuntimePackCliError("native-executable-unavailable")
    return interpreter, environment


def _terminal_reason(frames: list[object], *, default: str) -> str:
    if not frames:
        return default
    terminal = frames[-1]
    reason = getattr(terminal, "reason_code", None)
    if isinstance(reason, str) and _REASON.fullmatch(reason):
        return reason
    payload = getattr(terminal, "payload", {})
    reasons = payload.get("reason_codes", ()) if hasattr(payload, "get") else ()
    if isinstance(reasons, (list, tuple)) and reasons:
        first = reasons[0]
        if isinstance(first, str) and _REASON.fullmatch(first):
            return first
    return default


def _verification_request(
    supervisor: WorkerSupervisor,
    operation: WorkerOperation,
    *,
    mode: ExecutionMode,
    timeout_s: float,
) -> list[object]:
    return supervisor.request(
        operation,
        sanitized_model_ref="model::pack-verification",
        execution_mode=mode,
        policy_receipt_ref="receipt::pack-verification",
        timeout_s=timeout_s,
    )


def _verify_pack(manifest: RuntimePackManifest, install_root: Path) -> PackVerification:
    try:
        interpreter, environment = _pack_environment(manifest, install_root)
        declared = list(manifest.launch.command)
        if not declared or declared[0] != "python":
            return PackVerification(False, False, "worker-launch-token-unsupported")
        supervisor = WorkerSupervisor(
            command=[str(interpreter), *declared[1:]],
            working_directory=Path(__file__).resolve().parents[2],
            environment=environment,
            request_timeout_s=max(manifest.self_test_probe.timeout_ms / 1000.0, 1.0),
        )
    except RuntimePackCliError as error:
        return PackVerification(False, False, error.reason_code)
    except Exception:
        return PackVerification(False, False, "worker-verification-setup-failed")

    mode = manifest.execution_modes[0]
    try:
        health = _verification_request(
            supervisor,
            WorkerOperation.HEALTH,
            mode=mode,
            timeout_s=manifest.health_probe.timeout_ms / 1000.0,
        )
        health_terminal = health[-1] if health else None
        health_payload = getattr(health_terminal, "payload", {})
        health_passed = (
            getattr(health_terminal, "event", None) == "result"
            and hasattr(health_payload, "get")
            and health_payload.get("available") is True
        )
        if not health_passed:
            return PackVerification(False, False, _terminal_reason(health, default="worker-health-failed"))

        self_test = _verification_request(
            supervisor,
            WorkerOperation.SELF_TEST,
            mode=mode,
            timeout_s=manifest.self_test_probe.timeout_ms / 1000.0,
        )
        self_test_terminal = self_test[-1] if self_test else None
        self_test_payload = getattr(self_test_terminal, "payload", {})
        self_test_passed = (
            getattr(self_test_terminal, "event", None) == "result"
            and hasattr(self_test_payload, "get")
            and self_test_payload.get("passed") is True
        )
        if not self_test_passed:
            return PackVerification(True, False, _terminal_reason(self_test, default="worker-self-test-failed"))
        return PackVerification(True, True, "pack-verified")
    except WorkerSupervisorError as error:
        reason = error.reason_code if _REASON.fullmatch(error.reason_code) else "worker-verification-failed"
        return PackVerification(False, False, reason)
    except Exception:
        return PackVerification(False, False, "worker-verification-failed")
    finally:
        supervisor.stop()


def _create_installer(home: Path, registry: RuntimePackRegistry, manifest: RuntimePackManifest | None = None) -> PackInstaller:
    install_root = (home / "runtime-packs").resolve(strict=False)
    acquirer = None
    if manifest is not None and manifest.artifacts:
        allowed_hosts = frozenset(
            host
            for descriptor in manifest.artifacts
            if (host := (urlsplit(descriptor.url).hostname or "").casefold())
        )
        acquirer = ArtifactAcquirer(
            root=install_root / "downloads" / manifest.pack_id / manifest.version,
            policy=AcquisitionPolicy(allowed_hosts=allowed_hosts),
        )
    return PackInstaller(
        registry=registry,
        install_root=install_root,
        acquirer=acquirer,
        verifier=lambda selected, _pack_root: _verify_pack(selected, install_root),
        environment_builder=PrivateEnvironmentBuilder(interpreter=sys.executable),
        environment_lock_root=install_root / "environment-locks",
    )


def _success_payload(command: str, record: object) -> dict[str, object]:
    manifest = record.manifest
    state = record.state.value if hasattr(record.state, "value") else str(record.state)
    return {
        "command": command,
        "outcome": "passed",
        "pack_id": manifest.pack_id,
        "pack_version": manifest.version,
        "reason_codes": [_COMMAND_REASONS[command]],
        "state": state,
    }


def _plan_payload() -> dict[str, object]:
    projected: dict[tuple[str, str], dict[str, object]] = {}
    for candidate in _discover_candidates():
        key = (candidate.manifest.pack_id, candidate.manifest.version)
        projected.setdefault(
            key,
            {
                "pack_id": candidate.manifest.pack_id,
                "pack_version": candidate.manifest.version,
                "reason_codes": sorted(set(candidate.reason_codes)),
                "verification_state": candidate.verification_state,
            },
        )
    candidates = [projected[key] for key in sorted(projected)]
    return {
        "candidate_count": len(candidates),
        "candidates": candidates,
        "command": "plan",
        "downloads_require_consent": True,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            _print(_plan_payload())
            return 0
        if args.command == "install" and not args.consent:
            raise RuntimePackCliError("pack-download-consent-required")
        registry = RuntimePackRegistry(args.home / "runtime-packs" / "registry.json")
        if args.command == "status":
            snapshot = registry.snapshot()
            _print(
                {
                    "command": args.command,
                    "pack_count": len(snapshot.records),
                    "active_pack_ids": sorted(snapshot.active_versions),
                    "downloads_require_consent": True,
                }
            )
            return 0
        pack_id = _validate_identity(args.pack_id)
        if args.command == "install":
            version = _validate_identity(args.version, version=True)
            manifest = _candidate_manifest(pack_id, version)
            record = _create_installer(args.home, registry, manifest).install(manifest, consent=True)
        elif args.command == "repair":
            version = _validate_identity(args.version, version=True)
            record = _create_installer(args.home, registry).repair(pack_id, version)
        elif args.command == "rollback":
            record = _create_installer(args.home, registry).rollback(
                pack_id,
                reason_code=_validate_reason(args.reason_code),
            )
        else:
            version = _validate_identity(args.version, version=True)
            record = _create_installer(args.home, registry).uninstall(pack_id, version)
        _print(_success_payload(args.command, record))
        return 0
    except (RuntimePackCliError, PackInstallError, RegistryError) as error:
        reason_code = error.reason_code if _REASON.fullmatch(error.reason_code) else "runtime-pack-command-failed"
    except Exception:
        reason_code = "runtime-pack-command-failed"
    _print({"command": args.command, "outcome": "failed", "reason_codes": [reason_code]})
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
