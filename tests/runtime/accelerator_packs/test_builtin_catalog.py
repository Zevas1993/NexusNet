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


def test_builtin_catalog_always_projects_cpu_and_only_projects_cuda_with_driver_evidence():
    cpu_only = BuiltInPackCatalog().candidates(_graph(cuda=False))
    mixed = BuiltInPackCatalog().candidates(_graph(cuda=True))

    assert [candidate.manifest.pack_id for candidate in cpu_only] == ["org.nexusnet.cpu.reference"]
    assert [candidate.manifest.pack_id for candidate in mixed] == [
        "org.nexusnet.cpu.reference",
        "org.nexusnet.torch.cuda",
    ]
    assert all(candidate.verification_state == "unverified" for candidate in mixed)
    assert mixed[1].device_node_id == "gpu:0"
    assert mixed[1].reason_codes == ("cuda-driver-detected", "runtime-pack-unverified")


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

    assert [candidate.manifest.pack_id for candidate in candidates] == ["org.nexusnet.cpu.reference"]
