from __future__ import annotations

import hashlib
import json
import math
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
_MAX_MEMORY_BYTES = 2**64 - 1
_PCI_VENDOR = re.compile(r"VEN_([0-9A-F]{4})", re.IGNORECASE)
_PCI_DEVICE = re.compile(r"DEV_([0-9A-F]{4})", re.IGNORECASE)
_SAFE_HARDWARE_PAYLOAD = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .()_+\-]{0,119}\Z")
_HOST_STYLE_PAYLOAD = re.compile(r"\b(?=[a-z0-9-]*[a-z])[a-z0-9-]+(?:\.[a-z0-9-]+)+\b", re.IGNORECASE)
_DRIVER_VERSION = re.compile(r"\d+(?:\.\d+){1,5}\Z")
_HARDWARE_VOCABULARY = frozenset(
    {
        "adapter",
        "amd",
        "arc",
        "controller",
        "display",
        "geforce",
        "gpu",
        "graphics",
        "intel",
        "iris",
        "nvidia",
        "quadro",
        "radeon",
        "rtx",
        "tesla",
        "uhd",
        "video",
        "xe",
    }
)
_HARDWARE_DISPLAY_TOKENS = {
    "adapter": "Adapter",
    "amd": "AMD",
    "arc": "Arc",
    "controller": "Controller",
    "display": "Display",
    "geforce": "GeForce",
    "gpu": "GPU",
    "graphics": "Graphics",
    "intel": "Intel",
    "iris": "Iris",
    "nvidia": "NVIDIA",
    "quadro": "Quadro",
    "radeon": "Radeon",
    "rtx": "RTX",
    "tesla": "Tesla",
    "uhd": "UHD",
    "video": "Video",
    "xe": "Xe",
}
_SAFE_MODEL_TOKENS = frozenset({"ada", "ai", "max", "pro", "super", "ti", "xt", "xtx"})
_SAFE_MODEL_IDENTIFIER = re.compile(r"(?:\d{1,5}|[a-z]{1,2}\d{2,5})\Z", re.IGNORECASE)
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


@dataclass(frozen=True)
class _CimNode:
    node: HardwareNode
    raw_match_name: str


@dataclass(frozen=True)
class _NvidiaRow:
    raw_match_name: str
    name: str
    memory_bytes: int | None
    driver_version: str | None


def discover_windows_accelerators(command_runner: CommandRunner) -> WindowsAcceleratorDiscovery:
    cim_stdout, cim_reason = _run_bounded(command_runner, _cim_command())
    cim_nodes, cim_reason = _cim_nodes(cim_stdout) if cim_stdout is not None else ([], cim_reason)
    nodes = [item.node for item in cim_nodes]
    nvidia_stdout, nvidia_reason = _run_bounded(command_runner, _nvidia_smi_command())
    augmented_nodes = nodes
    nvidia_available = False
    if nvidia_stdout is not None:
        nvidia_rows = _nvidia_rows(nvidia_stdout)
        nvidia_available = bool(nvidia_rows)
        nvidia_reason = "cuda-driver-detected" if nvidia_available else "unparseable-output"
        augmented_nodes, unmatched_rows = _augment_nvidia_nodes(cim_nodes, nvidia_rows)
        augmented_nodes.extend(_nvidia_fallback_nodes(unmatched_rows))
    cim_available = bool(nodes)
    cim_observation_reason = "windows-cim-detected" if cim_available else cim_reason
    return WindowsAcceleratorDiscovery(
        nodes=tuple(augmented_nodes),
        adapters=(
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
    try:
        returncode = int(getattr(result, "returncode", 1))
        if returncode != 0:
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
    except (AttributeError, OSError, OverflowError, RecursionError, TypeError, UnicodeError, ValueError):
        return None, "probe-failed"


def _cim_nodes(stdout: str) -> tuple[list[_CimNode], str]:
    try:
        payload = json.loads(stdout)
    except (OverflowError, RecursionError, TypeError, UnicodeError, ValueError):
        return [], "unparseable-output"
    if payload == []:
        return [], "no-devices-detected"
    if isinstance(payload, dict):
        records = [payload]
    elif isinstance(payload, list) and payload and all(isinstance(record, dict) for record in payload):
        records = payload
    else:
        return [], "unparseable-output"
    nodes: list[_CimNode] = []
    seen_ids: set[str] = set()
    for record in records:
        node = _cim_node(record)
        if node is not None and node.node.node_id not in seen_ids:
            seen_ids.add(node.node.node_id)
            nodes.append(node)
    return (nodes, "windows-cim-detected") if nodes else ([], "unparseable-output")


def _cim_node(record: Any) -> _CimNode | None:
    if not isinstance(record, dict):
        return None
    pnp_device_id = record.get("PNPDeviceID")
    if not isinstance(pnp_device_id, str) or not pnp_device_id:
        return None
    canonical_identity = pnp_device_id.strip().upper()
    if not canonical_identity:
        return None
    vendor_match = _PCI_VENDOR.search(canonical_identity)
    device_match = _PCI_DEVICE.search(canonical_identity)
    memory = _positive_int(record.get("AdapterRAM"))
    reason_codes = ["windows-cim-detected", "runtime-unverified"]
    if memory is not None:
        reason_codes.append("memory-os-reported")
    raw_match_name = record.get("Name") if isinstance(record.get("Name"), str) else ""
    return _CimNode(
        node=HardwareNode(
            node_id="gpu:windows:" + hashlib.sha256(canonical_identity.encode()).hexdigest()[:16],
            kind="gpu",
            name=_sanitize_hardware_label(raw_match_name, fallback="windows-gpu"),
            backend="portable",
            memory_bytes=memory,
            vendor_id=vendor_match.group(1).lower() if vendor_match else None,
            device_id=device_match.group(1).lower() if device_match else None,
            architecture=_sanitize_hardware_optional(record.get("VideoProcessor")),
            driver_version=_sanitize_driver_version(record.get("DriverVersion")),
            dedicated_memory_bytes=memory,
            accelerator_apis=[],
            verification_state="detected",
            probe_source="windows-cim",
            reason_codes=reason_codes,
        ),
        raw_match_name=raw_match_name,
    )


def _nvidia_rows(stdout: str) -> list[_NvidiaRow]:
    rows: list[_NvidiaRow] = []
    for line in stdout.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 3 or not fields[0]:
            continue
        rows.append(
            _NvidiaRow(
                raw_match_name=fields[0],
                name=_sanitize_hardware_label(fields[0], fallback="nvidia-gpu"),
                memory_bytes=_mib_bytes(fields[1]),
                driver_version=_sanitize_driver_version(fields[2]),
            )
        )
    return rows


def _augment_nvidia_nodes(
    nodes: list[_CimNode], rows: list[_NvidiaRow]
) -> tuple[list[HardwareNode], list[tuple[int, _NvidiaRow]]]:
    augmented = [item.node for item in nodes]
    nvidia_indexes = [index for index, item in enumerate(nodes) if item.node.vendor_id == "10de"]
    unmatched = list(nvidia_indexes)
    unmatched_rows: list[tuple[int, _NvidiaRow]] = []
    for ordinal, row in enumerate(rows):
        normalized_name = _normalized_name(row.raw_match_name)
        match = next(
            (
                index
                for index in unmatched
                if _normalized_name(nodes[index].raw_match_name) == normalized_name
            ),
            None,
        )
        if match is None and ordinal < len(nvidia_indexes) and nvidia_indexes[ordinal] in unmatched:
            match = nvidia_indexes[ordinal]
        if match is None:
            unmatched_rows.append((ordinal, row))
            continue
        unmatched.remove(match)
        node = nodes[match].node
        updates: dict[str, Any] = {
            "backend": "cuda",
            "accelerator_apis": ["cuda"],
            "probe_source": "windows-cim+nvidia-smi",
            "reason_codes": [
                "windows-cim-detected",
                "cuda-driver-detected",
                "runtime-pack-unverified",
            ],
        }
        if row.memory_bytes is not None:
            updates["memory_bytes"] = row.memory_bytes
            updates["dedicated_memory_bytes"] = row.memory_bytes
        if row.driver_version is not None:
            updates["driver_version"] = row.driver_version
        augmented[match] = node.model_copy(update=updates)
    return augmented, unmatched_rows


def _nvidia_fallback_nodes(
    rows: list[tuple[int, _NvidiaRow]]
) -> list[HardwareNode]:
    return [
        HardwareNode(
            node_id=f"gpu:windows:nvidia-smi:{index}",
            kind="gpu",
            name=row.name,
            backend="cuda",
            memory_bytes=row.memory_bytes,
            vendor_id="10de",
            driver_version=row.driver_version,
            dedicated_memory_bytes=row.memory_bytes,
            accelerator_apis=["cuda"],
            verification_state="detected",
            probe_source="nvidia-smi",
            reason_codes=["cuda-driver-detected", "runtime-pack-unverified"],
        )
        for index, row in rows
    ]


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool) or (isinstance(value, str) and len(value) > 32):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    try:
        parsed = int(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return parsed if 0 < parsed <= _MAX_MEMORY_BYTES else None


def _mib_bytes(value: Any) -> int | None:
    if isinstance(value, bool) or (isinstance(value, str) and len(value) > 32):
        return None
    try:
        parsed_float = float(value)
        if not math.isfinite(parsed_float) or parsed_float <= 0:
            return None
        parsed = int(parsed_float)
    except (OverflowError, TypeError, ValueError):
        return None
    return parsed * 1024**2 if 0 < parsed <= _MAX_MEMORY_BYTES // 1024**2 else None


def _normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _sanitize_hardware_label(value: Any, *, fallback: str) -> str:
    return _sanitize_hardware_optional(value) or fallback


def _sanitize_hardware_optional(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    rendered = value
    if (
        not _SAFE_HARDWARE_PAYLOAD.fullmatch(rendered)
        or any(character in rendered for character in "\\/:=@\r\n\t")
        or _HOST_STYLE_PAYLOAD.search(rendered)
    ):
        return None
    normalized: list[str] = []
    has_hardware_token = False
    for token in re.findall(r"[A-Za-z0-9]+", rendered):
        lowered = token.lower()
        if lowered in _HARDWARE_VOCABULARY:
            normalized.append(_HARDWARE_DISPLAY_TOKENS[lowered])
            has_hardware_token = True
        elif lowered in _SAFE_MODEL_TOKENS:
            normalized.append(lowered.upper() if lowered == "ai" else lowered.title())
        elif _SAFE_MODEL_IDENTIFIER.fullmatch(token):
            normalized.append(token.upper() if token[0].isalpha() else token)
    return " ".join(normalized) if has_hardware_token and normalized else None


def _sanitize_driver_version(value: Any) -> str | None:
    if not isinstance(value, str) or len(value) > 32 or not _DRIVER_VERSION.fullmatch(value):
        return None
    return value
