import ctypes
from ctypes import wintypes
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import JsonLineCodec, WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError


def _command() -> list[str]:
    fixture = Path(__file__).parents[2] / "fixtures" / "accelerator_pack_worker.py"
    return [sys.executable, "-I", str(fixture)]


def _request(supervisor: WorkerSupervisor, operation: WorkerOperation, **overrides):
    arguments = {
        "sanitized_model_ref": "model::none",
        "execution_mode": ExecutionMode.AUTO,
        "policy_receipt_ref": "receipt::test",
    }
    arguments.update(overrides)
    return supervisor.request(operation, **arguments)


def _process_is_running(process_id: int) -> bool:
    if sys.platform == "win32":
        synchronize = 0x00100000
        wait_timeout = 0x00000102
        wait_failed = 0xFFFFFFFF
        invalid_parameter = 87
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        kernel32.WaitForSingleObject.restype = wintypes.DWORD
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(synchronize, False, process_id)
        if not handle:
            error_code = ctypes.get_last_error()
            if error_code == invalid_parameter:
                return False
            raise ctypes.WinError(error_code)
        try:
            result = kernel32.WaitForSingleObject(handle, 0)
            if result == wait_failed:
                raise ctypes.WinError(ctypes.get_last_error())
            return result == wait_timeout
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(process_id, 0)
    except OSError:
        return False
    return True


def _force_kill(process_id: int) -> None:
    if not _process_is_running(process_id):
        return
    if sys.platform == "win32":
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        subprocess.run(
            [str(system_root / "System32" / "taskkill.exe"), "/PID", str(process_id), "/T", "/F"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    else:
        os.kill(process_id, signal.SIGKILL)


def test_supervisor_correlates_streaming_frames_and_stops_the_worker():
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    try:
        health = _request(supervisor, WorkerOperation.HEALTH, policy_receipt_ref="receipt::health")
        inference = _request(
            supervisor,
            WorkerOperation.INFER,
            sanitized_model_ref="model::fixture",
            execution_mode=ExecutionMode.CPU,
            policy_receipt_ref="receipt::infer",
            payload={"prompt": "hello"},
        )

        assert health[-1].payload["available"] is True
        assert [frame.event for frame in inference] == ["accepted", "chunk", "result"]
        assert inference[-1].payload["text"] == "worker:hello"
    finally:
        supervisor.stop()
    assert supervisor.running is False


def test_supervisor_terminates_timeout_and_malformed_workers_without_echoing_payload():
    timeout_supervisor = WorkerSupervisor(command=_command(), request_timeout_s=0.1)
    with pytest.raises(WorkerSupervisorError, match="worker-timeout") as timeout:
        _request(
            timeout_supervisor,
            WorkerOperation.BENCHMARK,
            execution_mode=ExecutionMode.GPU,
            policy_receipt_ref="receipt::timeout",
            payload={"hang": True, "prompt": "private timeout prompt"},
        )
    assert "private timeout prompt" not in str(timeout.value)
    assert timeout_supervisor.running is False

    malformed_supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    with pytest.raises(WorkerSupervisorError, match="worker-frame-invalid") as malformed:
        _request(
            malformed_supervisor,
            WorkerOperation.SELF_TEST,
            execution_mode=ExecutionMode.CPU,
            policy_receipt_ref="receipt::malformed",
            payload={"malformed": True},
        )
    assert "private-output" not in str(malformed.value)
    assert malformed_supervisor.running is False


@pytest.mark.parametrize(
    ("payload", "reason_code"),
    [
        ({"wrong_request_id": True}, "worker-request-mismatch"),
        ({"bad_sequence": True}, "worker-sequence-invalid"),
    ],
)
def test_supervisor_rejects_uncorrelated_or_out_of_order_frames(payload, reason_code):
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    with pytest.raises(WorkerSupervisorError, match=reason_code):
        _request(supervisor, WorkerOperation.SELF_TEST, payload=payload)
    assert supervisor.running is False


def test_supervisor_bounds_unterminated_worker_output_before_codec_admission():
    supervisor = WorkerSupervisor(
        command=_command(),
        request_timeout_s=2,
        codec=JsonLineCodec(max_frame_bytes=1024),
    )
    with pytest.raises(WorkerSupervisorError, match="worker-frame-too-large") as error:
        _request(supervisor, WorkerOperation.SELF_TEST, payload={"oversized": True})
    assert "private-oversized-output" not in str(error.value)
    assert supervisor.running is False


def test_supervisor_uses_a_restricted_environment_with_explicit_pack_values(monkeypatch):
    monkeypatch.setenv("NEXUSNET_PRIVATE_TEST", "private-parent-secret")
    supervisor = WorkerSupervisor(command=_command(), environment={"PACK_SETTING": "explicit"})
    try:
        result = _request(supervisor, WorkerOperation.DESCRIBE)[-1]
    finally:
        supervisor.stop()

    assert result.payload["private_environment_seen"] is False
    assert result.payload["pack_setting"] == "explicit"


@pytest.mark.parametrize(
    "arguments",
    [
        {"command": []},
        {"command": "private-worker.exe"},
        {"command": ["private\nworker.exe"]},
        {"command": ["worker.exe"], "request_timeout_s": True},
        {"command": ["worker.exe"], "request_timeout_s": math.nan},
        {"command": ["worker.exe"], "environment": {"BAD=NAME": "private"}},
        {"command": ["worker.exe"], "environment": {"Path": "one", "PATH": "two"}},
        {"command": ["worker.exe"], "environment": {"PYTHONNOUSERSITE": "0"}},
    ],
)
def test_supervisor_rejects_invalid_launch_configuration_without_echoing_values(arguments):
    with pytest.raises(ValueError) as error:
        WorkerSupervisor(**arguments)
    assert "private" not in str(error.value)


def test_supervisor_enforces_aggregate_windows_launch_block_bounds():
    oversized_component = "x" * 20_000

    with pytest.raises(ValueError, match="worker-command-invalid"):
        WorkerSupervisor(command=["worker.exe", oversized_component, oversized_component])
    with pytest.raises(ValueError, match="worker-environment-invalid"):
        WorkerSupervisor(
            command=["worker.exe"],
            environment={"PACK_VALUE_ONE": oversized_component, "PACK_VALUE_TWO": oversized_component},
        )


def test_supervisor_falls_back_cleanly_when_job_containment_is_unavailable(monkeypatch):
    import nexusnet.runtime.accelerator_packs.supervisor as supervisor_module

    def fail_job_assignment(process):
        raise OSError("private job-assignment failure")

    monkeypatch.setattr(supervisor_module, "_create_windows_job", fail_job_assignment)
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    try:
        result = _request(supervisor, WorkerOperation.HEALTH)
    finally:
        supervisor.stop()

    assert result[-1].payload["available"] is True
    assert supervisor.running is False


def test_supervisor_sanitizes_start_and_request_validation_failures(tmp_path):
    missing = tmp_path / "private-worker-does-not-exist.exe"
    supervisor = WorkerSupervisor(command=[str(missing)])
    with pytest.raises(WorkerSupervisorError, match="worker-start-failed") as start_error:
        _request(supervisor, WorkerOperation.HEALTH)
    assert "private-worker" not in str(start_error.value)

    invalid_request = WorkerSupervisor(command=_command())
    with pytest.raises(WorkerSupervisorError, match="worker-request-invalid") as request_error:
        invalid_request.request(
            b"health",
            sanitized_model_ref="model::none",
            execution_mode=ExecutionMode.AUTO,
            policy_receipt_ref="receipt::test",
            payload={"private": {1, 2}},
        )
    assert "private" not in str(request_error.value)
    assert invalid_request.running is False


def test_supervisor_sanitizes_hostile_request_mapping_exceptions():
    class HostilePayload(dict):
        def items(self):
            raise RuntimeError("private hostile mapping output")

    supervisor = WorkerSupervisor(command=_command())
    with pytest.raises(WorkerSupervisorError, match="worker-request-invalid") as error:
        _request(supervisor, WorkerOperation.HEALTH, payload=HostilePayload({"private": True}))

    assert "private" not in str(error.value)
    assert supervisor.running is False


def test_supervisor_snapshots_the_admitted_codec_frame_limit():
    codec = JsonLineCodec(max_frame_bytes=1024)
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2, codec=codec)
    codec.max_frame_bytes = 1024 * 1024

    with pytest.raises(WorkerSupervisorError, match="worker-frame-too-large"):
        _request(supervisor, WorkerOperation.SELF_TEST, payload={"oversized": True})

    assert supervisor.running is False


def test_supervisor_can_restart_without_stale_reader_events_poisoning_the_new_worker():
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    for _ in range(3):
        assert _request(supervisor, WorkerOperation.HEALTH)[-1].payload["available"] is True
        supervisor.stop()
        assert supervisor.running is False


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process-tree contract")
def test_supervisor_terminates_spawned_descendants_on_timeout(tmp_path):
    child_pid_path = tmp_path / "child.pid"
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=0.5)
    child_pid = None
    try:
        with pytest.raises(WorkerSupervisorError, match="worker-timeout"):
            _request(
                supervisor,
                WorkerOperation.BENCHMARK,
                payload={"spawn_child": True, "child_pid_path": str(child_pid_path)},
            )
        deadline = time.monotonic() + 2
        while not child_pid_path.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert child_pid_path.exists()
        child_pid = int(child_pid_path.read_text(encoding="ascii"))
        assert not _process_is_running(child_pid)
    finally:
        supervisor.stop()
        if child_pid is not None:
            _force_kill(child_pid)
