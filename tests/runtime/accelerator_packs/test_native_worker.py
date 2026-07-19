from __future__ import annotations

import json
from pathlib import Path
import sys
import threading
import time

import pytest

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation, WorkerRequest
from nexusnet.runtime.accelerator_packs.workers.native_worker import (
    NativeConnectorError,
    NativeExecutableClient,
    NativeKernel,
)


class _FakeClient:
    def __init__(self, handshake: dict):
        self.handshake = handshake
        self.calls: list[tuple[str, dict]] = []
        self.cancelled = False

    def invoke(self, operation: str, payload: dict, *, timeout_ms: int) -> dict:
        self.calls.append((operation, payload))
        if operation == "describe":
            return self.handshake
        if operation == "load_model":
            return {"loaded": True}
        if operation == "infer":
            return {"text": "bounded output"}
        return {"ok": True}

    def cancel(self) -> bool:
        self.cancelled = True
        return True


def _request(operation: WorkerOperation, *, payload: dict | None = None) -> WorkerRequest:
    return WorkerRequest(
        request_id=f"req::{operation.value}",
        operation=operation,
        deadline_unix_ms=int(time.time() * 1000) + 30_000,
        sanitized_model_ref="model::native-test",
        execution_mode=ExecutionMode.GPU,
        policy_receipt_ref="receipt::native-test",
        payload=payload or {},
    )


def _kernel(client: _FakeClient) -> NativeKernel:
    return NativeKernel(
        client=client,
        declared_backend="vulkan",
        declared_device_node_id="gpu:amd",
        declared_model_formats=("gguf",),
        declared_capabilities=("llm-generate",),
    )


def test_native_connector_confines_executable_to_pack_root(tmp_path: Path) -> None:
    with pytest.raises(NativeConnectorError, match="native-executable-ref-invalid"):
        NativeExecutableClient(tmp_path / "pack", "../outside.exe")


@pytest.mark.parametrize(
    ("handshake", "reason"),
    [
        (
            {"available": True, "backend": "hip", "device_node_id": "gpu:amd", "model_formats": ["gguf"], "capabilities": ["llm-generate"]},
            "native-backend-mismatch",
        ),
        (
            {"available": True, "backend": "vulkan", "device_node_id": "gpu:other", "model_formats": ["gguf"], "capabilities": ["llm-generate"]},
            "native-device-mismatch",
        ),
        (
            {"available": True, "backend": "vulkan", "device_node_id": "gpu:amd", "model_formats": ["gguf", "onnx"], "capabilities": ["llm-generate"]},
            "native-model-format-overclaim",
        ),
        (
            {"available": True, "backend": "vulkan", "device_node_id": "gpu:amd", "model_formats": ["gguf"], "capabilities": ["llm-generate", "training"]},
            "native-capability-overclaim",
        ),
        (
            {"available": True, "backend": "vulkan", "device_node_id": "gpu:amd", "model_formats": [{}], "capabilities": ["llm-generate"]},
            "native-model-format-overclaim",
        ),
    ],
)
def test_native_worker_reconciles_handshake_against_manifest(handshake: dict, reason: str) -> None:
    payload, actual_reason, _ = _kernel(_FakeClient(handshake)).handle(_request(WorkerOperation.HEALTH))

    assert payload is None
    assert actual_reason == reason


def test_native_worker_validates_model_format_and_runs_lifecycle() -> None:
    client = _FakeClient(
        {"available": True, "backend": "vulkan", "device_node_id": "gpu:amd", "model_formats": ["gguf"], "capabilities": ["llm-generate"]}
    )
    kernel = _kernel(client)

    invalid, invalid_reason, _ = kernel.handle(
        _request(WorkerOperation.LOAD_MODEL, payload={"model_ref": "model.onnx"})
    )
    loaded, load_reason, _ = kernel.handle(
        _request(WorkerOperation.LOAD_MODEL, payload={"model_ref": "model.gguf"})
    )
    inferred, infer_reason, _ = kernel.handle(
        _request(WorkerOperation.INFER, payload={"prompt_ref": "prompt::sanitized"})
    )

    assert invalid is None
    assert invalid_reason == "native-model-format-unsupported"
    assert load_reason is None and loaded["loaded"] is True
    assert infer_reason is None and inferred["text"] == "bounded output"
    assert client.calls[-1][1]["model_ref"] == "model.gguf"


def _write_bridge(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "import json, sys, time",
                "payload = json.load(sys.stdin)",
                "mode = payload.get('payload', {}).get('mode')",
                "if mode == 'large': print(json.dumps({'data': 'x' * 2000000}))",
                "elif mode == 'sleep': time.sleep(30)",
                "else: print(json.dumps({'ok': True}))",
            ]
        ),
        encoding="utf-8",
    )


def test_native_client_bounds_output_and_honors_deadline(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge.py"
    _write_bridge(bridge)
    client = NativeExecutableClient(
        tmp_path,
        "bridge.py",
        command=(sys.executable, str(bridge)),
        max_output_bytes=1024,
    )

    with pytest.raises(NativeConnectorError, match="native-output-too-large"):
        client.invoke("infer", {"mode": "large"}, timeout_ms=5_000)
    with pytest.raises(NativeConnectorError, match="native-deadline-expired"):
        client.invoke("infer", {"mode": "sleep"}, timeout_ms=100)


def test_native_client_cancellation_terminates_inflight_process(tmp_path: Path) -> None:
    bridge = tmp_path / "bridge.py"
    _write_bridge(bridge)
    client = NativeExecutableClient(
        tmp_path,
        "bridge.py",
        command=(sys.executable, str(bridge)),
    )
    outcome: list[str] = []

    def invoke() -> None:
        try:
            client.invoke("infer", {"mode": "sleep"}, timeout_ms=10_000)
        except NativeConnectorError as exc:
            outcome.append(str(exc))

    thread = threading.Thread(target=invoke)
    thread.start()
    for _ in range(100):
        if client.active:
            break
        time.sleep(0.01)
    assert client.cancel() is True
    thread.join(timeout=5)

    assert thread.is_alive() is False
    assert outcome == ["native-operation-cancelled"]
