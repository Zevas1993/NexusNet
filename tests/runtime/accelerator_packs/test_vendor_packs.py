from __future__ import annotations

from datetime import datetime, timezone

from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.accelerator_packs.vendor_packs import VendorPackCatalog
from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph, HardwareNode


def _graph(*nodes: HardwareNode) -> HardwareCapabilityGraph:
    return HardwareCapabilityGraph(
        host_fingerprint="host::vendor-matrix",
        collected_at=datetime.now(timezone.utc),
        nodes=[HardwareNode(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu"), *nodes],
        links=[],
        adapters=[],
    )


def _gpu(
    node_id: str,
    *,
    vendor_id: str,
    architecture: str,
    apis: list[str],
) -> HardwareNode:
    return HardwareNode(
        node_id=node_id,
        kind="gpu",
        name="Test GPU",
        vendor_id=vendor_id,
        architecture=architecture,
        accelerator_apis=apis,
        backend=apis[0],
        verification_state="detected",
    )


def test_amd_hip_requires_official_windows_rocm_architecture_tuple() -> None:
    supported = VendorPackCatalog().candidates(
        _graph(_gpu("gpu:amd", vendor_id="1002", architecture="gfx1100", apis=["hip", "vulkan"]))
    )
    legacy = VendorPackCatalog().candidates(
        _graph(_gpu("gpu:legacy", vendor_id="1002", architecture="gfx1030", apis=["hip", "vulkan"]))
    )

    assert [item.manifest.pack_id for item in supported] == [
        "org.nexusnet.native.amd-hip",
        "org.nexusnet.native.amd-vulkan",
    ]
    assert [item.manifest.pack_id for item in legacy] == ["org.nexusnet.native.amd-vulkan"]
    assert all(item.verification_state == "unverified" for item in supported)
    assert legacy[0].manifest.device_matches[0].architectures == ()


def test_intel_sycl_and_openvino_require_supported_family_and_observed_api() -> None:
    supported = VendorPackCatalog().candidates(
        _graph(_gpu("gpu:intel", vendor_id="8086", architecture="xe-hpg", apis=["sycl", "openvino"]))
    )
    legacy = VendorPackCatalog().candidates(
        _graph(_gpu("gpu:intel-legacy", vendor_id="8086", architecture="gen8", apis=["sycl", "openvino"]))
    )

    assert [item.manifest.pack_id for item in supported] == [
        "org.nexusnet.native.intel-sycl",
        "org.nexusnet.native.intel-openvino",
    ]
    assert legacy == ()


def test_mixed_vendor_devices_remain_independent_and_never_imply_hybrid() -> None:
    graph = _graph(
        _gpu("gpu:amd", vendor_id="1002", architecture="gfx1200", apis=["hip"]),
        _gpu("gpu:intel", vendor_id="8086", architecture="arc", apis=["sycl"]),
    )

    candidates = VendorPackCatalog().candidates(graph)

    assert {item.device_node_id for item in candidates} == {"gpu:amd", "gpu:intel"}
    assert all([mode.value for mode in item.manifest.execution_modes] == ["gpu"] for item in candidates)
    assert all("hybrid-offload" not in item.manifest.capabilities for item in candidates)


def test_common_catalog_adds_vendor_candidates_but_preserves_cpu_fallback() -> None:
    graph = _graph(_gpu("gpu:amd", vendor_id="1002", architecture="gfx1101", apis=["vulkan"]))

    candidates = BuiltInPackCatalog().candidates(graph)

    assert [item.manifest.pack_id for item in candidates] == [
        "org.nexusnet.cpu.reference",
        "org.nexusnet.torch.cpu",
        "org.nexusnet.native.amd-vulkan",
    ]
    assert candidates[2].reason_codes[-1] == "runtime-pack-unverified"


def test_support_matrix_is_immutable_data_with_source_and_runtime_identity() -> None:
    records = VendorPackCatalog.support_matrix()
    amd = next(record for record in records if record.backend == "hip")

    assert amd.runtime_version == "7.2.1"
    assert amd.python_abi == "cp312"
    assert amd.supported_architectures == ("gfx1201", "gfx1200", "gfx1100", "gfx1101", "gfx1150", "gfx1151")
    assert amd.source_url.startswith("https://rocm.docs.amd.com/")
