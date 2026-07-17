import subprocess
import sys
from pathlib import Path

import pytest

from nexus.schemas import Message
from nexus.runtimes.worker import RuntimeExecutionError, WorkerRuntimeAdapter
from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerFrame, WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError


def _command() -> list[str]:
    fixture = Path(__file__).parents[2] / "fixtures" / "accelerator_pack_worker.py"
    return [sys.executable, "-I", str(fixture)]


def _frame(*, payload=None, event="result", reason_code=None) -> WorkerFrame:
    return WorkerFrame(
        request_id="request::fixture",
        event=event,
        sequence=0,
        terminal=True,
        payload={} if payload is None else payload,
        reason_code=reason_code,
    )


class _RecordingSupervisor:
    def __init__(self, *, health_frames=None, inference_frames=None, error=None):
        self.health_frames = health_frames or [
            _frame(payload={"available": True, "capabilities": {"streaming": True}})
        ]
        self.inference_frames = inference_frames or [_frame(payload={"text": "recorded"})]
        self.error = error
        self.calls = []

    def request(self, operation, **arguments):
        self.calls.append((operation, arguments))
        if self.error is not None:
            raise self.error
        if operation is WorkerOperation.HEALTH:
            return self.health_frames
        return self.inference_frames


def test_worker_adapter_preserves_health_profile_and_generate_contract(manifest_factory):
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    adapter = WorkerRuntimeAdapter(manifest=manifest_factory(), supervisor=supervisor)

    try:
        health = adapter.health()
        generated = adapter.generate(
            prompt=None,
            messages=[Message(role="user", content="hello")],
            model_id="fixture-model",
            metadata={"execution_mode": "gpu", "policy_receipt_ref": "receipt::adapter"},
        )

        assert health["available"] is True
        assert health["pack_id"] == "org.nexusnet.test.cuda"
        assert adapter.profile().backend_type == "managed-worker"
        assert generated == "worker:USER: hello"
    finally:
        supervisor.stop()


def test_accelerator_pack_core_imports_no_vendor_runtime_modules():
    repository_root = Path(__file__).parents[3]
    script = (
        "import sys; import nexusnet.runtime.accelerator_packs; "
        "banned=('torch','onnxruntime','openvino','intel_extension_for_pytorch'); "
        "assert not any(n == b or n.startswith(b + '.') for n in sys.modules for b in banned)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_accelerator_pack_package_exports_foundation_contracts_without_adapter_registration():
    import nexusnet.runtime.accelerator_packs as accelerator_packs

    expected_exports = {
        "CompatibilityDecision",
        "ExecutionMode",
        "JsonLineCodec",
        "PackCompatibilityEvaluator",
        "RuntimePackManifest",
        "RuntimePackRegistry",
        "WorkerOperation",
        "WorkerSupervisor",
    }
    assert expected_exports <= set(accelerator_packs.__all__)
    assert "WorkerRuntimeAdapter" not in accelerator_packs.__all__


@pytest.mark.parametrize("requested_mode", ["cpu", "both"])
def test_worker_adapter_rejects_forced_modes_the_manifest_does_not_support(
    manifest_factory,
    requested_mode,
):
    supervisor = _RecordingSupervisor()
    adapter = WorkerRuntimeAdapter(manifest=manifest_factory(), supervisor=supervisor)

    with pytest.raises(RuntimeExecutionError, match="execution-mode-unsupported") as captured:
        adapter.generate(
            prompt="hello",
            messages=[],
            model_id="fixture-model",
            metadata={"execution_mode": requested_mode},
        )

    assert captured.value.reason_code == "execution-mode-unsupported"
    assert supervisor.calls == []


def test_worker_adapter_translates_declared_both_mode_to_hybrid(manifest_factory):
    manifest = manifest_factory(
        execution_modes=["gpu", "hybrid"],
        capabilities=["streaming", "hybrid-offload"],
    )
    supervisor = _RecordingSupervisor()
    adapter = WorkerRuntimeAdapter(manifest=manifest, supervisor=supervisor)

    assert adapter.generate(
        prompt="hello",
        messages=[],
        model_id="fixture-model",
        metadata={"execution_mode": "both"},
    ) == "recorded"
    assert supervisor.calls[-1][1]["execution_mode"] is ExecutionMode.HYBRID


def test_worker_adapter_hashes_model_identity_and_rejects_unsafe_receipt_metadata(manifest_factory):
    supervisor = _RecordingSupervisor()
    adapter = WorkerRuntimeAdapter(manifest=manifest_factory(), supervisor=supervisor)
    private_model_id = r"C:\Users\private\weights\model.gguf"

    assert adapter.generate(
        prompt="hello",
        messages=[],
        model_id=private_model_id,
        metadata={"execution_mode": "gpu", "policy_receipt_ref": "receipt::safe"},
    ) == "recorded"
    arguments = supervisor.calls[-1][1]
    assert arguments["sanitized_model_ref"].startswith("model::")
    assert private_model_id not in repr(arguments)
    assert "model_id" not in arguments["payload"]

    with pytest.raises(RuntimeExecutionError, match="policy-receipt-ref-invalid") as captured:
        adapter.generate(
            prompt="hello",
            messages=[],
            model_id="fixture-model",
            metadata={"execution_mode": "gpu", "policy_receipt_ref": private_model_id},
        )
    assert private_model_id not in str(captured.value)


@pytest.mark.parametrize(
    "payload",
    [
        {"available": "true", "capabilities": {}},
        {"available": 1, "capabilities": {}},
        {"available": True, "capabilities": []},
    ],
)
def test_worker_adapter_health_requires_exact_public_contract_types(manifest_factory, payload):
    adapter = WorkerRuntimeAdapter(
        manifest=manifest_factory(),
        supervisor=_RecordingSupervisor(health_frames=[_frame(payload=payload)]),
    )

    health = adapter.health()

    assert health["available"] is False
    assert health["reason_codes"] == ["worker-health-invalid"]
    assert adapter.profile().available is False


def test_worker_adapter_sanitizes_hostile_supervisor_failures(manifest_factory):
    private_error = r"C:\Users\private\prompt.txt"
    adapter = WorkerRuntimeAdapter(
        manifest=manifest_factory(),
        supervisor=_RecordingSupervisor(error=WorkerSupervisorError(private_error)),
    )

    health = adapter.health()
    assert health["reason_codes"] == ["worker-health-failed"]
    with pytest.raises(RuntimeExecutionError, match="worker-inference-failed") as captured:
        adapter.generate(
            prompt="hello",
            messages=[],
            model_id="fixture-model",
            metadata={"execution_mode": "gpu"},
        )
    assert private_error not in str(health)
    assert private_error not in str(captured.value)
