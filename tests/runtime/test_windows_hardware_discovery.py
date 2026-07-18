from datetime import datetime, timezone
from hashlib import sha256
import json
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
    assert [adapter.backend for adapter in discovery.adapters] == ["cuda"]


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
            "VideoProcessor": "NVIDIA Ada"
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
    assert nvidia.architecture == "NVIDIA Ada"
    assert nvidia.backend == "cuda"
    assert nvidia.accelerator_apis == ["cuda"]
    assert nvidia.memory_bytes == 32607 * 1024**2
    assert nvidia.dedicated_memory_bytes == 32607 * 1024**2
    assert nvidia.driver_version == "576.80"
    assert nvidia.probe_source == "windows-cim+nvidia-smi"
    assert nvidia.reason_codes == ["windows-cim-detected", "cuda-driver-detected", "runtime-pack-unverified"]
    assert nvidia.verification_state == "detected"


def test_windows_discovery_redacts_unsafe_cim_and_nvidia_payloads_from_serialized_nodes():
    private_path = r"C:\\Users\\Chris\\private-model"
    env_assignment = "COMPUTERNAME=PRIVATE-HOST"
    host_uri = "https://private-host.example/secret"
    cim_json = json.dumps(
        [
            {
                "Name": private_path,
                "PNPDeviceID": "PCI\\VEN_8086&DEV_9A49",
                "DriverVersion": host_uri,
                "VideoProcessor": env_assignment,
            }
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(returncode=0, stdout=f"{host_uri}, 16303, {env_assignment}\nmultiline-output")

    discovery = discover_windows_accelerators(runner)

    serialized = "\n".join(node.model_dump_json() for node in discovery.nodes)
    for prohibited in (private_path, env_assignment, host_uri, "multiline-output"):
        assert prohibited not in serialized
    cim_node, nvidia_node = discovery.nodes
    assert cim_node.name == "windows-gpu"
    assert cim_node.architecture is None
    assert cim_node.driver_version is None
    assert nvidia_node.name == "nvidia-gpu"
    assert nvidia_node.driver_version is None


def test_windows_discovery_redacts_bare_user_and_host_names_from_cim_and_nvidia_fields():
    bare_user = "Chris"
    bare_host = "DESKTOP-7K3M"
    cim_json = json.dumps(
        [
            {
                "Name": bare_user,
                "PNPDeviceID": "PCI\\VEN_8086&DEV_9A49",
                "VideoProcessor": bare_host,
                "DriverVersion": "31.0.101.5333",
            }
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(returncode=0, stdout=f"{bare_host}, 16303, {bare_user}")

    discovery = discover_windows_accelerators(runner)

    serialized = "\n".join(node.model_dump_json() for node in discovery.nodes)
    assert bare_user not in serialized
    assert bare_host not in serialized
    cim_node, nvidia_node = discovery.nodes
    assert cim_node.name == "windows-gpu"
    assert cim_node.architecture is None
    assert cim_node.driver_version == "31.0.101.5333"
    assert nvidia_node.name == "nvidia-gpu"
    assert nvidia_node.driver_version is None


def test_windows_discovery_rejects_overlong_numeric_driver_versions():
    overlong_version = "1." + "0" * 64
    cim_json = json.dumps(
        [
            {
                "Name": "NVIDIA GeForce RTX 5070 Ti",
                "PNPDeviceID": "PCI\\VEN_10DE&DEV_2C05",
                "DriverVersion": overlong_version,
            }
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        raise FileNotFoundError()

    discovery = discover_windows_accelerators(runner)

    assert discovery.nodes[0].driver_version is None
    assert overlong_version not in discovery.nodes[0].model_dump_json()


def test_windows_discovery_reconstructs_labels_without_vendor_prefixed_host_bypasses():
    cim_bypass = "NVIDIA-DESKTOP-7K3M"
    smi_bypass = "NVIDIA_HOME"
    cim_json = json.dumps(
        [
            {
                "Name": cim_bypass,
                "PNPDeviceID": "PCI\\VEN_8086&DEV_9A49",
                "VideoProcessor": smi_bypass,
            }
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(returncode=0, stdout=f"{smi_bypass}, 16303, 596.36")

    discovery = discover_windows_accelerators(runner)

    serialized = "\n".join(node.model_dump_json() for node in discovery.nodes)
    for prohibited in (cim_bypass, smi_bypass, "DESKTOP", "HOME"):
        assert prohibited not in serialized
    assert [node.name for node in discovery.nodes] == ["NVIDIA", "NVIDIA"]
    assert discovery.nodes[0].architecture == "NVIDIA"
    assert discovery.nodes[1].driver_version == "596.36"


def test_cim_pnp_identity_is_canonicalized_before_deduplication_and_hashing():
    cim_json = json.dumps(
        [
            {"Name": "NVIDIA GeForce RTX 5090", "PNPDeviceID": " pci\\ven_10de&dev_2c05 "},
            {"Name": "NVIDIA GeForce RTX 5090", "PNPDeviceID": "PCI\\VEN_10DE&DEV_2C05"},
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        raise FileNotFoundError()

    discovery = discover_windows_accelerators(runner)

    assert len(discovery.nodes) == 1
    assert discovery.nodes[0].node_id == "gpu:windows:" + sha256(b"PCI\\VEN_10DE&DEV_2C05").hexdigest()[:16]
    assert (discovery.nodes[0].vendor_id, discovery.nodes[0].device_id) == ("10de", "2c05")


def test_same_name_nvidia_rows_augment_cim_devices_in_source_order():
    controllers = [
        {"Name": "Intel Graphics", "PNPDeviceID": "PCI\\VEN_8086&DEV_0001"},
        {"Name": "NVIDIA GeForce RTX", "PNPDeviceID": "PCI\\VEN_10DE&DEV_0001", "VideoProcessor": "NVIDIA Ada 1"},
    ]
    controllers.extend(
        {"Name": f"Intel Graphics {index}", "PNPDeviceID": f"PCI\\VEN_8086&DEV_{index:04X}"}
        for index in range(2, 8)
    )
    controllers.append(
        {"Name": "NVIDIA GeForce RTX", "PNPDeviceID": "PCI\\VEN_10DE&DEV_0002", "VideoProcessor": "NVIDIA Ada 2"}
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=json.dumps(controllers))
        return SimpleNamespace(
            returncode=0,
            stdout="NVIDIA GeForce RTX, 100, 600.01\nNVIDIA GeForce RTX, 200, 600.02",
        )

    discovery = discover_windows_accelerators(runner)

    nvidia = [node for node in discovery.nodes if node.vendor_id == "10de"]
    assert [node.memory_bytes for node in nvidia] == [100 * 1024**2, 200 * 1024**2]
    assert [node.driver_version for node in nvidia] == ["600.01", "600.02"]
    assert [node.architecture for node in nvidia] == ["NVIDIA Ada 1", "NVIDIA Ada 2"]


def test_nvidia_matching_uses_exact_original_ordinal_before_fallback():
    cim_json = json.dumps(
        [
            {"Name": "NVIDIA GeForce RTX A", "PNPDeviceID": "PCI\\VEN_10DE&DEV_000A"},
            {"Name": "NVIDIA GeForce RTX B", "PNPDeviceID": "PCI\\VEN_10DE&DEV_000B"},
        ]
    )

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(
            returncode=0,
            stdout="NVIDIA GeForce RTX B, 200, 600.02\nNVIDIA GeForce RTX C, 300, 600.03",
        )

    discovery = discover_windows_accelerators(runner)

    first, second, fallback = discovery.nodes
    assert first.backend == "portable"
    assert first.name == "NVIDIA GeForce RTX"
    assert second.backend == "cuda"
    assert second.memory_bytes == 200 * 1024**2
    assert fallback.node_id == "gpu:windows:nvidia-smi:1"
    assert fallback.memory_bytes == 300 * 1024**2


@pytest.mark.parametrize(
    ("cim_json", "expected_reason"),
    [
        ("[]", "no-devices-detected"),
        ("{}", "unparseable-output"),
        ("[null]", "unparseable-output"),
    ],
    ids=["empty-list", "empty-object", "null-record"],
)
def test_cim_empty_and_structurally_unusable_payloads_have_distinct_sanitized_reasons(cim_json, expected_reason):
    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        raise FileNotFoundError()

    discovery = discover_windows_accelerators(runner)

    assert discovery.observations[0].available is False
    assert discovery.observations[0].reason_code == expected_reason
    assert discovery.observations[0].reason_code != "available"


def test_unmatched_nvidia_smi_rows_are_added_when_cim_only_reports_intel():
    cim_json = json.dumps([{"Name": "Intel Graphics", "PNPDeviceID": "PCI\\VEN_8086&DEV_9A49"}])

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(returncode=0, stdout="NVIDIA GeForce RTX 5070 Ti, 16303, 596.36")

    discovery = discover_windows_accelerators(runner)

    assert len(discovery.nodes) == 2
    assert discovery.nodes[0].backend == "portable"
    fallback = discovery.nodes[1]
    assert fallback.node_id == "gpu:windows:nvidia-smi:0"
    assert fallback.backend == "cuda"
    assert fallback.driver_version == "596.36"


def test_extra_nvidia_smi_rows_are_fallbacks_after_matching_cim_nvidia_device():
    cim_json = json.dumps([{"Name": "NVIDIA GeForce RTX", "PNPDeviceID": "PCI\\VEN_10DE&DEV_2C05"}])

    def runner(command: list[str], timeout: float):
        if command[0] == "powershell.exe":
            return SimpleNamespace(returncode=0, stdout=cim_json)
        return SimpleNamespace(
            returncode=0,
            stdout="NVIDIA GeForce RTX, 100, 600.01\nNVIDIA GeForce RTX Extra, 200, 600.02",
        )

    discovery = discover_windows_accelerators(runner)

    assert [node.node_id for node in discovery.nodes] == [
        "gpu:windows:" + sha256(b"PCI\\VEN_10DE&DEV_2C05").hexdigest()[:16],
        "gpu:windows:nvidia-smi:1",
    ]
    assert [node.memory_bytes for node in discovery.nodes] == [100 * 1024**2, 200 * 1024**2]


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
