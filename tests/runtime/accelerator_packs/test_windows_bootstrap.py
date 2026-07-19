from pathlib import Path
import json
import subprocess
import sys
from types import SimpleNamespace

from nexusnet.cli import runtime_packs as runtime_pack_cli
from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.installer import PackInstallError, PackInstaller
from nexusnet.runtime.evolutionary_inference.hardware import HardwareCapabilityDiscoverer


def test_windows_bootstrap_builds_private_core_without_global_python_mutation():
    script = Path("install/windows/bootstrap.ps1").read_text(encoding="utf-8")

    assert "NEXUSNET_HOME" in script
    assert "private" in script.casefold()
    assert "pyproject.toml" in script
    assert "--system-site-packages" not in script
    assert "python -m venv .venv" not in script
    assert "requirements-windows.txt" not in script
    assert "$env:PATH =" not in script


def test_runtime_pack_cli_executes_when_invoked_as_a_module(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nexusnet.cli.runtime_packs",
            "status",
            "--home",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "active_pack_ids": [],
        "command": "status",
        "downloads_require_consent": True,
        "pack_count": 0,
    }


def test_hardware_discovery_import_does_not_require_optional_torch():
    script = """
import importlib.abc
import sys

class RejectTorch(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "torch" or fullname.startswith("torch."):
            raise ModuleNotFoundError("optional torch rejected by clean-core probe")
        return None

sys.meta_path.insert(0, RejectTorch())
from nexusnet.runtime.evolutionary_inference.hardware import HardwareCapabilityDiscoverer
from nexusnet.runtime.evolutionary_inference import HardwareCapabilityDiscoverer as ExportedDiscoverer
assert ExportedDiscoverer is HardwareCapabilityDiscoverer
print("clean-core-import-passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "clean-core-import-passed"


def test_runtime_pack_cli_dispatches_all_lifecycle_commands_with_sanitized_receipts(
    tmp_path,
    manifest_factory,
    monkeypatch,
    capsys,
):
    manifest = manifest_factory(artifacts=[])
    record = SimpleNamespace(manifest=manifest, state=PackLifecycleState.ACTIVE)
    calls: list[tuple[object, ...]] = []

    monkeypatch.setattr(HardwareCapabilityDiscoverer, "discover", lambda self: object())
    monkeypatch.setattr(
        BuiltInPackCatalog,
        "candidates",
        lambda self, _graph: (SimpleNamespace(manifest=manifest),),
    )
    monkeypatch.setattr(
        PackInstaller,
        "install",
        lambda self, selected, *, consent: calls.append(("install", selected, consent)) or record,
    )
    monkeypatch.setattr(
        PackInstaller,
        "repair",
        lambda self, pack_id, version: calls.append(("repair", pack_id, version)) or record,
    )
    monkeypatch.setattr(
        PackInstaller,
        "rollback",
        lambda self, pack_id, *, reason_code: calls.append(("rollback", pack_id, reason_code)) or record,
    )
    monkeypatch.setattr(
        PackInstaller,
        "uninstall",
        lambda self, pack_id, version: calls.append(("uninstall", pack_id, version)) or record,
    )

    commands = (
        (["install", "--pack-id", manifest.pack_id, "--version", manifest.version, "--consent"], "pack-installed"),
        (["repair", "--pack-id", manifest.pack_id, "--version", manifest.version], "pack-repaired"),
        (["rollback", "--pack-id", manifest.pack_id, "--reason-code", "operator-requested"], "pack-rolled-back"),
        (["uninstall", "--pack-id", manifest.pack_id, "--version", manifest.version], "pack-uninstalled"),
    )
    for command, reason_code in commands:
        assert runtime_pack_cli.main([*command, "--home", str(tmp_path)]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload == {
            "command": command[0],
            "outcome": "passed",
            "pack_id": manifest.pack_id,
            "pack_version": manifest.version,
            "reason_codes": [reason_code],
            "state": "active",
        }

    assert calls == [
        ("install", manifest, True),
        ("repair", manifest.pack_id, manifest.version),
        ("rollback", manifest.pack_id, "operator-requested"),
        ("uninstall", manifest.pack_id, manifest.version),
    ]
    assert str(tmp_path) not in capsys.readouterr().out


def test_runtime_pack_cli_requires_consent_before_install_discovery(tmp_path, monkeypatch, capsys):
    discovered = False

    def discover(_self):
        nonlocal discovered
        discovered = True
        return object()

    monkeypatch.setattr(HardwareCapabilityDiscoverer, "discover", discover)

    assert runtime_pack_cli.main(
        ["install", "--pack-id", "org.nexusnet.torch.cuda", "--version", "1.0.0", "--home", str(tmp_path)]
    ) == 2
    assert json.loads(capsys.readouterr().out) == {
        "command": "install",
        "outcome": "failed",
        "reason_codes": ["pack-download-consent-required"],
    }
    assert discovered is False


def test_runtime_pack_cli_runs_real_reference_install_and_uninstall(tmp_path):
    base_command = [
        sys.executable,
        "-m",
        "nexusnet.cli.runtime_packs",
    ]
    identity = ["--pack-id", "org.nexusnet.cpu.reference", "--version", "1.0.0"]

    installed = subprocess.run(
        [*base_command, "install", "--home", str(tmp_path), *identity, "--consent"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert installed.returncode == 0
    assert json.loads(installed.stdout)["state"] == "active"
    assert str(tmp_path) not in installed.stdout
    configuration = (
        tmp_path
        / "runtime-packs"
        / "environments"
        / "org.nexusnet.cpu.reference"
        / "1.0.0"
        / "venv"
        / "pyvenv.cfg"
    ).read_text(encoding="utf-8")
    assert "include-system-site-packages = false" in configuration.casefold()

    removed = subprocess.run(
        [*base_command, "uninstall", "--home", str(tmp_path), *identity],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert removed.returncode == 0
    assert json.loads(removed.stdout)["state"] == "removed"
    assert str(tmp_path) not in removed.stdout
    assert not (
        tmp_path / "runtime-packs" / "environments" / "org.nexusnet.cpu.reference" / "1.0.0"
    ).exists()


def test_runtime_pack_cli_sanitizes_lifecycle_failures(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        PackInstaller,
        "repair",
        lambda _self, _pack_id, _version: (_ for _ in ()).throw(PackInstallError("pack-repair-unavailable")),
    )

    assert runtime_pack_cli.main(
        [
            "repair",
            "--pack-id",
            "org.nexusnet.torch.cuda",
            "--version",
            "1.0.0",
            "--home",
            str(tmp_path),
        ]
    ) == 2
    output = capsys.readouterr().out
    assert json.loads(output) == {
        "command": "repair",
        "outcome": "failed",
        "reason_codes": ["pack-repair-unavailable"],
    }
    assert str(tmp_path) not in output


def test_runtime_pack_cli_sanitizes_corrupt_registry_failure(tmp_path, capsys):
    registry = tmp_path / "runtime-packs" / "registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"private_path":"C:/Users/example/secret"', encoding="utf-8")

    assert runtime_pack_cli.main(["status", "--home", str(tmp_path)]) == 2
    output = capsys.readouterr().out
    assert json.loads(output) == {
        "command": "status",
        "outcome": "failed",
        "reason_codes": ["registry-invalid"],
    }
    assert str(tmp_path) not in output
    assert "private_path" not in output


def test_runtime_pack_cli_verifier_launches_locked_worker_from_private_interpreter(
    tmp_path,
    manifest_factory,
    monkeypatch,
):
    manifest = manifest_factory(
        pack_type="python-worker",
        workload_kinds=["native-moe"],
        model_formats=["torch"],
        artifacts=[],
        dependency_constraints={"environment_lock_id": "torch-cuda-2.11.0-cu128-cp311-win-amd64"},
        launch={
            "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"],
            "environment_allowlist": ["NEXUSNET_TORCH_BACKEND", "NEXUSNET_TORCH_FAMILY"],
        },
        capabilities=["numeric-model", "cuda-tensor-execution"],
    )
    observed: dict[str, object] = {"operations": []}

    class FakeSupervisor:
        def __init__(self, **kwargs):
            observed.update(kwargs)

        def request(self, operation, **_kwargs):
            observed["operations"].append(operation.value)
            payload = {"available": True} if operation.value == "health" else {"passed": True}
            return [SimpleNamespace(event="result", payload=payload, reason_code=None)]

        def stop(self):
            observed["stopped"] = True

    monkeypatch.setattr(runtime_pack_cli, "WorkerSupervisor", FakeSupervisor)
    install_root = tmp_path / "runtime-packs"

    verification = runtime_pack_cli._verify_pack(manifest, install_root)

    private_python = (
        install_root
        / "environments"
        / manifest.pack_id
        / manifest.version
        / "venv"
        / "Scripts"
        / "python.exe"
    )
    assert observed["command"] == [
        str(private_python),
        "-m",
        "nexusnet.runtime.accelerator_packs.workers.torch_worker",
    ]
    assert observed["environment"] == {
        "NEXUSNET_TORCH_BACKEND": "cuda",
        "NEXUSNET_TORCH_FAMILY": "torch-cuda",
    }
    assert Path(observed["working_directory"]) == Path(runtime_pack_cli.__file__).resolve().parents[2]
    assert observed["operations"] == ["health", "self_test"]
    assert observed["stopped"] is True
    assert verification.health_passed is True
    assert verification.self_test_passed is True
    assert verification.reason_code == "pack-verified"
