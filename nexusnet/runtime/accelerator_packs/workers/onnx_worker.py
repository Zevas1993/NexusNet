from __future__ import annotations

import importlib
import math
import os
from pathlib import Path
import sys
import time
from typing import Any
from collections.abc import Mapping

from nexusnet.runtime.accelerator_packs.protocol import (
    JsonLineCodec,
    ProtocolError,
    WorkerFrame,
    WorkerOperation,
    WorkerRequest,
)


_MAX_TENSOR_VALUES = 1_000_000
_PROVIDER_BACKENDS = {
    "CPUExecutionProvider": "cpu",
    "DmlExecutionProvider": "directml",
}


def _ort():
    return importlib.import_module("onnxruntime")


def _numpy():
    return importlib.import_module("numpy")


class OnnxKernel:
    def __init__(self) -> None:
        self.requested_provider = os.environ.get("NEXUSNET_ONNX_PROVIDER", "auto")
        self.model_root = Path(os.environ.get("NEXUSNET_MODEL_ROOT", ".")).resolve()
        self.session = None
        self.provider: str | None = None
        try:
            self._runtime = _ort()
        except Exception:
            self._runtime = None

    def _select_provider(self, ort) -> str | None:
        available = set(ort.get_available_providers())
        if self.requested_provider == "auto":
            for candidate in ("DmlExecutionProvider", "CPUExecutionProvider"):
                if candidate in available:
                    return candidate
            return None
        if self.requested_provider not in _PROVIDER_BACKENDS:
            return None
        return self.requested_provider if self.requested_provider in available else None

    def _model_path(self, model_ref: object) -> Path:
        if type(model_ref) is not str or not model_ref or len(model_ref) > 512:
            raise ValueError
        relative = Path(model_ref)
        if relative.is_absolute() or ".." in relative.parts or any(character in model_ref for character in "\r\n\x00"):
            raise ValueError
        resolved = (self.model_root / relative).resolve(strict=True)
        try:
            resolved.relative_to(self.model_root)
        except ValueError as exc:
            raise ValueError from exc
        if resolved.suffix.casefold() not in {".onnx", ".ort"}:
            raise ValueError
        return resolved

    @staticmethod
    def _execution_mode_supported(request: WorkerRequest, backend: str) -> bool:
        expected = "cpu" if backend == "cpu" else "gpu"
        return request.execution_mode.value in {"auto", expected}

    @staticmethod
    def _bounded_inputs(payload: object) -> dict[str, Any]:
        if not isinstance(payload, Mapping) or not 1 <= len(payload) <= 64:
            raise ValueError
        arrays: dict[str, Any] = {}
        count = 0
        numpy = _numpy()
        for name, values in payload.items():
            if type(name) is not str or not name or len(name) > 128 or not isinstance(values, (list, tuple)):
                raise ValueError
            count += len(values)
            if count > _MAX_TENSOR_VALUES:
                raise ValueError
            normalized = []
            for value in values:
                if type(value) not in {int, float} or not math.isfinite(float(value)):
                    raise ValueError
                normalized.append(float(value))
            arrays[name] = numpy.asarray(normalized, dtype=numpy.float32)
        return arrays

    def _load(self, ort, model_ref: object) -> dict[str, Any]:
        provider = self._select_provider(ort)
        if provider is None:
            raise RuntimeError("onnx-provider-unavailable")
        options = ort.SessionOptions()
        if provider == "DmlExecutionProvider":
            options.enable_mem_pattern = False
            options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
        path = self._model_path(model_ref)
        session = ort.InferenceSession(str(path), sess_options=options, providers=[provider])
        if provider not in session.get_providers():
            raise RuntimeError("onnx-provider-registration-failed")
        self.session = session
        self.provider = provider
        return {"loaded": True, "provider": provider, "backend": _PROVIDER_BACKENDS[provider]}

    def handle(self, request: WorkerRequest) -> tuple[dict[str, Any] | None, str | None, bool]:
        try:
            ort = self._runtime
            if ort is None:
                raise RuntimeError
            provider = self._select_provider(ort)
        except Exception:
            ort = None
            provider = None
        if request.operation == WorkerOperation.DESCRIBE:
            return {
                "worker": "nexusnet-onnx",
                "protocol_version": "1.0",
                "requested_provider": self.requested_provider,
                "execution_modes": ["cpu", "gpu"],
            }, None, False
        if request.operation == WorkerOperation.HEALTH:
            if ort is None or provider is None:
                return {
                    "available": False,
                    "backend": _PROVIDER_BACKENDS.get(self.requested_provider, "unavailable"),
                    "reason_codes": ["onnx-provider-unavailable"],
                }, None, False
            backend = _PROVIDER_BACKENDS[provider]
            if not self._execution_mode_supported(request, backend):
                return None, "execution-mode-unsupported", False
            return {
                "available": True,
                "backend": backend,
                "provider": provider,
                "provider_version": str(ort.__version__),
                "capabilities": {"onnx-inference": True},
            }, None, False
        if ort is None or provider is None:
            return None, "onnx-provider-unavailable", False
        backend = _PROVIDER_BACKENDS[provider]
        if not self._execution_mode_supported(request, backend):
            return None, "execution-mode-unsupported", False
        if request.operation == WorkerOperation.LOAD_MODEL:
            try:
                return self._load(ort, request.payload.get("model_ref")), None, False
            except ValueError:
                return None, "model-ref-invalid", False
            except RuntimeError as exc:
                return None, str(exc), False
            except Exception:
                return None, "model-load-failed", False
        if request.operation == WorkerOperation.SELF_TEST:
            try:
                self._load(ort, request.payload.get("model_ref"))
                inputs = self._bounded_inputs(request.payload.get("inputs"))
                outputs = self.session.run(None, inputs)
                actual = _json_outputs(outputs)
                expected = _plain_json(request.payload.get("expected_outputs"))
                return {"passed": actual == expected, "provider": self.provider}, None, False
            except Exception:
                return {"passed": False, "provider": provider}, None, False
        if request.operation == WorkerOperation.INFER:
            if self.session is None:
                return None, "model-not-loaded", False
            try:
                inputs = self._bounded_inputs(request.payload.get("inputs"))
                return {"outputs": _json_outputs(self.session.run(None, inputs)), "provider": self.provider}, None, False
            except (TypeError, ValueError):
                return None, "inference-payload-invalid", False
            except Exception:
                return None, "inference-failed", False
        if request.operation == WorkerOperation.UNLOAD_MODEL:
            self.session = None
            self.provider = None
            return {"unloaded": True}, None, False
        if request.operation == WorkerOperation.BENCHMARK:
            return None, "benchmark-model-required", False
        if request.operation == WorkerOperation.CANCEL:
            return None, "worker-cancel-unavailable", False
        if request.operation == WorkerOperation.SHUTDOWN:
            return {"stopped": True}, None, True
        return None, "operation-unsupported", False


def _json_outputs(outputs: object) -> list[object]:
    if not isinstance(outputs, (list, tuple)) or len(outputs) > 64:
        raise ValueError
    normalized: list[object] = []
    for output in outputs:
        value = output.tolist() if hasattr(output, "tolist") else output
        normalized.append(value)
    return normalized


def _plain_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return value


def _emit(codec: JsonLineCodec, request: WorkerRequest, payload: dict[str, Any] | None, reason: str | None) -> None:
    frame = WorkerFrame(
        request_id=request.request_id,
        event="error" if reason else "result",
        sequence=0,
        terminal=True,
        payload={} if payload is None else payload,
        reason_code=reason,
    )
    sys.stdout.buffer.write(codec.encode(frame))
    sys.stdout.buffer.flush()


def main() -> int:
    codec = JsonLineCodec()
    kernel = OnnxKernel()
    for raw in sys.stdin.buffer:
        try:
            request = codec.decode_request(raw)
        except ProtocolError:
            return 2
        if request.deadline_unix_ms < int(time.time() * 1000):
            _emit(codec, request, None, "worker-deadline-expired")
            continue
        try:
            payload, reason, stop = kernel.handle(request)
        except Exception:
            payload, reason, stop = None, "worker-operation-failed", False
        _emit(codec, request, payload, reason)
        if stop:
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
