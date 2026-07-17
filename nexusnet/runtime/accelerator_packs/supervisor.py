from __future__ import annotations

import ctypes
from ctypes import wintypes
import math
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import threading
import time
from typing import Any
from uuid import uuid4

from .contracts import ExecutionMode
from .protocol import JsonLineCodec, ProtocolError, WorkerFrame, WorkerOperation, WorkerRequest


_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
_MAX_COMMAND_COMPONENTS = 128
_MAX_COMMAND_COMPONENT_LENGTH = 32_767
_MAX_COMMAND_LINE_LENGTH = 32_767
_MAX_ENVIRONMENT_ITEMS = 256
_MAX_ENVIRONMENT_VALUE_LENGTH = 32_767
_MAX_ENVIRONMENT_BLOCK_LENGTH = 32_767
_MAX_TIMEOUT_SECONDS = 3600.0
_MAX_RESPONSE_FRAMES = 4096
_FRAME_QUEUE_SIZE = 16
_RESERVED_ENVIRONMENT = {"pythonnousersite", "pythonunbuffered"}


class WorkerSupervisorError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


def _validate_timeout(value: object, *, label: str) -> float:
    if type(value) not in {int, float}:
        raise ValueError(f"{label}-invalid")
    timeout = float(value)
    if not math.isfinite(timeout) or not 0 < timeout <= _MAX_TIMEOUT_SECONDS:
        raise ValueError(f"{label}-invalid")
    return timeout


def _validate_command(command: object) -> tuple[str, ...]:
    if type(command) not in {list, tuple} or not command or len(command) > _MAX_COMMAND_COMPONENTS:
        raise ValueError("worker-command-invalid")
    validated: list[str] = []
    for component in command:
        if (type(component) is not str or not component
                or len(component) > _MAX_COMMAND_COMPONENT_LENGTH
                or any(ord(character) < 32 for character in component)):
            raise ValueError("worker-command-invalid")
        validated.append(component)
    if len(subprocess.list2cmdline(validated)) >= _MAX_COMMAND_LINE_LENGTH:
        raise ValueError("worker-command-invalid")
    return tuple(validated)


def _validate_working_directory(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, (str, Path)):
        raise ValueError("worker-working-directory-invalid")
    path = os.fspath(value)
    if not path or any(ord(character) < 32 for character in path):
        raise ValueError("worker-working-directory-invalid")
    return path


def _validate_environment(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if type(value) is not dict or len(value) > _MAX_ENVIRONMENT_ITEMS:
        raise ValueError("worker-environment-invalid")
    validated: dict[str, str] = {}
    normalized_names: set[str] = set()
    block_length = 1
    for name, item in value.items():
        if type(name) is not str or not _ENVIRONMENT_NAME.fullmatch(name):
            raise ValueError("worker-environment-invalid")
        normalized = name.casefold()
        if normalized in normalized_names or normalized in _RESERVED_ENVIRONMENT:
            raise ValueError("worker-environment-invalid")
        if (type(item) is not str or len(item) > _MAX_ENVIRONMENT_VALUE_LENGTH
                or any(character in "\r\n\x00" for character in item)):
            raise ValueError("worker-environment-invalid")
        normalized_names.add(normalized)
        validated[name] = item
        block_length += len(name) + len(item) + 2
        if block_length > _MAX_ENVIRONMENT_BLOCK_LENGTH:
            raise ValueError("worker-environment-invalid")
    return validated


if os.name == "nt":
    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class _JobObjectBasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]


    class _IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]


    class _JobObjectExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JobObjectBasicLimitInformation),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]


    _KERNEL32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
    _KERNEL32.CreateJobObjectW.restype = wintypes.HANDLE
    _KERNEL32.SetInformationJobObject.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    )
    _KERNEL32.SetInformationJobObject.restype = wintypes.BOOL
    _KERNEL32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    _KERNEL32.AssignProcessToJobObject.restype = wintypes.BOOL
    _KERNEL32.CloseHandle.argtypes = (wintypes.HANDLE,)
    _KERNEL32.CloseHandle.restype = wintypes.BOOL


def _create_windows_job(process: subprocess.Popen[bytes]) -> int | None:
    if os.name != "nt":
        return None
    job = _KERNEL32.CreateJobObjectW(None, None)
    if not job:
        return None
    information = _JobObjectExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = 0x00002000
    configured = _KERNEL32.SetInformationJobObject(
        job,
        9,
        ctypes.byref(information),
        ctypes.sizeof(information),
    )
    assigned = configured and _KERNEL32.AssignProcessToJobObject(job, wintypes.HANDLE(process._handle))
    if not assigned:
        _KERNEL32.CloseHandle(job)
        return None
    return int(job)


class WorkerSupervisor:
    _BASE_ENVIRONMENT = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "TEMP", "TMP")

    def __init__(
        self,
        *,
        command: list[str],
        working_directory: str | Path | None = None,
        environment: dict[str, str] | None = None,
        request_timeout_s: float = 30.0,
        codec: JsonLineCodec | None = None,
    ) -> None:
        self._command = _validate_command(command)
        self._working_directory = _validate_working_directory(working_directory)
        self._environment = _validate_environment(environment)
        self._request_timeout_s = _validate_timeout(request_timeout_s, label="request-timeout")
        if codec is not None and type(codec) is not JsonLineCodec:
            raise ValueError("worker-codec-invalid")
        self._codec = JsonLineCodec(max_frame_bytes=codec.max_frame_bytes) if codec is not None else JsonLineCodec()
        self._process: subprocess.Popen[bytes] | None = None
        self._frames: queue.Queue[bytes | None] = queue.Queue(maxsize=_FRAME_QUEUE_SIZE)
        self._request_lock = threading.RLock()
        self._reader: threading.Thread | None = None
        self._reader_stop: threading.Event | None = None
        self._windows_job: int | None = None

    @property
    def running(self) -> bool:
        process = self._process
        return process is not None and process.poll() is None

    def _worker_environment(self) -> dict[str, str]:
        inherited_by_name = {name.casefold(): (name, value) for name, value in os.environ.items()}
        environment: dict[str, str] = {}
        for allowed_name in self._BASE_ENVIRONMENT:
            inherited = inherited_by_name.get(allowed_name.casefold())
            if inherited is not None:
                environment[inherited[0]] = inherited[1]
        for name, value in self._environment.items():
            normalized = name.casefold()
            for inherited_name in tuple(environment):
                if inherited_name.casefold() == normalized:
                    del environment[inherited_name]
            environment[name] = value
        environment["PYTHONNOUSERSITE"] = "1"
        environment["PYTHONUNBUFFERED"] = "1"
        return environment

    def start(self) -> None:
        with self._request_lock:
            if self.running:
                return
            self._terminate()
            frame_queue: queue.Queue[bytes | None] = queue.Queue(maxsize=_FRAME_QUEUE_SIZE)
            reader_stop = threading.Event()
            creationflags = 0
            popen_options: dict[str, object] = {}
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
                    subprocess, "CREATE_NEW_PROCESS_GROUP", 0
                )
            else:
                popen_options["start_new_session"] = True
            try:
                process = subprocess.Popen(
                    self._command,
                    cwd=self._working_directory,
                    env=self._worker_environment(),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    bufsize=0,
                    creationflags=creationflags,
                    **popen_options,
                )
            except (OSError, ValueError, subprocess.SubprocessError):
                raise WorkerSupervisorError("worker-start-failed") from None
            self._process = process
            self._frames = frame_queue
            self._reader_stop = reader_stop
            try:
                self._windows_job = _create_windows_job(process)
            except Exception:
                self._windows_job = None
            reader = threading.Thread(
                target=self._read_stdout,
                args=(process, frame_queue, reader_stop),
                name="nexusnet-pack-worker-reader",
                daemon=True,
            )
            self._reader = reader
            try:
                reader.start()
            except RuntimeError:
                self._terminate()
                raise WorkerSupervisorError("worker-start-failed") from None

    def _read_stdout(
        self,
        process: subprocess.Popen[bytes],
        frame_queue: queue.Queue[bytes | None],
        reader_stop: threading.Event,
    ) -> None:
        stream = process.stdout
        if stream is None:
            self._queue_frame(frame_queue, None, reader_stop)
            return
        try:
            while not reader_stop.is_set():
                line = stream.readline(self._codec.max_frame_bytes + 1)
                if not line:
                    break
                if not self._queue_frame(frame_queue, line, reader_stop):
                    return
        except (OSError, ValueError):
            pass
        finally:
            self._queue_frame(frame_queue, None, reader_stop)

    @staticmethod
    def _queue_frame(
        frame_queue: queue.Queue[bytes | None],
        frame: bytes | None,
        reader_stop: threading.Event,
    ) -> bool:
        while not reader_stop.is_set():
            try:
                frame_queue.put(frame, timeout=0.05)
                return True
            except queue.Full:
                continue
        return False

    def request(
        self,
        operation: WorkerOperation,
        *,
        sanitized_model_ref: str,
        execution_mode: ExecutionMode,
        policy_receipt_ref: str,
        workload_profile: dict[str, int | float | str | bool] | None = None,
        payload: dict[str, Any] | None = None,
        timeout_s: float | None = None,
    ) -> list[WorkerFrame]:
        with self._request_lock:
            try:
                timeout = (
                    self._request_timeout_s
                    if timeout_s is None
                    else _validate_timeout(timeout_s, label="request-timeout")
                )
                request = WorkerRequest(
                    request_id=f"request-{uuid4().hex}",
                    operation=operation,
                    deadline_unix_ms=int((time.time() + timeout) * 1000),
                    sanitized_model_ref=sanitized_model_ref,
                    workload_profile={} if workload_profile is None else workload_profile,
                    execution_mode=execution_mode,
                    policy_receipt_ref=policy_receipt_ref,
                    payload={} if payload is None else payload,
                )
            except Exception:
                raise WorkerSupervisorError("worker-request-invalid") from None

            self.start()
            process = self._process
            frame_queue = self._frames
            if process is None or process.stdin is None:
                self._terminate()
                raise WorkerSupervisorError("worker-start-failed")
            try:
                process.stdin.write(self._codec.encode(request))
                process.stdin.flush()
            except ProtocolError as error:
                self._terminate()
                raise WorkerSupervisorError(error.reason_code) from None
            except (BrokenPipeError, OSError, ValueError):
                self._terminate()
                raise WorkerSupervisorError("worker-write-failed") from None

            deadline = time.monotonic() + timeout
            frames: list[WorkerFrame] = []
            while len(frames) < _MAX_RESPONSE_FRAMES:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._terminate()
                    raise WorkerSupervisorError("worker-timeout")
                try:
                    raw = frame_queue.get(timeout=remaining)
                except queue.Empty:
                    self._terminate()
                    raise WorkerSupervisorError("worker-timeout") from None
                if raw is None:
                    self._terminate()
                    raise WorkerSupervisorError("worker-exited")
                try:
                    frame = self._codec.decode_frame(raw)
                except ProtocolError as error:
                    self._terminate()
                    raise WorkerSupervisorError(error.reason_code) from None
                if frame.request_id != request.request_id:
                    self._terminate()
                    raise WorkerSupervisorError("worker-request-mismatch")
                if frame.sequence != len(frames):
                    self._terminate()
                    raise WorkerSupervisorError("worker-sequence-invalid")
                frames.append(frame)
                if frame.terminal:
                    return frames
            self._terminate()
            raise WorkerSupervisorError("worker-frame-limit-exceeded")

    def stop(self) -> None:
        with self._request_lock:
            if not self.running:
                self._terminate()
                return
            try:
                self.request(
                    WorkerOperation.SHUTDOWN,
                    sanitized_model_ref="model::none",
                    execution_mode=ExecutionMode.AUTO,
                    policy_receipt_ref="receipt::shutdown",
                    timeout_s=min(2.0, self._request_timeout_s),
                )
            except WorkerSupervisorError:
                pass
            finally:
                self._terminate()

    def _terminate(self) -> None:
        process = self._process
        reader = self._reader
        reader_stop = self._reader_stop
        windows_job = self._windows_job
        self._process = None
        self._reader = None
        self._reader_stop = None
        self._windows_job = None
        if reader_stop is not None:
            reader_stop.set()
        if process is not None:
            self._terminate_process_tree(process, windows_job)
            for stream in (process.stdin, process.stdout):
                if stream is not None:
                    try:
                        stream.close()
                    except OSError:
                        pass
        elif windows_job is not None and os.name == "nt":
            _KERNEL32.CloseHandle(wintypes.HANDLE(windows_job))
        if reader is not None and reader is not threading.current_thread():
            reader.join(timeout=1)

    @staticmethod
    def _terminate_process_tree(process: subprocess.Popen[bytes], windows_job: int | None) -> None:
        if os.name == "nt":
            requires_fallback = windows_job is None
            if windows_job is not None:
                requires_fallback = not bool(_KERNEL32.CloseHandle(wintypes.HANDLE(windows_job)))
            if requires_fallback and process.poll() is None:
                system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
                try:
                    subprocess.run(
                        [
                            str(system_root / "System32" / "taskkill.exe"),
                            "/PID",
                            str(process.pid),
                            "/T",
                            "/F",
                        ],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=2,
                        check=False,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                except (OSError, subprocess.SubprocessError):
                    pass
        elif process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
        try:
            process.wait(timeout=2)
            return
        except (OSError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            try:
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
