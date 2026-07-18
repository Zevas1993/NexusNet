from __future__ import annotations

import math
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


class ReferenceKernel:
    backend = "cpu"

    def __init__(self) -> None:
        self.model: tuple[float, float] | None = None

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
        if request.operation == WorkerOperation.DESCRIBE:
            return {
                "worker": "nexusnet-reference",
                "backend": self.backend,
                "protocol_version": "1.0",
                "execution_modes": ["cpu"],
            }, None, False
        if request.operation == WorkerOperation.HEALTH:
            return {
                "available": True,
                "backend": self.backend,
                "capabilities": {"numeric-model": True},
            }, None, False
        if request.execution_mode.value not in {"auto", "cpu"}:
            return None, "execution-mode-unsupported", False
        if request.operation == WorkerOperation.SELF_TEST:
            return {"passed": [1.0 * 2.0 + 1.0, 2.0 * 2.0 + 1.0] == [3.0, 5.0]}, None, False
        if request.operation == WorkerOperation.LOAD_MODEL:
            try:
                self.model = (self._number(request.payload.get("scale")), self._number(request.payload.get("bias")))
            except (TypeError, ValueError):
                return None, "model-payload-invalid", False
            return {"loaded": True, "backend": self.backend}, None, False
        if request.operation == WorkerOperation.INFER:
            if self.model is None:
                return None, "model-not-loaded", False
            try:
                values = self._values(request.payload.get("values"))
            except (TypeError, ValueError):
                return None, "inference-payload-invalid", False
            scale, bias = self.model
            return {"values": [value * scale + bias for value in values], "backend": self.backend}, None, False
        if request.operation == WorkerOperation.BENCHMARK:
            try:
                iterations = int(request.payload.get("iterations", 16))
                if type(request.payload.get("iterations", 16)) is bool or not 1 <= iterations <= 10_000:
                    raise ValueError
            except (TypeError, ValueError, OverflowError):
                return None, "benchmark-payload-invalid", False
            started = time.perf_counter()
            accumulator = 0.0
            for index in range(iterations):
                accumulator += index * 2.0 + 1.0
            duration_ms = max((time.perf_counter() - started) * 1000.0, 1e-9)
            return {"iterations": iterations, "duration_ms": duration_ms, "checksum": accumulator}, None, False
        if request.operation == WorkerOperation.UNLOAD_MODEL:
            self.model = None
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
    kernel = ReferenceKernel()
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
