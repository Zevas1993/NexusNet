from datetime import datetime, timezone

from nexusnet.runtime.accelerator_packs.catalog import BuiltInPackCatalog
from nexusnet.runtime.hardware_contracts import (
    AcceleratorAdapterObservation,
    HardwareCapabilityGraph,
    HardwareNode,
)


def _graph(*, cuda: bool) -> HardwareCapabilityGraph:
    nodes = [
        HardwareNode(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu", logical_units=8),
        HardwareNode(node_id="ram:0", kind="system-ram", name="RAM", memory_bytes=16 * 1024**3),
    ]
    adapters = []
    if cuda:
        nodes.append(
            HardwareNode(
                node_id="gpu:0",
                kind="gpu",
                name="NVIDIA RTX",
                backend="cuda",
                vendor_id="10de",
                device_id="2c05",
                accelerator_apis=["cuda"],
                verification_state="detected",
                probe_source="nvidia-smi",
            )
        )
        adapters.append(
            AcceleratorAdapterObservation(
                backend="cuda",
                available=True,
                reason_code="cuda-driver-detected",
                device_count=1,
                verification_state="detected",
                probe_source="nvidia-smi",
            )
        )
    return HardwareCapabilityGraph(
        host_fingerprint="host::test",
        collected_at=datetime.now(timezone.utc),
        nodes=nodes,
        links=[],
        adapters=adapters,
    )


def test_builtin_catalog_projects_reference_and_locked_torch_cpu_then_cuda_only_with_driver_evidence():
    cpu_only = BuiltInPackCatalog().candidates(_graph(cuda=False))
    mixed = BuiltInPackCatalog().candidates(_graph(cuda=True))

    assert [candidate.manifest.pack_id for candidate in cpu_only] == [
        "org.nexusnet.cpu.reference",
        "org.nexusnet.torch.cpu",
    ]
    assert [candidate.manifest.pack_id for candidate in mixed] == [
        "org.nexusnet.cpu.reference",
        "org.nexusnet.torch.cpu",
        "org.nexusnet.torch.cuda",
    ]
    assert all(candidate.verification_state == "unverified" for candidate in mixed)
    assert mixed[2].device_node_id == "gpu:0"
    assert mixed[2].reason_codes == ("cuda-driver-detected", "runtime-pack-unverified")


def test_builtin_catalog_does_not_turn_cim_only_nvidia_detection_into_cuda_candidate():
    graph = _graph(cuda=False)
    graph = graph.model_copy(
        update={
            "nodes": [
                *graph.nodes,
                HardwareNode(
                    node_id="gpu:portable",
                    kind="gpu",
                    name="NVIDIA RTX",
                    backend="portable",
                    vendor_id="10de",
                    device_id="2c05",
                    verification_state="detected",
                    probe_source="windows-cim",
                ),
            ]
        }
    )

    candidates = BuiltInPackCatalog().candidates(graph)

    assert [candidate.manifest.pack_id for candidate in candidates] == [
        "org.nexusnet.cpu.reference",
        "org.nexusnet.torch.cpu",
    ]


def test_builtin_catalog_projects_isolated_torch_cpu_cuda_and_xpu_families():
    graph = _graph(cuda=True)
    graph = graph.model_copy(
        update={
            "nodes": [
                *graph.nodes,
                HardwareNode(
                    node_id="gpu:intel",
                    kind="gpu",
                    name="Intel Arc",
                    backend="xpu",
                    vendor_id="8086",
                    architecture="arc",
                    accelerator_apis=["xpu"],
                    verification_state="detected",
                ),
            ]
        }
    )

    candidates = BuiltInPackCatalog().candidates(graph)
    by_id = {candidate.manifest.pack_id: candidate for candidate in candidates}

    assert "org.nexusnet.torch.cpu" in by_id
    assert "org.nexusnet.torch.cuda" in by_id
    assert "org.nexusnet.torch.xpu" in by_id
    assert by_id["org.nexusnet.torch.cpu"].manifest.dependency_constraints["environment_lock_id"] == "torch-cpu-2.11.0-cp311-win-amd64"
    assert by_id["org.nexusnet.torch.xpu"].manifest.dependency_constraints["environment_lock_id"] == "torch-xpu-2.10.0-cp311-win-amd64"
    assert all("training" not in candidate.manifest.capabilities for candidate in by_id.values())


def test_windows_rocm_torch_candidate_requires_cp312_and_supported_architecture():
    graph = _graph(cuda=False).model_copy(
        update={
            "nodes": [
                *_graph(cuda=False).nodes,
                HardwareNode(
                    node_id="gpu:amd",
                    kind="gpu",
                    name="AMD Radeon",
                    backend="hip",
                    vendor_id="1002",
                    architecture="gfx1100",
                    accelerator_apis=["hip"],
                    verification_state="detected",
                ),
            ]
        }
    )

    cp311 = BuiltInPackCatalog().candidates(graph, python_abi="cp311")
    cp312 = BuiltInPackCatalog().candidates(graph, python_abi="cp312")

    assert "org.nexusnet.torch.rocm-windows" not in {item.manifest.pack_id for item in cp311}
    assert "org.nexusnet.torch.rocm-windows" in {item.manifest.pack_id for item in cp312}
