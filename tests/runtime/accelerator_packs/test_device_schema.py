from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from nexusnet.runtime.evolutionary_inference.schemas import (
    AcceleratorAdapterObservation,
    HardwareCapabilityGraph,
    HardwareLink,
    HardwareNode,
)
from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph as SharedHardwareCapabilityGraph
from nexusnet.runtime.hardware_contracts import HardwareNode as SharedHardwareNode


def test_hardware_graph_represents_mixed_vendor_windows_devices_without_claiming_support():
    graph = HardwareCapabilityGraph(
        host_fingerprint="a" * 32,
        collected_at=datetime.now(timezone.utc),
        nodes=[
            HardwareNode(
                node_id="cpu:0",
                kind="cpu",
                name="Windows CPU",
                backend="cpu",
                accelerator_apis=["cpu"],
                verification_state="detected",
                probe_source="windows-cim",
            ),
            HardwareNode(
                node_id="gpu:pci:0001",
                kind="gpu",
                name="Discrete GPU",
                backend="cuda",
                vendor_id="10de",
                device_id="2c05",
                driver_version="test-driver",
                dedicated_memory_bytes=16 * 1024**3,
                shared_memory_bytes=32 * 1024**3,
                accelerator_apis=["cuda", "vulkan", "directml", "windows-ml"],
                verification_state="detected",
                probe_source="dxgi",
            ),
            HardwareNode(
                node_id="gpu:pci:0002",
                kind="gpu",
                name="Integrated GPU",
                backend="xpu",
                vendor_id="8086",
                accelerator_apis=["xpu", "sycl", "openvino", "directml", "windows-ml"],
                verification_state="unverified",
                probe_source="dxgi",
                reason_codes=["pack-evidence-missing"],
            ),
        ],
        links=[
            HardwareLink(source_node_id="cpu:0", target_node_id="gpu:pci:0001", kind="accelerator-transfer"),
            HardwareLink(source_node_id="cpu:0", target_node_id="gpu:pci:0002", kind="accelerator-transfer"),
        ],
        adapters=[
            AcceleratorAdapterObservation(
                backend="windows-ml",
                available=True,
                reason_code="provider-enumeration-available",
                device_count=2,
                verification_state="detected",
                probe_source="windows-ml",
            )
        ],
    )

    assert [node.node_id for node in graph.nodes if node.kind == "gpu"] == ["gpu:pci:0001", "gpu:pci:0002"]
    assert graph.nodes[1].vendor_id == "10de"
    assert graph.nodes[2].verification_state == "unverified"
    assert all(node.verification_state != "supported" for node in graph.nodes)
    assert HardwareNode is SharedHardwareNode
    assert HardwareCapabilityGraph is SharedHardwareCapabilityGraph


def test_hardware_graph_rejects_duplicate_or_dangling_device_references():
    common = dict(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu", accelerator_apis=["cpu"])
    with pytest.raises(ValidationError, match="node_id values must be unique"):
        HardwareCapabilityGraph(
            host_fingerprint="b" * 32,
            collected_at=datetime.now(timezone.utc),
            nodes=[HardwareNode(**common), HardwareNode(**common)],
            links=[],
            adapters=[],
        )

    with pytest.raises(ValidationError, match="unknown node"):
        HardwareCapabilityGraph(
            host_fingerprint="c" * 32,
            collected_at=datetime.now(timezone.utc),
            nodes=[HardwareNode(**common)],
            links=[HardwareLink(source_node_id="cpu:0", target_node_id="gpu:missing", kind="accelerator-transfer")],
            adapters=[],
        )
