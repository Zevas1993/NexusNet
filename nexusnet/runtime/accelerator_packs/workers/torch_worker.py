from __future__ import annotations

import importlib
import math
import os
import sys
import time
from typing import Any

from nexusnet.runtime.accelerator_packs.protocol import (
    JsonLineCodec,
    ProtocolError,
    WorkerFrame,
    WorkerOperation,
    WorkerRequest,
)


_MAX_VALUES = 4096


def _torch():
    return importlib.import_module("torch")


class TorchKernel:
    def __init__(self) -> None:
        self.backend = os.environ.get("NEXUSNET_TORCH_BACKEND", "").casefold()
        self.family = os.environ.get("NEXUSNET_TORCH_FAMILY", "").casefold()
        self.model: tuple[object, object] | None = None

    def _device(self, torch):
        if not self._family_available(torch):
            raise RuntimeError("torch-family-unavailable")
        if self.backend == "cpu":
            return torch.device("cpu")
        if self.backend in {"cuda", "rocm-windows"} and torch.cuda.is_available() and torch.cuda.device_count() >= 1:
            return torch.device("cuda:0")
        if self.backend == "xpu" and torch.xpu.is_available() and torch.xpu.device_count() >= 1:
            return torch.device("xpu:0")
        raise RuntimeError("backend-unavailable")

    def _family_available(self, torch) -> bool:
        if not self.family:
            return True
        expected_family = {
            "cpu": "torch-cpu",
            "cuda": "torch-cuda",
            "xpu": "torch-xpu",
            "rocm-windows": "torch-rocm-windows",
        }.get(self.backend)
        if self.family != expected_family:
            return False
        version = str(getattr(torch, "__version__", "")).casefold()
        torch_version = getattr(torch, "version", None)
        cuda_version = getattr(torch_version, "cuda", None)
        hip_version = getattr(torch_version, "hip", None)
        if self.family == "torch-cpu":
            return "+cpu" in version and not cuda_version and not hip_version
        if self.family == "torch-cuda":
            return "+cu" in version and bool(cuda_version) and not hip_version
        if self.family == "torch-xpu":
            return "+xpu" in version and hasattr(torch, "xpu") and torch.xpu.is_available()
        return "+rocm" in version and bool(hip_version) and self.backend == "rocm-windows"

    def _synchronize(self, torch, device) -> None:
        if self.backend in {"cuda", "rocm-windows"}:
            torch.cuda.synchronize(device)
        elif self.backend == "xpu":
            torch.xpu.synchronize(device)

    @staticmethod
    def _number(value: object) -> float:
        if type(value) not in {int, float}:
            raise ValueError
        result = float(value)
        if not math.isfinite(result) or abs(result) > 1e12:
            raise ValueError
        return result

    @classmethod
    def _values(cls, value: object) -> list[float]:
        if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= _MAX_VALUES:
            raise ValueError
        return [cls._number(item) for item in value]

    def handle(self, request: WorkerRequest) -> tuple[dict[str, Any] | None, str | None, bool]:
        if self.backend not in {"cpu", "cuda", "xpu", "rocm-windows"}:
            return None, "torch-backend-invalid", False
        try:
            torch = _torch()
            device = self._device(torch)
        except Exception:
            if request.operation == WorkerOperation.HEALTH:
                return {
                    "available": False,
                    "backend": self.backend,
                    "device_count": 0,
                    "capabilities": {},
                    "reason_codes": ["torch-family-unavailable" if self.family else "torch-backend-unavailable"],
                }, None, False
            return None, "torch-backend-unavailable", False

        if request.operation == WorkerOperation.DESCRIBE:
            return {
                "worker": "nexusnet-torch",
                "backend": self.backend,
                "distribution_family": self.family or "legacy-unpinned",
                "protocol_version": "1.0",
                "execution_modes": ["cpu" if self.backend == "cpu" else "gpu"],
            }, None, False
        if request.operation == WorkerOperation.HEALTH:
            return {
                "available": True,
                "backend": self.backend,
                "distribution_family": self.family or "legacy-unpinned",
                "device_count": (
                    1
                    if self.backend == "cpu"
                    else int(torch.xpu.device_count())
                    if self.backend == "xpu"
                    else int(torch.cuda.device_count())
                ),
                "capabilities": {"numeric-model": True, "tensor-execution": True},
            }, None, False
        expected_mode = "cpu" if self.backend == "cpu" else "gpu"
        if request.execution_mode.value not in {"auto", expected_mode}:
            return None, "execution-mode-unsupported", False
        if request.operation == WorkerOperation.SELF_TEST:
            values = torch.tensor([1.0, 2.0], dtype=torch.float32, device=device)
            output = values * 2.0 + 1.0
            self._synchronize(torch, device)
            passed = output.detach().cpu().tolist() == [3.0, 5.0]
            return {"passed": passed, "backend": self.backend}, None, False
        if request.operation == WorkerOperation.LOAD_MODEL:
            try:
                scale = self._number(request.payload.get("scale"))
                bias = self._number(request.payload.get("bias"))
            except (TypeError, ValueError):
                return None, "model-payload-invalid", False
            self.model = (
                torch.tensor(scale, dtype=torch.float32, device=device),
                torch.tensor(bias, dtype=torch.float32, device=device),
            )
            return {"loaded": True, "backend": self.backend}, None, False
        if request.operation == WorkerOperation.INFER:
            if self.model is None:
                return None, "model-not-loaded", False
            try:
                values = self._values(request.payload.get("values"))
            except (TypeError, ValueError):
                return None, "inference-payload-invalid", False
            tensor = torch.tensor(values, dtype=torch.float32, device=device)
            output = tensor * self.model[0] + self.model[1]
            self._synchronize(torch, device)
            return {"values": output.detach().cpu().tolist(), "backend": self.backend}, None, False
        if request.operation == WorkerOperation.BENCHMARK:
            try:
                iterations = int(request.payload.get("iterations", 16))
                if type(request.payload.get("iterations", 16)) is bool or not 1 <= iterations <= 10_000:
                    raise ValueError
            except (TypeError, ValueError, OverflowError):
                return None, "benchmark-payload-invalid", False
            tensor = torch.arange(1024, dtype=torch.float32, device=device)
            started = time.perf_counter()
            output = tensor
            for _ in range(iterations):
                output = output * 1.0001 + 0.0001
            self._synchronize(torch, device)
            duration_ms = max((time.perf_counter() - started) * 1000.0, 1e-9)
            return {
                "iterations": iterations,
                "duration_ms": duration_ms,
                "checksum": float(output[0].detach().cpu().item()),
                "backend": self.backend,
            }, None, False
        if request.operation == WorkerOperation.UNLOAD_MODEL:
            self.model = None
            if self.backend in {"cuda", "rocm-windows"}:
                torch.cuda.empty_cache()
            elif self.backend == "xpu":
                torch.xpu.empty_cache()
            return {"unloaded": True}, None, False
        if request.operation == WorkerOperation.CANCEL:
            return None, "worker-cancel-unavailable", False
        if request.operation == WorkerOperation.SHUTDOWN:
            return {"stopped": True}, None, True
        return None, "operation-unsupported", False


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
    kernel = TorchKernel()
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
