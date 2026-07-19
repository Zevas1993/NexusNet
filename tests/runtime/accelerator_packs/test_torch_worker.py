import json
from pathlib import Path
import subprocess
import sys

import pytest

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor


def _supervisor(backend: str) -> WorkerSupervisor:
    return WorkerSupervisor(
        command=[sys.executable, "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"],
        environment={"NEXUSNET_TORCH_BACKEND": backend},
        request_timeout_s=15,
    )


def _request(supervisor, operation, mode, **kwargs):
    payload = {
        "sanitized_model_ref": "model::torch-linear",
        "execution_mode": mode,
        "policy_receipt_ref": "receipt::torch-test",
    }
    payload.update(kwargs)
    return supervisor.request(operation, **payload)[-1]


def test_importing_torch_worker_module_does_not_import_torch_into_core_process():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import nexusnet.runtime.accelerator_packs.workers.torch_worker; "
                "print('torch' in sys.modules)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "False"


def test_torch_cpu_worker_runs_real_tensor_model_lifecycle():
    supervisor = _supervisor("cpu")
    try:
        health = _request(supervisor, WorkerOperation.HEALTH, ExecutionMode.CPU)
        self_test = _request(supervisor, WorkerOperation.SELF_TEST, ExecutionMode.CPU)
        _request(
            supervisor,
            WorkerOperation.LOAD_MODEL,
            ExecutionMode.CPU,
            payload={"scale": 2.0, "bias": 1.0},
        )
        inference = _request(
            supervisor,
            WorkerOperation.INFER,
            ExecutionMode.CPU,
            payload={"values": [1.0, 2.0]},
        )
    finally:
        supervisor.stop()

    assert health.payload["available"] is True
    assert health.payload["backend"] == "cpu"
    assert self_test.payload["passed"] is True
    assert inference.payload["values"] == (3.0, 5.0)


def test_torch_cuda_worker_runs_on_current_gpu_when_cuda_is_available():
    torch_probe = subprocess.run(
        [sys.executable, "-c", "import json, torch; print(json.dumps(torch.cuda.is_available()))"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        env=None,
    )
    if torch_probe.returncode != 0 or json.loads(torch_probe.stdout) is not True:
        pytest.skip("CUDA is not available in the test interpreter")

    supervisor = _supervisor("cuda")
    try:
        health = _request(supervisor, WorkerOperation.HEALTH, ExecutionMode.GPU)
        self_test = _request(supervisor, WorkerOperation.SELF_TEST, ExecutionMode.GPU)
        _request(
            supervisor,
            WorkerOperation.LOAD_MODEL,
            ExecutionMode.GPU,
            payload={"scale": 2.0, "bias": 1.0},
        )
        inference = _request(
            supervisor,
            WorkerOperation.INFER,
            ExecutionMode.GPU,
            payload={"values": [1.0, 2.0]},
        )
    finally:
        supervisor.stop()

    assert health.payload["available"] is True
    assert health.payload["backend"] == "cuda"
    assert health.payload["device_count"] >= 1
    assert self_test.payload["passed"] is True
    assert inference.payload["values"] == (3.0, 5.0)
