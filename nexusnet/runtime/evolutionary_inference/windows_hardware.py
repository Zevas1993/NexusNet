from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Callable

from nexusnet.runtime.hardware_contracts import (
    AcceleratorAdapterObservation,
    HardwareNode,
    HardwareProbeObservation,
)


CommandRunner = Callable[[list[str], float], Any]

_MAX_STDOUT_BYTES = 1024 * 1024
_PCI_VENDOR = re.compile(r"VEN_([0-9A-Fa-f]{4})")
_PCI_DEVICE = re.compile(r"DEV_([0-9A-Fa-f]{4})")
_CIM_SCRIPT = (
    "$ErrorActionPreference='Stop'; "
    "@(Get-CimInstance -ClassName Win32_VideoController | "
    "Select-Object Name,PNPDeviceID,DriverVersion,AdapterRAM,VideoProcessor,"
    "AdapterCompatibility,Status,ConfigManagerErrorCode) | ConvertTo-Json -Compress"
)


@dataclass(frozen=True)
class WindowsAcceleratorDiscovery:
    nodes: tuple[HardwareNode, ...]
    adapters: tuple[AcceleratorAdapterObservation, ...]
    observations: tuple[HardwareProbeObservation, ...]


def discover_windows_accelerators(command_runner: CommandRunner) -> WindowsAcceleratorDiscovery:
    cim_stdout, cim_reason = _run_bounded(command_runner, _cim_command())
    nodes, cim_parsed = _cim_nodes(cim_stdout) if cim_stdout is not None else ([], False)
    if cim_stdout is not None and not cim_parsed:
        cim_reason = "unparseable-output"
    nvidia_stdout, nvidia_reason = _run_bounded(command_runner, _nvidia_smi_command())
    augmented_nodes = nodes
    nvidia_available = False
    if nvidia_stdout is not None:
        nvidia_rows = _nvidia_rows(nvidia_stdout)
        nvidia_available = bool(nvidia_rows)
        nvidia_reason = "cuda-driver-detected" if nvidia_available else "unparseable-output"
        augmented_nodes = _augment_nvidia_nodes(nodes, nvidia_rows)
        if not nodes:
            augmented_nodes = _nvidia_fallback_nodes(nvidia_rows)
    cim_available = bool(nodes)
    cim_observation_reason = "windows-cim-detected" if cim_available else cim_reason
    return WindowsAcceleratorDiscovery(
        nodes=tuple(augmented_nodes),
        adapters=(
            AcceleratorAdapterObservation(
                backend="portable",
                available=cim_available,
                reason_code=cim_observation_reason,
                device_count=len(nodes),
                verification_state="detected" if cim_available else "unavailable",
                probe_source="windows-cim",
            ),
            AcceleratorAdapterObservation(
                backend="cuda",
                available=nvidia_available,
                reason_code=nvidia_reason,
                device_count=sum(node.backend == "cuda" for node in augmented_nodes),
                verification_state="detected" if nvidia_available else "unavailable",
                probe_source="nvidia-smi",
            ),
        ),
        observations=(
            HardwareProbeObservation(
                probe_id="windows-cim-video-controller",
                available=cim_available,
                reason_code=cim_observation_reason,
                device_count=len(nodes),
                verification_state="detected" if cim_available else "unavailable",
                probe_source="windows-cim",
            ),
            HardwareProbeObservation(
                probe_id="nvidia-smi",
                available=nvidia_available,
                reason_code=nvidia_reason,
                device_count=sum(node.backend == "cuda" for node in augmented_nodes),
                verification_state="detected" if nvidia_available else "unavailable",
                probe_source="nvidia-smi",
            ),
        ),
    )


def _cim_command() -> list[str]:
    return [
        "powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        _CIM_SCRIPT,
    ]


def _nvidia_smi_command() -> list[str]:
    return [
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ]


def _run_bounded(command_runner: CommandRunner, command: list[str]) -> tuple[str | None, str]:
    try:
        result = command_runner(command, 3.0)
    except FileNotFoundError:
        return None, "tool-not-found"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except (OSError, ValueError):
        return None, "probe-failed"
    if int(getattr(result, "returncode", 1)) != 0:
        return None, "probe-failed"
    stdout = getattr(result, "stdout", "")
    if isinstance(stdout, bytes):
        if len(stdout) > _MAX_STDOUT_BYTES:
            return None, "output-too-large"
        return stdout.decode("utf-8", errors="replace"), "available"
    rendered = str(stdout)
    if len(rendered.encode("utf-8")) > _MAX_STDOUT_BYTES:
        return None, "output-too-large"
    return rendered, "available"


def _cim_nodes(stdout: str) -> tuple[list[HardwareNode], bool]:
    try:
        payload = json.loads(stdout)
    except (TypeError, json.JSONDecodeError):
        return [], False
    if not isinstance(payload, (dict, list)):
        return [], False
    records = payload if isinstance(payload, list) else [payload]
    nodes: list[HardwareNode] = []
    seen_ids: set[str] = set()
    for record in records:
        node = _cim_node(record)
        if node is not None and node.node_id not in seen_ids:
            seen_ids.add(node.node_id)
            nodes.append(node)
    return nodes, True


def _cim_node(record: Any) -> HardwareNode | None:
    if not isinstance(record, dict):
        return None
    pnp_device_id = record.get("PNPDeviceID")
    if not isinstance(pnp_device_id, str) or not pnp_device_id:
        return None
    vendor_match = _PCI_VENDOR.search(pnp_device_id)
    device_match = _PCI_DEVICE.search(pnp_device_id)
    memory = _positive_int(record.get("AdapterRAM"))
    reason_codes = ["windows-cim-detected", "runtime-unverified"]
    if memory is not None:
        reason_codes.append("memory-os-reported")
    return HardwareNode(
        node_id="gpu:windows:" + hashlib.sha256(pnp_device_id.encode()).hexdigest()[:16],
        kind="gpu",
        name=_clean_label(record.get("Name"), fallback="windows-gpu"),
        backend="portable",
        memory_bytes=memory,
        vendor_id=vendor_match.group(1).lower() if vendor_match else None,
        device_id=device_match.group(1).lower() if device_match else None,
        architecture=_clean_optional(record.get("VideoProcessor")),
        driver_version=_clean_optional(record.get("DriverVersion")),
        dedicated_memory_bytes=memory,
        accelerator_apis=[],
        verification_state="detected",
        probe_source="windows-cim",
        reason_codes=reason_codes,
    )


def _nvidia_rows(stdout: str) -> list[tuple[str, int | None, str | None]]:
    rows: list[tuple[str, int | None, str | None]] = []
    for line in stdout.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 3 or not fields[0]:
            continue
        rows.append((
            _clean_label(fields[0], fallback="nvidia-gpu"),
            _mib_bytes(fields[1]),
            _clean_optional(fields[2]),
        ))
    return rows


def _augment_nvidia_nodes(
    nodes: list[HardwareNode], rows: list[tuple[str, int | None, str | None]]
) -> list[HardwareNode]:
    augmented = list(nodes)
    nvidia_indexes = [index for index, node in enumerate(nodes) if node.vendor_id == "10de"]
    unmatched = set(nvidia_indexes)
    for ordinal, (name, memory, driver_version) in enumerate(rows):
        normalized_name = _normalized_name(name)
        match = next(
            (
                index
                for index in unmatched
                if _normalized_name(nodes[index].name) == normalized_name
            ),
            None,
        )
        if match is None and ordinal < len(nvidia_indexes) and nvidia_indexes[ordinal] in unmatched:
            match = nvidia_indexes[ordinal]
        if match is None:
            continue
        unmatched.remove(match)
        node = nodes[match]
        augmented[match] = node.model_copy(
            update={
                "backend": "cuda",
                "memory_bytes": memory,
                "dedicated_memory_bytes": memory,
                "driver_version": driver_version,
                "accelerator_apis": ["cuda"],
                "probe_source": "windows-cim+nvidia-smi",
                "reason_codes": [
                    "windows-cim-detected",
                    "cuda-driver-detected",
                    "runtime-pack-unverified",
                ],
            }
        )
    return augmented


def _nvidia_fallback_nodes(rows: list[tuple[str, int | None, str | None]]) -> list[HardwareNode]:
    return [
        HardwareNode(
            node_id=f"gpu:windows:nvidia-smi:{index}",
            kind="gpu",
            name=name,
            backend="cuda",
            memory_bytes=memory,
            vendor_id="10de",
            driver_version=driver_version,
            dedicated_memory_bytes=memory,
            accelerator_apis=["cuda"],
            verification_state="detected",
            probe_source="nvidia-smi",
            reason_codes=["cuda-driver-detected", "runtime-pack-unverified"],
        )
        for index, (name, memory, driver_version) in enumerate(rows)
    ]


def _positive_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _mib_bytes(value: Any) -> int | None:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return None
    return parsed * 1024**2 if parsed > 0 else None


def _normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _clean_label(value: Any, *, fallback: str) -> str:
    cleaned = " ".join(str(value or "").replace("\x00", " ").split()).strip()
    return cleaned[:120] or fallback


def _clean_optional(value: Any) -> str | None:
    cleaned = _clean_label(value, fallback="")
    return cleaned or None
