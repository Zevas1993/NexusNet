from __future__ import annotations

import importlib
from pathlib import Path
import subprocess
import sys
import time

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation, WorkerRequest


class _Input:
    name = "values"


class _SessionOptions:
    def __init__(self):
        self.enable_mem_pattern = True
        self.execution_mode = None
        self.config_entries = {}

    def add_session_config_entry(self, name, value):
        self.config_entries[name] = value


class _Session:
    def __init__(self, path, *, sess_options, providers):
        self.path = path
        self.options = sess_options
        self.providers = list(providers)

    def get_providers(self):
        return self.providers

    def get_inputs(self):
        return [_Input()]

    def run(self, output_names, inputs):
        values = inputs["values"]
        return [[float(value) * 2.0 + 1.0 for value in values]]


class _FakeOrt:
    __version__ = "1.24.0"
    SessionOptions = _SessionOptions
    InferenceSession = _Session

    class ExecutionMode:
        ORT_SEQUENTIAL = "sequential"

    def __init__(self, providers):
        self.providers = providers

    def get_available_providers(self):
        return list(self.providers)


def _request(operation: WorkerOperation, *, mode: ExecutionMode, payload: dict | None = None) -> WorkerRequest:
    return WorkerRequest(
        request_id=f"req::{operation.value}",
        operation=operation,
        deadline_unix_ms=int(time.time() * 1000) + 30_000,
        sanitized_model_ref="model::onnx-self-test",
        execution_mode=mode,
        policy_receipt_ref="receipt::onnx-test",
        payload=payload or {},
    )


def _kernel(monkeypatch, tmp_path: Path, *, provider: str, available: list[str]):
    module = importlib.import_module("nexusnet.runtime.accelerator_packs.workers.onnx_worker")
    monkeypatch.setenv("NEXUSNET_ONNX_PROVIDER", provider)
    monkeypatch.setenv("NEXUSNET_MODEL_ROOT", str(tmp_path))
    monkeypatch.setattr(module, "_ort", lambda: _FakeOrt(available))
    return module.OnnxKernel()


def test_importing_onnx_worker_does_not_import_onnxruntime_into_core() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import nexusnet.runtime.accelerator_packs.workers.onnx_worker; "
                "print('onnxruntime' in sys.modules)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "False"


def test_onnx_worker_selects_explicit_directml_and_reports_version(monkeypatch, tmp_path: Path) -> None:
    kernel = _kernel(
        monkeypatch,
        tmp_path,
        provider="DmlExecutionProvider",
        available=["CPUExecutionProvider", "DmlExecutionProvider"],
    )

    health, reason, _ = kernel.handle(_request(WorkerOperation.HEALTH, mode=ExecutionMode.GPU))

    assert reason is None
    assert health == {
        "available": True,
        "backend": "directml",
        "provider": "DmlExecutionProvider",
        "provider_version": "1.24.0",
        "capabilities": {"onnx-inference": True},
    }


def test_forced_directml_does_not_fall_back_to_cpu(monkeypatch, tmp_path: Path) -> None:
    kernel = _kernel(
        monkeypatch,
        tmp_path,
        provider="DmlExecutionProvider",
        available=["CPUExecutionProvider"],
    )

    health, reason, _ = kernel.handle(_request(WorkerOperation.HEALTH, mode=ExecutionMode.GPU))

    assert reason is None
    assert health["available"] is False
    assert health["reason_codes"] == ["onnx-provider-unavailable"]


def test_auto_provider_uses_directml_then_cpu(monkeypatch, tmp_path: Path) -> None:
    accelerated = _kernel(
        monkeypatch,
        tmp_path,
        provider="auto",
        available=["CPUExecutionProvider", "DmlExecutionProvider"],
    )
    cpu = _kernel(monkeypatch, tmp_path, provider="auto", available=["CPUExecutionProvider"])

    accelerated_health, _, _ = accelerated.handle(_request(WorkerOperation.HEALTH, mode=ExecutionMode.AUTO))
    cpu_health, _, _ = cpu.handle(_request(WorkerOperation.HEALTH, mode=ExecutionMode.AUTO))

    assert accelerated_health["provider"] == "DmlExecutionProvider"
    assert cpu_health["provider"] == "CPUExecutionProvider"
    assert cpu_health["backend"] == "cpu"


def test_onnx_worker_loads_and_executes_model_with_selected_provider(monkeypatch, tmp_path: Path) -> None:
    model = tmp_path / "self-test.onnx"
    model.write_bytes(b"bounded-test-model")
    kernel = _kernel(monkeypatch, tmp_path, provider="DmlExecutionProvider", available=["DmlExecutionProvider"])

    loaded, load_reason, _ = kernel.handle(
        _request(
            WorkerOperation.LOAD_MODEL,
            mode=ExecutionMode.GPU,
            payload={"model_ref": "self-test.onnx"},
        )
    )
    inferred, infer_reason, _ = kernel.handle(
        _request(
            WorkerOperation.INFER,
            mode=ExecutionMode.GPU,
            payload={"inputs": {"values": [1.0, 2.0]}},
        )
    )

    assert load_reason is None
    assert loaded["loaded"] is True
    assert loaded["provider"] == "DmlExecutionProvider"
    assert infer_reason is None
    assert inferred["outputs"] == [[3.0, 5.0]]
    assert kernel.session.options.enable_mem_pattern is False
    assert kernel.session.options.execution_mode == "sequential"
    assert kernel.session.options.config_entries == {"session.disable_cpu_ep_fallback": "1"}


def test_onnx_worker_self_test_requires_real_provider_execution(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "self-test.onnx").write_bytes(b"bounded-test-model")
    kernel = _kernel(monkeypatch, tmp_path, provider="CPUExecutionProvider", available=["CPUExecutionProvider"])

    payload, reason, _ = kernel.handle(
        _request(
            WorkerOperation.SELF_TEST,
            mode=ExecutionMode.CPU,
            payload={
                "model_ref": "self-test.onnx",
                "inputs": {"values": [1.0, 2.0]},
                "expected_outputs": [[3.0, 5.0]],
            },
        )
    )

    assert reason is None
    assert payload == {"passed": True, "provider": "CPUExecutionProvider"}


def test_onnx_worker_confines_model_refs_to_owned_root(monkeypatch, tmp_path: Path) -> None:
    kernel = _kernel(monkeypatch, tmp_path, provider="CPUExecutionProvider", available=["CPUExecutionProvider"])

    payload, reason, _ = kernel.handle(
        _request(
            WorkerOperation.LOAD_MODEL,
            mode=ExecutionMode.CPU,
            payload={"model_ref": "../secret.onnx"},
        )
    )

    assert payload is None
    assert reason == "model-ref-invalid"
