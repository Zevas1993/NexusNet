from __future__ import annotations

import importlib
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation, WorkerRequest


def test_worker_module_import_does_not_load_coordinator_http_dependencies() -> None:
    script = """
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name == 'requests' or name.startswith('nexus.runtimes'):
        raise RuntimeError('coordinator-dependency-loaded')
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from nexusnet.runtime.accelerator_packs.workers.torch_worker import TorchKernel
assert TorchKernel is not None
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


class _DeviceApi:
    def __init__(self, *, available: bool, count: int = 1):
        self._available = available
        self._count = count

    def is_available(self):
        return self._available

    def device_count(self):
        return self._count

    def synchronize(self, device=None):
        return None

    def empty_cache(self):
        return None


class _FakeTorch:
    def __init__(
        self,
        *,
        version: str,
        cuda_version: str | None = None,
        hip_version: str | None = None,
        cuda_available: bool = False,
        xpu_available: bool = False,
    ):
        self.__version__ = version
        self.version = SimpleNamespace(cuda=cuda_version, hip=hip_version)
        self.cuda = _DeviceApi(available=cuda_available)
        self.xpu = _DeviceApi(available=xpu_available)

    @staticmethod
    def device(value: str):
        return value


def _request(mode: ExecutionMode) -> WorkerRequest:
    return WorkerRequest(
        request_id="req::family-health",
        operation=WorkerOperation.HEALTH,
        deadline_unix_ms=int(time.time() * 1000) + 30_000,
        sanitized_model_ref="model::family",
        execution_mode=mode,
        policy_receipt_ref="receipt::family",
    )


def _health(monkeypatch, *, backend: str, family: str, torch: _FakeTorch, mode: ExecutionMode):
    module = importlib.import_module("nexusnet.runtime.accelerator_packs.workers.torch_worker")
    monkeypatch.setenv("NEXUSNET_TORCH_BACKEND", backend)
    monkeypatch.setenv("NEXUSNET_TORCH_FAMILY", family)
    monkeypatch.setattr(module, "_torch", lambda: torch)
    return module.TorchKernel().handle(_request(mode))


@pytest.mark.parametrize(
    ("backend", "family", "torch", "mode", "expected_backend"),
    [
        ("cpu", "torch-cpu", _FakeTorch(version="2.11.0+cpu"), ExecutionMode.CPU, "cpu"),
        (
            "cuda",
            "torch-cuda",
            _FakeTorch(version="2.11.0+cu128", cuda_version="12.8", cuda_available=True),
            ExecutionMode.GPU,
            "cuda",
        ),
        (
            "xpu",
            "torch-xpu",
            _FakeTorch(version="2.10.0+xpu", xpu_available=True),
            ExecutionMode.GPU,
            "xpu",
        ),
        (
            "rocm-windows",
            "torch-rocm-windows",
            _FakeTorch(version="2.9.1+rocm7.2.1", hip_version="7.2.1", cuda_available=True),
            ExecutionMode.GPU,
            "rocm-windows",
        ),
    ],
)
def test_torch_worker_family_handshake_accepts_matching_distribution(
    monkeypatch, backend: str, family: str, torch: _FakeTorch, mode: ExecutionMode, expected_backend: str
) -> None:
    payload, reason, _ = _health(
        monkeypatch,
        backend=backend,
        family=family,
        torch=torch,
        mode=mode,
    )

    assert reason is None
    assert payload["available"] is True
    assert payload["backend"] == expected_backend
    assert payload["distribution_family"] == family


@pytest.mark.parametrize(
    ("backend", "family", "torch"),
    [
        ("cuda", "torch-cuda", _FakeTorch(version="2.9.1+rocm7.2.1", hip_version="7.2.1", cuda_available=True)),
        ("rocm-windows", "torch-rocm-windows", _FakeTorch(version="2.11.0+cu128", cuda_version="12.8", cuda_available=True)),
        ("xpu", "torch-xpu", _FakeTorch(version="2.10.0+xpu", xpu_available=False)),
        ("cpu", "torch-cuda", _FakeTorch(version="2.11.0+cpu")),
    ],
)
def test_torch_worker_rejects_wrong_or_unavailable_family(monkeypatch, backend: str, family: str, torch: _FakeTorch) -> None:
    payload, reason, _ = _health(
        monkeypatch,
        backend=backend,
        family=family,
        torch=torch,
        mode=ExecutionMode.GPU if backend != "cpu" else ExecutionMode.CPU,
    )

    assert reason is None
    assert payload["available"] is False
    assert payload["reason_codes"] == ["torch-family-unavailable"]
