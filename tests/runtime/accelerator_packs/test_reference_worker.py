from pathlib import Path
import sys

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor


def _supervisor() -> WorkerSupervisor:
    return WorkerSupervisor(
        command=[sys.executable, "-m", "nexusnet.runtime.accelerator_packs.workers.reference_worker"],
        request_timeout_s=5,
    )


def _request(supervisor, operation, **kwargs):
    payload = {
        "sanitized_model_ref": "model::reference",
        "execution_mode": ExecutionMode.CPU,
        "policy_receipt_ref": "receipt::reference-test",
    }
    payload.update(kwargs)
    return supervisor.request(operation, **payload)[-1]


def test_reference_worker_runs_full_numeric_model_lifecycle():
    supervisor = _supervisor()
    try:
        description = _request(supervisor, WorkerOperation.DESCRIBE)
        health = _request(supervisor, WorkerOperation.HEALTH)
        self_test = _request(supervisor, WorkerOperation.SELF_TEST)
        loaded = _request(
            supervisor,
            WorkerOperation.LOAD_MODEL,
            payload={"scale": 2.0, "bias": 1.0},
        )
        inferred = _request(supervisor, WorkerOperation.INFER, payload={"values": [1.0, 2.0]})
        benchmark = _request(supervisor, WorkerOperation.BENCHMARK, payload={"iterations": 8})
        unloaded = _request(supervisor, WorkerOperation.UNLOAD_MODEL)
    finally:
        supervisor.stop()

    assert description.payload["backend"] == "cpu"
    assert health.payload == {"available": True, "backend": "cpu", "capabilities": {"numeric-model": True}}
    assert self_test.payload["passed"] is True
    assert loaded.payload["loaded"] is True
    assert inferred.payload["values"] == (3.0, 5.0)
    assert benchmark.payload["iterations"] == 8
    assert benchmark.payload["duration_ms"] > 0
    assert unloaded.payload["unloaded"] is True


def test_reference_worker_fails_closed_when_inference_has_no_loaded_model():
    supervisor = _supervisor()
    try:
        frame = _request(supervisor, WorkerOperation.INFER, payload={"values": [1.0]})
    finally:
        supervisor.stop()

    assert frame.event == "error"
    assert frame.reason_code == "model-not-loaded"
    assert frame.payload == {}
