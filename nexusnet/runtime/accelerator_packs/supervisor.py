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
_MAX_RESPONSE_BYTES_LIMIT = 1024 * 1024 * 1024
_DEFAULT_MAX_RESPONSE_BYTES = 64 * 1024 * 1024
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


    class _ThreadEntry32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
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
    _KERNEL32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    _KERNEL32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _KERNEL32.Thread32First.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    _KERNEL32.Thread32First.restype = wintypes.BOOL
    _KERNEL32.Thread32Next.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    _KERNEL32.Thread32Next.restype = wintypes.BOOL
    _KERNEL32.OpenThread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    _KERNEL32.OpenThread.restype = wintypes.HANDLE
    _KERNEL32.ResumeThread.argtypes = (wintypes.HANDLE,)
    _KERNEL32.ResumeThread.restype = wintypes.DWORD


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


def _resume_windows_process(process: subprocess.Popen[bytes]) -> bool:
    if os.name != "nt":
        return True
    invalid_handle_value = ctypes.c_void_p(-1).value
    snapshot = _KERNEL32.CreateToolhelp32Snapshot(0x00000004, 0)
    if not snapshot or int(snapshot) == invalid_handle_value:
        return False
    thread_handle = None
    try:
        entry = _ThreadEntry32()
        entry.dwSize = ctypes.sizeof(entry)
        found = bool(_KERNEL32.Thread32First(snapshot, ctypes.byref(entry)))
        while found:
            if entry.th32OwnerProcessID == process.pid:
                thread_handle = _KERNEL32.OpenThread(0x0002, False, entry.th32ThreadID)
                break
            found = bool(_KERNEL32.Thread32Next(snapshot, ctypes.byref(entry)))
        if not thread_handle:
            return False
        return _KERNEL32.ResumeThread(thread_handle) != 0xFFFFFFFF
    finally:
        if thread_handle:
            _KERNEL32.CloseHandle(thread_handle)
        _KERNEL32.CloseHandle(snapshot)


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
        max_response_bytes: int = _DEFAULT_MAX_RESPONSE_BYTES,
    ) -> None:
        self._command = _validate_command(command)
        self._working_directory = _validate_working_directory(working_directory)
        self._environment = _validate_environment(environment)
        self._request_timeout_s = _validate_timeout(request_timeout_s, label="request-timeout")
        if codec is not None and type(codec) is not JsonLineCodec:
            raise ValueError("worker-codec-invalid")
        if (type(max_response_bytes) is not int or max_response_bytes <= 0
                or max_response_bytes > _MAX_RESPONSE_BYTES_LIMIT):
            raise ValueError("worker-response-limit-invalid")
        self._codec = JsonLineCodec(max_frame_bytes=codec.max_frame_bytes) if codec is not None else JsonLineCodec()
        self._max_response_bytes = max_response_bytes
        self._process: subprocess.Popen[bytes] | None = None
        self._frames: queue.Queue[bytes | None] = queue.Queue(maxsize=_FRAME_QUEUE_SIZE)
        self._request_lock = threading.RLock()
        self._write_lock = threading.Lock()
        self._cancel_state_lock = threading.Lock()
        self._lifecycle_lock = threading.RLock()
        self._reader: threading.Thread | None = None
        self._reader_stop: threading.Event | None = None
        self._windows_job: int | None = None
        self._launch_cancel: threading.Event | None = None
        self._active_request_id: str | None = None
        self._active_request_ready: threading.Event | None = None
        self._active_cancel_committed = False
        self._control_request_ids: set[str] = set()

    @property
    def running(self) -> bool:
        with self._lifecycle_lock:
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
            self._start_with_deadline(time.monotonic() + self._request_timeout_s)

    def _start_with_deadline(self, deadline: float) -> None:
        with self._lifecycle_lock:
            if self._process is not None and self._process.poll() is None:
                return
            if self._launch_cancel is not None:
                raise WorkerSupervisorError("worker-start-in-progress")
            launch_cancel = threading.Event()
            self._launch_cancel = launch_cancel

        result_queue: queue.Queue[tuple[str, subprocess.Popen[bytes] | None, int | None]] = queue.Queue(maxsize=1)
        handoff_lock = threading.Lock()
        launcher = threading.Thread(
            target=self._launch_worker,
            args=(launch_cancel, handoff_lock, result_queue),
            name="nexusnet-pack-worker-launcher",
            daemon=True,
        )
        try:
            launcher.start()
        except RuntimeError:
            with self._lifecycle_lock:
                if self._launch_cancel is launch_cancel:
                    self._launch_cancel = None
            raise WorkerSupervisorError("worker-start-failed") from None

        result: tuple[str, subprocess.Popen[bytes] | None, int | None] | None = None
        while result is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                result = self._cancel_launch(launch_cancel, handoff_lock, result_queue)
                with self._lifecycle_lock:
                    if self._launch_cancel is launch_cancel:
                        self._launch_cancel = None
                if result is not None and result[1] is not None:
                    self._cleanup_launched_process(result[1], result[2])
                raise WorkerSupervisorError("worker-timeout")
            if launch_cancel.is_set():
                with self._lifecycle_lock:
                    if self._launch_cancel is launch_cancel:
                        self._launch_cancel = None
                raise WorkerSupervisorError("worker-exited")
            try:
                result = result_queue.get(timeout=min(remaining, 0.05))
            except queue.Empty:
                continue

        status, process, windows_job = result
        if status != "ok" or process is None:
            with self._lifecycle_lock:
                if self._launch_cancel is launch_cancel:
                    self._launch_cancel = None
            raise WorkerSupervisorError("worker-start-failed")

        frame_queue: queue.Queue[bytes | None] = queue.Queue(maxsize=_FRAME_QUEUE_SIZE)
        reader_stop = threading.Event()
        reader = threading.Thread(
            target=self._read_stdout,
            args=(process, frame_queue, reader_stop),
            name="nexusnet-pack-worker-reader",
            daemon=True,
        )
        with self._lifecycle_lock:
            if launch_cancel.is_set() or self._launch_cancel is not launch_cancel:
                publish = False
            else:
                self._launch_cancel = None
                self._process = process
                self._frames = frame_queue
                self._reader_stop = reader_stop
                self._reader = reader
                self._windows_job = windows_job
                publish = True
        if not publish:
            self._cleanup_launched_process(process, windows_job)
            raise WorkerSupervisorError("worker-exited")
        try:
            reader.start()
        except RuntimeError:
            self._terminate()
            raise WorkerSupervisorError("worker-start-failed") from None

    def _launch_worker(
        self,
        launch_cancel: threading.Event,
        handoff_lock: threading.Lock,
        result_queue: queue.Queue[tuple[str, subprocess.Popen[bytes] | None, int | None]],
    ) -> None:
        process: subprocess.Popen[bytes] | None = None
        windows_job: int | None = None
        status = "error"
        try:
            creationflags = 0
            popen_options: dict[str, object] = {}
            if os.name == "nt":
                creationflags = (
                    getattr(subprocess, "CREATE_NO_WINDOW", 0)
                    | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    | 0x00000004
                )
            else:
                popen_options["start_new_session"] = True
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
            if launch_cancel.is_set():
                self._cleanup_launched_process(process, None)
                return
            if os.name == "nt":
                windows_job = _create_windows_job(process)
                if windows_job is None or launch_cancel.is_set() or not _resume_windows_process(process):
                    self._cleanup_launched_process(process, windows_job)
                    process = None
                    windows_job = None
                else:
                    status = "ok"
            else:
                status = "ok"
        except Exception:
            if process is not None:
                self._cleanup_launched_process(process, windows_job)
            process = None
            windows_job = None

        with handoff_lock:
            cancelled = launch_cancel.is_set()
            if not cancelled:
                result_queue.put_nowait((status, process, windows_job))
        if cancelled and process is not None:
            self._cleanup_launched_process(process, windows_job)

    @staticmethod
    def _cancel_launch(
        launch_cancel: threading.Event,
        handoff_lock: threading.Lock,
        result_queue: queue.Queue[tuple[str, subprocess.Popen[bytes] | None, int | None]],
    ) -> tuple[str, subprocess.Popen[bytes] | None, int | None] | None:
        with handoff_lock:
            launch_cancel.set()
            try:
                return result_queue.get_nowait()
            except queue.Empty:
                return None

    @classmethod
    def _cleanup_launched_process(cls, process: subprocess.Popen[bytes], windows_job: int | None) -> None:
        cls._terminate_process_tree(process, windows_job)
        for stream in (process.stdin, process.stdout):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass

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
        if operation == WorkerOperation.CANCEL:
            self.cancel(timeout_s=timeout_s)
            return []
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
                encoded = self._codec.encode(request)
            except ProtocolError as error:
                raise WorkerSupervisorError(error.reason_code) from None
            except Exception:
                raise WorkerSupervisorError("worker-request-invalid") from None

            deadline = time.monotonic() + timeout
            request_ready = threading.Event()
            with self._cancel_state_lock:
                with self._lifecycle_lock:
                    self._active_request_id = None
                    self._active_request_ready = request_ready
                    self._active_cancel_committed = False
                    self._control_request_ids.clear()
            try:
                self._start_with_deadline(deadline)
                with self._lifecycle_lock:
                    process = self._process
                    frame_queue = self._frames
                if process is None or process.stdin is None:
                    self._terminate()
                    raise WorkerSupervisorError("worker-start-failed")
                self._write_encoded(process, encoded, deadline)
                with self._cancel_state_lock:
                    with self._lifecycle_lock:
                        if self._process is not process or self._active_request_ready is not request_ready:
                            raise WorkerSupervisorError("worker-exited")
                        self._active_request_id = request.request_id
                        request_ready.set()

                frames: list[WorkerFrame] = []
                response_bytes = 0
                while len(frames) < _MAX_RESPONSE_FRAMES:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self._terminate()
                        raise WorkerSupervisorError("worker-timeout")
                    try:
                        raw = frame_queue.get(timeout=min(remaining, 0.05))
                    except queue.Empty:
                        with self._lifecycle_lock:
                            active_process = self._process
                        if active_process is not process:
                            raise WorkerSupervisorError("worker-exited") from None
                        continue
                    if raw is None:
                        self._terminate()
                        raise WorkerSupervisorError("worker-exited")
                    response_bytes += len(raw)
                    if response_bytes > self._max_response_bytes:
                        self._terminate()
                        raise WorkerSupervisorError("worker-response-too-large")
                    try:
                        frame = self._codec.decode_frame(raw)
                    except ProtocolError as error:
                        self._terminate()
                        raise WorkerSupervisorError(error.reason_code) from None
                    if frame.request_id != request.request_id:
                        with self._lifecycle_lock:
                            is_control = frame.request_id in self._control_request_ids
                            if is_control and frame.terminal:
                                self._control_request_ids.discard(frame.request_id)
                        if is_control:
                            continue
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
            finally:
                recycle_worker = False
                with self._cancel_state_lock:
                    with self._lifecycle_lock:
                        if self._active_request_ready is request_ready:
                            recycle_worker = self._active_cancel_committed
                            self._active_request_id = None
                            self._active_request_ready = None
                            self._active_cancel_committed = False
                        self._control_request_ids.clear()
                if recycle_worker:
                    self._terminate()
                request_ready.set()

    def cancel(self, *, timeout_s: float | None = None) -> None:
        try:
            timeout = 2.0 if timeout_s is None else _validate_timeout(timeout_s, label="cancel-timeout")
            deadline = time.monotonic() + timeout
            deadline_unix_ms = int((time.time() + timeout) * 1000)
            while True:
                with self._lifecycle_lock:
                    process = self._process
                    target_request_id = self._active_request_id
                    request_ready = self._active_request_ready
                if process is not None and process.poll() is None and target_request_id is not None:
                    break
                if request_ready is None:
                    raise WorkerSupervisorError("worker-cancel-unavailable")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise WorkerSupervisorError("worker-timeout")
                request_ready.wait(timeout=min(remaining, 0.05))
            cancel_request = WorkerRequest(
                request_id=f"request-{uuid4().hex}",
                operation=WorkerOperation.CANCEL,
                deadline_unix_ms=deadline_unix_ms,
                sanitized_model_ref="model::none",
                workload_profile={},
                execution_mode=ExecutionMode.AUTO,
                policy_receipt_ref="receipt::cancel",
                payload={"target_request_id": target_request_id},
            )
            encoded = self._codec.encode(cancel_request)
        except WorkerSupervisorError:
            raise
        except Exception:
            raise WorkerSupervisorError("worker-cancel-invalid") from None
        with self._cancel_state_lock:
            with self._lifecycle_lock:
                if (self._process is not process or process.poll() is not None
                        or self._active_request_id != target_request_id
                        or self._active_cancel_committed):
                    raise WorkerSupervisorError("worker-cancel-unavailable")
                self._control_request_ids.add(cancel_request.request_id)
            self._write_encoded(process, encoded, deadline)
            with self._lifecycle_lock:
                if self._process is not process or self._active_request_id != target_request_id:
                    raise WorkerSupervisorError("worker-cancel-unavailable")
                self._active_cancel_committed = True

    def _write_encoded(self, process: subprocess.Popen[bytes], encoded: bytes, deadline: float) -> None:
        result_queue: queue.Queue[str | None] = queue.Queue(maxsize=1)

        def write_request() -> None:
            try:
                with self._write_lock:
                    if process.stdin is None:
                        raise BrokenPipeError
                    process.stdin.write(encoded)
                    process.stdin.flush()
                result_queue.put_nowait(None)
            except Exception:
                try:
                    result_queue.put_nowait("worker-write-failed")
                except queue.Full:
                    pass

        writer = threading.Thread(
            target=write_request,
            name="nexusnet-pack-worker-writer",
            daemon=True,
        )
        try:
            writer.start()
        except RuntimeError:
            self._terminate()
            raise WorkerSupervisorError("worker-write-failed") from None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._terminate()
                writer.join(timeout=0.5)
                raise WorkerSupervisorError("worker-timeout")
            try:
                reason = result_queue.get(timeout=min(remaining, 0.05))
            except queue.Empty:
                with self._lifecycle_lock:
                    active_process = self._process
                if active_process is not process:
                    raise WorkerSupervisorError("worker-exited") from None
                continue
            writer.join(timeout=0.5)
            if reason is not None:
                self._terminate()
                raise WorkerSupervisorError(reason)
            return

    def stop(self) -> None:
        self._terminate()

    def _terminate(self) -> None:
        with self._lifecycle_lock:
            launch_cancel = self._launch_cancel
            process = self._process
            frame_queue = self._frames
            reader = self._reader
            reader_stop = self._reader_stop
            windows_job = self._windows_job
            active_request_ready = self._active_request_ready
            self._launch_cancel = None
            self._process = None
            self._frames = queue.Queue(maxsize=_FRAME_QUEUE_SIZE)
            self._reader = None
            self._reader_stop = None
            self._windows_job = None
            self._active_request_id = None
            self._active_request_ready = None
            self._control_request_ids.clear()
        if launch_cancel is not None:
            launch_cancel.set()
        if reader_stop is not None:
            reader_stop.set()
        if active_request_ready is not None:
            active_request_ready.set()
        if process is not None:
            self._cleanup_launched_process(process, windows_job)
        elif windows_job is not None and os.name == "nt":
            _KERNEL32.CloseHandle(wintypes.HANDLE(windows_job))
        if (reader is not None and reader is not threading.current_thread()
                and reader.ident is not None):
            try:
                reader.join(timeout=1)
            except RuntimeError:
                pass
        while True:
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                break
        try:
            frame_queue.put_nowait(None)
        except queue.Full:
            pass

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
            try:
                process.wait(timeout=2)
                return
            except (OSError, subprocess.TimeoutExpired):
                pass
            if process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            return
        else:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass
            try:
                process.wait(timeout=0.5)
            except (OSError, subprocess.TimeoutExpired):
                pass
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
