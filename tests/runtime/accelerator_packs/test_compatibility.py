import pytest

from nexusnet.runtime.accelerator_packs.compatibility import PackCompatibilityEvaluator
from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, ModelFormat, WorkloadKind
from nexusnet.runtime.hardware_contracts import HardwareNode


def _matching_gpu(**overrides) -> HardwareNode:
    payload = {
        "node_id": "gpu:test:0",
        "kind": "gpu",
        "name": "Test GPU",
        "backend": "cuda",
        "vendor_id": "10de",
        "driver_version": "551.61",
        "dedicated_memory_bytes": 16 * 1024**3,
        "accelerator_apis": ["cuda"],
    }
    payload.update(overrides)
    return HardwareNode.model_validate(payload)


def _evaluate(manifest, device: HardwareNode, **overrides):
    arguments = {
        "manifest": manifest,
        "device": device,
        "host_os": "windows",
        "architecture": "amd64",
        "os_build": 26100,
        "workload": WorkloadKind.LLM_GENERATE,
        "model_format": ModelFormat.GGUF,
        "requested_mode": ExecutionMode.GPU,
    }
    arguments.update(overrides)
    return PackCompatibilityEvaluator().evaluate(**arguments)


def test_compatibility_matches_capabilities_instead_of_vendor_dispatch(manifest_factory):
    manifest = manifest_factory(
        pack_id="org.nexusnet.test.vulkan",
        accelerator_apis=["vulkan"],
        device_matches=[{"accelerator_apis": ["vulkan"]}],
    )
    amd = HardwareNode(
        node_id="gpu:amd:0",
        kind="gpu",
        name="AMD GPU",
        backend="vulkan",
        vendor_id="1002",
        accelerator_apis=["vulkan", "directml"],
    )
    intel = HardwareNode(
        node_id="gpu:intel:0",
        kind="gpu",
        name="Intel GPU",
        backend="vulkan",
        vendor_id="8086",
        accelerator_apis=["vulkan", "directml"],
    )

    evaluator = PackCompatibilityEvaluator()
    for device in (amd, intel):
        decision = evaluator.evaluate(
            manifest=manifest,
            device=device,
            host_os="windows",
            architecture="amd64",
            os_build=26100,
            workload=WorkloadKind.LLM_GENERATE,
            model_format=ModelFormat.GGUF,
            requested_mode=ExecutionMode.GPU,
        )
        assert decision.compatible is True
        assert decision.reason_codes == ("manifest-compatible",)


def test_forced_modes_fail_honestly_when_device_class_or_pack_mode_conflicts(manifest_factory):
    cpu = HardwareNode(
        node_id="cpu:0",
        kind="cpu",
        name="CPU",
        backend="cpu",
        accelerator_apis=["cpu"],
    )
    decision = PackCompatibilityEvaluator().evaluate(
        manifest=manifest_factory(),
        device=cpu,
        host_os="windows",
        architecture="amd64",
        os_build=26100,
        workload=WorkloadKind.LLM_GENERATE,
        model_format=ModelFormat.GGUF,
        requested_mode=ExecutionMode.GPU,
    )

    assert decision.compatible is False
    assert "gpu-mode-requires-accelerator" in decision.reason_codes
    assert "device-api-mismatch" in decision.reason_codes


@pytest.mark.parametrize(
    ("override", "reason_code"),
    [
        ({"host_os": "linux"}, "os-mismatch"),
        ({"architecture": "arm64"}, "architecture-mismatch"),
        ({"os_build": 26000}, "os-build-too-old"),
        ({"workload": WorkloadKind.EMBEDDING}, "workload-mismatch"),
        ({"model_format": ModelFormat.ONNX}, "model-format-mismatch"),
        ({"requested_mode": ExecutionMode.CPU}, "cpu-mode-requires-cpu"),
    ],
)
def test_compatibility_reports_each_manifest_mismatch(manifest_factory, override, reason_code):
    decision = _evaluate(manifest_factory(), _matching_gpu(), **override)

    assert decision.compatible is False
    assert reason_code in decision.reason_codes


def test_compatibility_checks_driver_python_abi_and_dependency_evidence(manifest_factory):
    manifest = manifest_factory(
        minimum_driver_version="552.0",
        python_abi="cp311",
        dependency_constraints={"runtime": ">=1.2,<2.0"},
    )

    unverified = _evaluate(manifest, _matching_gpu(driver_version=None))
    assert {
        "driver-version-unverified",
        "python-abi-unverified",
        "dependency-constraints-unverified",
    }.issubset(unverified.reason_codes)

    mismatched = _evaluate(
        manifest,
        _matching_gpu(driver_version="551.61"),
        host_python_abi="cp310",
        dependency_versions={"runtime": "2.0"},
    )
    assert {
        "driver-version-too-old",
        "python-abi-mismatch",
        "dependency-version-mismatch",
    }.issubset(mismatched.reason_codes)

    compatible = _evaluate(
        manifest,
        _matching_gpu(driver_version="552.1"),
        host_python_abi="CP311",
        dependency_versions={"Runtime": "1.3.0"},
    )
    assert compatible.compatible is True


@pytest.mark.parametrize("kind", ["storage", "system-ram"])
def test_auto_rejects_non_compute_nodes(manifest_factory, kind):
    node = HardwareNode(
        node_id=f"{kind}:0",
        kind=kind,
        name=kind,
        backend="portable",
        accelerator_apis=["portable"],
    )
    manifest = manifest_factory(
        accelerator_apis=["portable"],
        device_matches=[],
        execution_modes=["gpu"],
    )

    decision = _evaluate(manifest, node, requested_mode=ExecutionMode.AUTO)

    assert decision.compatible is False
    assert "device-not-compute-capable" in decision.reason_codes
    assert "auto-has-no-concrete-mode" in decision.reason_codes


def test_hybrid_requires_an_accelerator_node_even_when_pack_supports_offload(manifest_factory):
    manifest = manifest_factory(
        accelerator_apis=["cpu"],
        device_matches=[],
        execution_modes=["hybrid"],
        capabilities=["hybrid-offload"],
    )
    cpu = HardwareNode(
        node_id="cpu:0",
        kind="cpu",
        name="CPU",
        backend="cpu",
        accelerator_apis=["cpu"],
    )

    decision = _evaluate(manifest, cpu, requested_mode=ExecutionMode.HYBRID)

    assert decision.compatible is False
    assert "hybrid-mode-requires-accelerator" in decision.reason_codes


def test_auto_and_hybrid_accept_only_matching_compute_routes(manifest_factory):
    cpu_manifest = manifest_factory(
        pack_id="org.nexusnet.test.cpu",
        accelerator_apis=["cpu"],
        device_matches=[],
        execution_modes=["cpu"],
    )
    cpu = HardwareNode(
        node_id="cpu:0",
        kind="cpu",
        name="CPU",
        backend="cpu",
        accelerator_apis=["cpu"],
    )
    assert _evaluate(cpu_manifest, cpu, requested_mode=ExecutionMode.AUTO).compatible is True
    assert _evaluate(manifest_factory(), _matching_gpu(), requested_mode=ExecutionMode.AUTO).compatible is True

    hybrid_manifest = manifest_factory(
        execution_modes=["hybrid"],
        capabilities=["hybrid-offload"],
    )
    assert _evaluate(hybrid_manifest, _matching_gpu(), requested_mode=ExecutionMode.HYBRID).compatible is True


def test_mode_and_api_mismatch_reason_codes_are_preserved(manifest_factory):
    wrong_mode = _evaluate(
        manifest_factory(),
        _matching_gpu(),
        requested_mode=ExecutionMode.CPU,
    )
    assert {"cpu-mode-requires-cpu", "execution-mode-mismatch"}.issubset(wrong_mode.reason_codes)

    wrong_api = _evaluate(
        manifest_factory(),
        _matching_gpu(backend="vulkan", accelerator_apis=["vulkan"]),
    )
    assert {"device-api-mismatch", "device-predicate-mismatch"}.issubset(wrong_api.reason_codes)


def test_prerequisites_fail_closed_on_invalid_constraints_or_missing_dependencies(manifest_factory):
    manifest = manifest_factory(
        minimum_driver_version="latest",
        dependency_constraints={
            "runtime": "~=1.2",
            "missing-runtime": ">=1.0",
        },
    )

    decision = _evaluate(
        manifest,
        _matching_gpu(),
        dependency_versions={"runtime": "1.3"},
    )

    assert decision.compatible is False
    assert {
        "driver-version-constraint-invalid",
        "dependency-constraint-unverified",
        "dependency-unavailable",
    }.issubset(decision.reason_codes)


def test_device_predicates_enforce_memory_and_decisions_are_deeply_immutable(manifest_factory):
    manifest = manifest_factory(
        device_matches=[
            {
                "vendor_ids": ["10de"],
                "accelerator_apis": ["cuda"],
                "minimum_memory_bytes": 8 * 1024**3,
            }
        ]
    )

    rejected = _evaluate(manifest, _matching_gpu(dedicated_memory_bytes=4 * 1024**3))
    assert rejected.compatible is False
    assert "device-predicate-mismatch" in rejected.reason_codes

    accepted = _evaluate(manifest, _matching_gpu())
    assert accepted.compatible is True
    with pytest.raises(AttributeError):
        accepted.reason_codes.append("tampered")
