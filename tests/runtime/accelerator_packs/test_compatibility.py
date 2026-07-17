from nexusnet.runtime.accelerator_packs.compatibility import PackCompatibilityEvaluator
from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, ModelFormat, WorkloadKind
from nexusnet.runtime.hardware_contracts import HardwareNode


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
        assert decision.reason_codes == ["manifest-compatible"]


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
