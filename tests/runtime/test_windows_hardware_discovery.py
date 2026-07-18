from datetime import datetime, timezone
from hashlib import sha256
import subprocess
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from nexusnet.runtime.evolutionary_inference.windows_hardware import discover_windows_accelerators
from nexusnet.runtime.evolutionary_inference.schemas import (
    HardwareCapabilityGraph,
    HardwareProbeObservation,
)


def test_windows_cim_discovers_portable_gpu_nodes_without_retaining_pnp_identity():
    cim_json = """[
        {
            "Name": "Intel(R) UHD Graphics",
            "PNPDeviceID": "PCI\\\\VEN_8086&DEV_9A49&SUBSYS_00000000",
            "DriverVersion": "31.0.101.5333",
            "AdapterRAM": "1073741824",
            "VideoProcessor": "Intel Xe",
            "AdapterCompatibility": "Intel Corporation",
            "Status": "OK",
            "ConfigManagerErrorCode": 0
        },
        {
            "Name": "NVIDIA GeForce RTX 5090",
            "PNPDeviceID": "PCI\\\\VEN_10DE&DEV_2C05&SUBSYS_00000000",
            "DriverVersion": "576.02",
            "AdapterRAM": "34359738368",
            "VideoProcessor": "NVIDIA GeForce RTX 5090",
            "AdapterCompatibility": "NVIDIA",
            "Status": "OK",
            "ConfigManagerErrorCode": 0
        }
    ]"""
    commands: list[list[str]] = []

    def runner(command: list[str], timeout: float):
        commands.append(command)
        if command[0] == "powershell.exe":
            assert timeout == 3.0
            return SimpleNamespace(returncode=0, stdout=cim_json)
        raise FileNotFoundError()

    discovery = discover_windows_accelerators(runner)

    assert [node.node_id for node in discovery.nodes] == [
        "gpu:windows:" + sha256(b"PCI\\VEN_8086&DEV_9A49&SUBSYS_00000000").hexdigest()[:16],
        "gpu:windows:" + sha256(b"PCI\\VEN_10DE&DEV_2C05&SUBSYS_00000000").hexdigest()[:16],
    ]
    assert [(node.vendor_id, node.device_id) for node in discovery.nodes] == [
        ("8086", "9a49"),
        ("10de", "2c05"),
    ]
    assert all(node.backend == "portable" for node in discovery.nodes)
    assert all(node.accelerator_apis == [] for node in discovery.nodes)
    assert all(node.verification_state == "detected" for node in discovery.nodes)
    serialized = "\n".join(node.model_dump_json() for node in discovery.nodes)
    assert "PNPDeviceID" not in serialized
    assert "VEN_10DE" not in serialized
    assert commands[0][:6] == [
        "powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
    ]
    assert [(item.probe_id, item.reason_code) for item in discovery.observations] == [
        ("windows-cim-video-controller", "windows-cim-detected"),
        ("nvidia-smi", "tool-not-found"),
    ]


def test_nvidia_smi_augments_matching_cim_nvidia_node_without_duplication():
    cim_json = """[
        {
            "Name": "Intel(R) UHD Graphics",
            "PNPDeviceID": "PCI\\\\VEN_8086&DEV_9A49",
            "AdapterRAM": "1073741824",
            "VideoProcessor": "Intel Xe"
        },
        {
            "Name": "NVIDIA GeForce RTX 5090",
            "PNPDeviceID": "PCI\\\\VEN_10DE&DEV_2C05",
            "AdapterRAM": "34359738368",
            "DriverVersion": "576.02",
            "VideoProcessor": "Ada"
        }
    ]"""

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        assert command == [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
        assert timeout == 3.0
        return SimpleNamespace(returncode=0, stdout="NVIDIA GeForce RTX 5090, 32607, 576.80")

    discovery = discover_windows_accelerators(runner)

    assert len(discovery.nodes) == 2
    intel, nvidia = discovery.nodes
    assert intel.backend == "portable"
    assert intel.accelerator_apis == []
    assert intel.reason_codes == ["windows-cim-detected", "runtime-unverified", "memory-os-reported"]
    assert nvidia.node_id == "gpu:windows:" + sha256(b"PCI\\VEN_10DE&DEV_2C05").hexdigest()[:16]
    assert nvidia.vendor_id == "10de"
    assert nvidia.device_id == "2c05"
    assert nvidia.architecture == "Ada"
    assert nvidia.backend == "cuda"
    assert nvidia.accelerator_apis == ["cuda"]
    assert nvidia.memory_bytes == 32607 * 1024**2
    assert nvidia.dedicated_memory_bytes == 32607 * 1024**2
    assert nvidia.driver_version == "576.80"
    assert nvidia.probe_source == "windows-cim+nvidia-smi"
    assert nvidia.reason_codes == ["windows-cim-detected", "cuda-driver-detected", "runtime-pack-unverified"]
    assert nvidia.verification_state == "detected"


@pytest.mark.parametrize(
    ("cim_response", "expected_reason"),
    [
        ("{malformed-json", "unparseable-output"),
        ("x" * (1024 * 1024 + 1), "output-too-large"),
        (FileNotFoundError(), "tool-not-found"),
        (subprocess.TimeoutExpired("powershell.exe", 3.0), "timeout"),
    ],
    ids=["malformed", "oversized", "missing-powershell", "timed-out"],
)
def test_nvidia_smi_fallback_preserves_driver_evidence_when_cim_is_unavailable(cim_response, expected_reason):
    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            if isinstance(cim_response, BaseException):
                raise cim_response
            return SimpleNamespace(returncode=0, stdout=cim_response)
        return SimpleNamespace(returncode=0, stdout="NVIDIA GeForce RTX 5070 Ti, 16303, 596.36")

    discovery = discover_windows_accelerators(runner)

    assert [(item.probe_id, item.reason_code) for item in discovery.observations] == [
        ("windows-cim-video-controller", expected_reason),
        ("nvidia-smi", "cuda-driver-detected"),
    ]
    assert len(discovery.nodes) == 1
    fallback = discovery.nodes[0]
    assert fallback.node_id == "gpu:windows:nvidia-smi:0"
    assert fallback.backend == "cuda"
    assert fallback.accelerator_apis == ["cuda"]
    assert fallback.memory_bytes == 16303 * 1024**2
    assert fallback.driver_version == "596.36"
    assert fallback.reason_codes == ["cuda-driver-detected", "runtime-pack-unverified"]


@pytest.mark.parametrize(
    ("field_name", "raw_value"),
    [
        ("probe_id", "PCI\\\\VEN_10DE&DEV_2C05"),
        ("reason_code", "C:/Users/private"),
        ("probe_source", "COMPUTERNAME=HOST"),
        ("reason_code", "command output\\nwith multiple lines"),
    ],
)
def test_hardware_probe_observation_rejects_raw_or_sensitive_receipt_values(field_name, raw_value):
    observation = {
        "probe_id": "windows-cim-video-controller",
        "available": False,
        "reason_code": "cim-query-failed",
        "probe_source": "windows-cim",
    }
    observation[field_name] = raw_value

    with pytest.raises(ValidationError):
        HardwareProbeObservation(**observation)


def test_hardware_graph_preserves_failed_windows_cim_probe_as_strict_observation():
    graph = HardwareCapabilityGraph(
        host_fingerprint="a" * 32,
        collected_at=datetime(2026, 7, 18, tzinfo=timezone.utc),
        nodes=[],
        links=[],
        adapters=[],
        discovery_observations=[
            HardwareProbeObservation(
                probe_id="windows-cim-video-controller",
                available=False,
                reason_code="cim-query-failed",
                verification_state="unavailable",
                probe_source="windows-cim",
            )
        ],
    )

    assert graph.model_dump(mode="json")["discovery_observations"] == [
        {
            "probe_id": "windows-cim-video-controller",
            "available": False,
            "reason_code": "cim-query-failed",
            "device_count": 0,
            "verification_state": "unavailable",
            "probe_source": "windows-cim",
        }
    ]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        HardwareProbeObservation(
            probe_id="windows-cim-video-controller",
            available=False,
            reason_code="cim-query-failed",
            probe_source="windows-cim",
            private_error="C:/Users/private",
        )
