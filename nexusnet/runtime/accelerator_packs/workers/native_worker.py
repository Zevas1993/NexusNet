from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
import threading
import time
from typing import Any

from nexusnet.runtime.accelerator_packs.protocol import (
    JsonLineCodec,
    ProtocolError,
    WorkerFrame,
    WorkerOperation,
    WorkerRequest,
)


class NativeConnectorError(RuntimeError):
    pass


class NativeExecutableClient:
    def __init__(
        self,
        pack_root: Path,
        executable_ref: str,
        *,
        command: tuple[str, ...] | None = None,
        max_output_bytes: int = 1024 * 1024,
    ) -> None:
        self.pack_root = pack_root.resolve()
        self.executable = self._resolve_executable(executable_ref)
        if max_output_bytes < 1024 or max_output_bytes > 64 * 1024 * 1024:
            raise ValueError("native output bound is invalid")
        self.command = command or (str(self.executable),)
        if not self.command:
            raise ValueError("native command is empty")
        self.max_output_bytes = max_output_bytes
        self._lock = threading.RLock()
        self._process: subprocess.Popen[bytes] | None = None
        self._cancel_requested = False

    @property
    def active(self) -> bool:
        with self._lock:
            return self._process is not None and self._process.poll() is None

    def _resolve_executable(self, executable_ref: str) -> Path:
        if type(executable_ref) is not str or not executable_ref or len(executable_ref) > 512:
            raise NativeConnectorError("native-executable-ref-invalid")
        posix = PurePosixPath(executable_ref)
        windows = PureWindowsPath(executable_ref)
        if posix.is_absolute() or windows.is_absolute() or windows.drive or ".." in posix.parts or "\\" in executable_ref:
            raise NativeConnectorError("native-executable-ref-invalid")
        try:
            executable = (self.pack_root / posix).resolve(strict=True)
            executable.relative_to(self.pack_root)
        except (OSError, ValueError) as exc:
            raise NativeConnectorError("native-executable-ref-invalid") from exc
        if not executable.is_file():
            raise NativeConnectorError("native-executable-ref-invalid")
        return executable

    def invoke(self, operation: str, payload: dict[str, Any], *, timeout_ms: int) -> dict[str, Any]:
        if timeout_ms <= 0 or timeout_ms > 300_000:
            raise NativeConnectorError("native-deadline-invalid")
        request_bytes = json.dumps(
            {"operation": operation, "payload": payload},
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(request_bytes) > self.max_output_bytes:
            raise NativeConnectorError("native-request-too-large")
        environment = self._environment()
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        try:
            process = subprocess.Popen(
                list(self.command),
                cwd=self.pack_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
                creationflags=flags,
            )
        except OSError as exc:
            raise NativeConnectorError("native-launch-failed") from exc
        with self._lock:
            if self._process is not None:
                process.kill()
                raise NativeConnectorError("native-operation-already-active")
            self._process = process
            self._cancel_requested = False
        stdout = bytearray()
        stderr = bytearray()
        overflow = threading.Event()
        readers = [
            threading.Thread(target=self._read_bounded, args=(process.stdout, stdout, self.max_output_bytes, overflow)),
            threading.Thread(target=self._read_bounded, args=(process.stderr, stderr, 4096, threading.Event())),
        ]
        for reader in readers:
            reader.start()
        try:
            assert process.stdin is not None
            process.stdin.write(request_bytes)
            process.stdin.close()
            deadline = time.monotonic() + timeout_ms / 1000.0
            reason: str | None = None
            while process.poll() is None:
                with self._lock:
                    cancelled = self._cancel_requested
                if cancelled:
                    reason = "native-operation-cancelled"
                    process.kill()
                    break
                if overflow.is_set():
                    reason = "native-output-too-large"
                    process.kill()
                    break
                if time.monotonic() >= deadline:
                    reason = "native-deadline-expired"
                    process.kill()
                    break
                time.sleep(0.005)
            process.wait(timeout=5)
            for reader in readers:
                reader.join(timeout=2)
            with self._lock:
                if self._cancel_requested:
                    reason = "native-operation-cancelled"
            if reason is not None:
                raise NativeConnectorError(reason)
            if overflow.is_set():
                raise NativeConnectorError("native-output-too-large")
            if process.returncode != 0:
                raise NativeConnectorError("native-operation-failed")
            try:
                result = json.loads(stdout.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise NativeConnectorError("native-response-invalid") from exc
            if not isinstance(result, dict):
                raise NativeConnectorError("native-response-invalid")
            return result
        finally:
            if process.poll() is None:
                process.kill()
            with self._lock:
                self._process = None
                self._cancel_requested = False

    def cancel(self) -> bool:
        with self._lock:
            process = self._process
            if process is None or process.poll() is not None:
                return False
            self._cancel_requested = True
            process.kill()
            return True

    @staticmethod
    def _read_bounded(stream, sink: bytearray, limit: int, overflow: threading.Event) -> None:
        if stream is None:
            return
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                return
            if len(sink) + len(chunk) > limit:
                overflow.set()
                remaining = max(limit - len(sink), 0)
                sink.extend(chunk[:remaining])
                continue
            sink.extend(chunk)

    def _environment(self) -> dict[str, str]:
        environment: dict[str, str] = {"NEXUSNET_NATIVE_PACK_ROOT": str(self.pack_root)}
        for name in ("SystemRoot", "SYSTEMROOT", "COMSPEC", "TEMP", "TMP"):
            value = os.environ.get(name)
            if value:
                environment[name] = value
        return environment


class NativeKernel:
    def __init__(
        self,
        *,
        client: NativeExecutableClient,
        declared_backend: str,
        declared_device_node_id: str,
        declared_model_formats: tuple[str, ...],
        declared_capabilities: tuple[str, ...],
    ) -> None:
        self.client = client
        self.declared_backend = declared_backend
        self.declared_device_node_id = declared_device_node_id
        self.declared_model_formats = declared_model_formats
        self.declared_capabilities = declared_capabilities
        self.model_ref: str | None = None

    def _handshake(self, timeout_ms: int) -> tuple[dict[str, Any] | None, str | None]:
        try:
            payload = self.client.invoke("describe", {}, timeout_ms=timeout_ms)
        except NativeConnectorError as exc:
            return None, str(exc)
        if payload.get("available") is not True:
            return None, "native-backend-unavailable"
        if payload.get("backend") != self.declared_backend:
            return None, "native-backend-mismatch"
        if payload.get("device_node_id") != self.declared_device_node_id:
            return None, "native-device-mismatch"
        model_formats = payload.get("model_formats")
        if (
            not isinstance(model_formats, list)
            or any(type(item) is not str for item in model_formats)
            or not set(model_formats).issubset(self.declared_model_formats)
        ):
            return None, "native-model-format-overclaim"
        capabilities = payload.get("capabilities")
        if (
            not isinstance(capabilities, list)
            or any(type(item) is not str for item in capabilities)
            or not set(capabilities).issubset(self.declared_capabilities)
        ):
            return None, "native-capability-overclaim"
        return {
            "available": True,
            "backend": self.declared_backend,
            "device_node_id": self.declared_device_node_id,
            "model_formats": list(model_formats),
            "capabilities": list(capabilities),
        }, None

    def handle(self, request: WorkerRequest) -> tuple[dict[str, Any] | None, str | None, bool]:
        remaining_ms = request.deadline_unix_ms - int(time.time() * 1000)
        if remaining_ms <= 0:
            return None, "worker-deadline-expired", False
        if request.operation == WorkerOperation.CANCEL:
            return {"cancelled": self.client.cancel()}, None, False
        if request.operation == WorkerOperation.SHUTDOWN:
            self.client.cancel()
            return {"stopped": True}, None, True
        handshake, reason = self._handshake(min(remaining_ms, 15_000))
        if reason is not None:
            return None, reason, False
        if request.operation == WorkerOperation.DESCRIBE:
            return {"worker": "nexusnet-native-connector", "protocol_version": "1.0", **handshake}, None, False
        if request.operation == WorkerOperation.HEALTH:
            return handshake, None, False
        if request.execution_mode.value not in {"auto", "gpu"}:
            return None, "execution-mode-unsupported", False
        if request.operation == WorkerOperation.LOAD_MODEL:
            model_ref = request.payload.get("model_ref")
            if not self._valid_model_ref(model_ref):
                return None, "native-model-format-unsupported", False
            try:
                result = self.client.invoke("load_model", {"model_ref": model_ref}, timeout_ms=remaining_ms)
            except NativeConnectorError as exc:
                return None, str(exc), False
            if result.get("loaded") is not True:
                return None, "native-model-load-failed", False
            self.model_ref = model_ref
            return {"loaded": True, "backend": self.declared_backend}, None, False
        if request.operation == WorkerOperation.INFER:
            if self.model_ref is None:
                return None, "model-not-loaded", False
            payload = _plain_mapping(request.payload)
            payload["model_ref"] = self.model_ref
            try:
                return self.client.invoke("infer", payload, timeout_ms=remaining_ms), None, False
            except NativeConnectorError as exc:
                return None, str(exc), False
        if request.operation in {WorkerOperation.SELF_TEST, WorkerOperation.BENCHMARK}:
            try:
                result = self.client.invoke(request.operation.value, _plain_mapping(request.payload), timeout_ms=remaining_ms)
                return result, None, False
            except NativeConnectorError as exc:
                return None, str(exc), False
        if request.operation == WorkerOperation.UNLOAD_MODEL:
            self.model_ref = None
            try:
                self.client.invoke("unload_model", {}, timeout_ms=remaining_ms)
            except NativeConnectorError as exc:
                return None, str(exc), False
            return {"unloaded": True}, None, False
        return None, "operation-unsupported", False

    def _valid_model_ref(self, value: object) -> bool:
        if type(value) is not str or not value or len(value) > 512 or "\\" in value:
            return False
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts:
            return False
        suffix = path.suffix.removeprefix(".").casefold()
        return suffix in self.declared_model_formats


def _plain_mapping(value: Mapping[str, object]) -> dict[str, Any]:
    def thaw(item: object) -> object:
        if isinstance(item, Mapping):
            return {key: thaw(child) for key, child in item.items()}
        if isinstance(item, tuple):
            return [thaw(child) for child in item]
        return item

    return {key: thaw(item) for key, item in value.items()}


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


def _kernel_from_environment() -> NativeKernel:
    root = Path(os.environ["NEXUSNET_NATIVE_ROOT"])
    client = NativeExecutableClient(root, os.environ["NEXUSNET_NATIVE_EXECUTABLE"])
    return NativeKernel(
        client=client,
        declared_backend=os.environ["NEXUSNET_NATIVE_BACKEND"],
        declared_device_node_id=os.environ["NEXUSNET_NATIVE_DEVICE_NODE_ID"],
        declared_model_formats=tuple(filter(None, os.environ["NEXUSNET_NATIVE_MODEL_FORMATS"].split(","))),
        declared_capabilities=tuple(filter(None, os.environ["NEXUSNET_NATIVE_CAPABILITIES"].split(","))),
    )


def main() -> int:
    codec = JsonLineCodec()
    try:
        kernel = _kernel_from_environment()
    except (KeyError, ValueError, NativeConnectorError):
        return 3
    for raw in sys.stdin.buffer:
        try:
            request = codec.decode_request(raw)
        except ProtocolError:
            return 2
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
