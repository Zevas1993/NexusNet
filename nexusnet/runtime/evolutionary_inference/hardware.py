from __future__ import annotations

import ctypes
import hashlib
import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .schemas import (
    AcceleratorAdapterObservation,
    HardwareCapabilityGraph,
    HardwareLink,
    HardwareNode,
)


CommandRunner = Callable[[list[str], float], Any]


class HardwareCapabilityDiscoverer:
    def __init__(
        self,
        *,
        command_runner: CommandRunner | None = None,
        system_name: str | None = None,
        machine: str | None = None,
        processor_name: str | None = None,
        logical_cpu_count: int | None = None,
        total_memory_bytes: int | None = None,
        disk_usage_reader: Callable[[str], Any] | None = None,
        storage_root: str | None = None,
    ) -> None:
        self._command_runner = command_runner or _run_command
        self._system_name = system_name or platform.system() or "Unknown"
        self._machine = machine or platform.machine() or "unknown"
        self._processor_name = processor_name or platform.processor() or self._machine
        self._logical_cpu_count = logical_cpu_count or os.cpu_count() or 1
        self._total_memory_bytes = total_memory_bytes or _total_memory_bytes()
        self._disk_usage_reader = disk_usage_reader or shutil.disk_usage
        self._storage_root = storage_root or Path.cwd().anchor or str(Path.cwd())

    def discover(self) -> HardwareCapabilityGraph:
        disk = self._disk_usage_reader(self._storage_root)
        nodes = [
            HardwareNode(
                node_id="cpu:0",
                kind="cpu",
                name=_clean_label(self._processor_name, fallback=self._machine),
                logical_units=self._logical_cpu_count,
                capabilities=[self._machine.lower(), "portable-compute"],
            ),
            HardwareNode(
                node_id="ram:0",
                kind="system-ram",
                name="system-memory",
                memory_bytes=self._total_memory_bytes,
                capabilities=["pageable-host-memory"],
            ),
            HardwareNode(
                node_id="storage:0",
                kind="storage",
                name="primary-storage",
                memory_bytes=int(disk.total),
                capabilities=["persistent-artifact-storage"],
            ),
        ]
        links = [
            HardwareLink(source_node_id="cpu:0", target_node_id="ram:0", kind="memory-access"),
            HardwareLink(source_node_id="ram:0", target_node_id="storage:0", kind="storage-transfer"),
        ]
        adapters: list[AcceleratorAdapterObservation] = []
        for backend, probe in (("cuda", self._probe_cuda), ("rocm", self._probe_rocm), ("metal", self._probe_metal)):
            discovered, observation = probe()
            adapters.append(observation)
            for node in discovered:
                nodes.append(node)
                links.append(
                    HardwareLink(
                        source_node_id="ram:0",
                        target_node_id=node.node_id,
                        kind="accelerator-transfer",
                    )
                )
        return HardwareCapabilityGraph(
            host_fingerprint=self._host_fingerprint(),
            collected_at=datetime.now(timezone.utc),
            nodes=nodes,
            links=links,
            adapters=adapters,
        )

    def _host_fingerprint(self) -> str:
        memory_bucket_gib = max(1, self._total_memory_bytes // 1024**3)
        canonical = "|".join(
            (
                self._system_name.lower(),
                self._machine.lower(),
                _clean_label(self._processor_name, fallback=self._machine).lower(),
                str(self._logical_cpu_count),
                str(memory_bucket_gib),
            )
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]

    def _probe_cuda(self) -> tuple[list[HardwareNode], AcceleratorAdapterObservation]:
        command = [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
        result, reason = self._safe_command(command)
        if result is None:
            return [], AcceleratorAdapterObservation(backend="cuda", available=False, reason_code=reason)
        nodes: list[HardwareNode] = []
        for index, line in enumerate(str(result.stdout).splitlines()):
            fields = [field.strip() for field in line.split(",")]
            if len(fields) < 2:
                continue
            try:
                memory_bytes = int(float(fields[1])) * 1024**2
            except ValueError:
                continue
            nodes.append(
                HardwareNode(
                    node_id=f"gpu:cuda:{index}",
                    kind="gpu",
                    name=_clean_label(fields[0], fallback="cuda-gpu"),
                    backend="cuda",
                    memory_bytes=memory_bytes,
                    capabilities=["cuda", "device-memory"],
                )
            )
        available = bool(nodes)
        return nodes, AcceleratorAdapterObservation(
            backend="cuda",
            available=available,
            reason_code="available" if available else "unparseable-output",
            device_count=len(nodes),
        )

    def _probe_rocm(self) -> tuple[list[HardwareNode], AcceleratorAdapterObservation]:
        if self._system_name.lower() != "linux":
            return [], AcceleratorAdapterObservation(backend="rocm", available=False, reason_code="unsupported-platform")
        result, reason = self._safe_command(["rocm-smi", "--showproductname", "--showmeminfo", "vram", "--json"])
        if result is None:
            return [], AcceleratorAdapterObservation(backend="rocm", available=False, reason_code=reason)
        try:
            payload = json.loads(result.stdout)
        except (TypeError, json.JSONDecodeError):
            payload = {}
        nodes = _rocm_nodes(payload)
        return nodes, AcceleratorAdapterObservation(
            backend="rocm",
            available=bool(nodes),
            reason_code="available" if nodes else "unparseable-output",
            device_count=len(nodes),
        )

    def _probe_metal(self) -> tuple[list[HardwareNode], AcceleratorAdapterObservation]:
        if self._system_name.lower() != "darwin":
            return [], AcceleratorAdapterObservation(backend="metal", available=False, reason_code="unsupported-platform")
        result, reason = self._safe_command(["system_profiler", "SPDisplaysDataType", "-json"])
        if result is None:
            return [], AcceleratorAdapterObservation(backend="metal", available=False, reason_code=reason)
        try:
            payload = json.loads(result.stdout)
        except (TypeError, json.JSONDecodeError):
            payload = {}
        displays = payload.get("SPDisplaysDataType", []) if isinstance(payload, dict) else []
        nodes = [
            HardwareNode(
                node_id=f"gpu:metal:{index}",
                kind="gpu",
                name=_clean_label(str(item.get("sppci_model", "metal-gpu")), fallback="metal-gpu"),
                backend="metal",
                capabilities=["metal", "unified-memory"],
            )
            for index, item in enumerate(displays)
            if isinstance(item, dict)
        ]
        return nodes, AcceleratorAdapterObservation(
            backend="metal",
            available=bool(nodes),
            reason_code="available" if nodes else "unparseable-output",
            device_count=len(nodes),
        )

    def _safe_command(self, command: list[str]) -> tuple[Any | None, str]:
        try:
            result = self._command_runner(command, 2.0)
        except FileNotFoundError:
            return None, "tool-not-found"
        except subprocess.TimeoutExpired:
            return None, "timeout"
        except (OSError, ValueError):
            return None, "probe-failed"
        if int(getattr(result, "returncode", 1)) != 0:
            return None, "probe-failed"
        return result, "available"


def _run_command(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def _clean_label(value: str, *, fallback: str) -> str:
    cleaned = " ".join(value.replace("\x00", " ").split()).strip()
    return cleaned[:120] or fallback


def _total_memory_bytes() -> int:
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total_physical", ctypes.c_ulonglong),
                ("available_physical", ctypes.c_ulonglong),
                ("total_page_file", ctypes.c_ulonglong),
                ("available_page_file", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("available_virtual", ctypes.c_ulonglong),
                ("available_extended_virtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.total_physical)
    try:
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, OSError, ValueError):
        return 1 * 1024**3


def _rocm_nodes(payload: Any) -> list[HardwareNode]:
    if not isinstance(payload, dict):
        return []
    nodes: list[HardwareNode] = []
    for index, value in enumerate(payload.values()):
        if not isinstance(value, dict):
            continue
        name = next((str(item) for key, item in value.items() if "card series" in key.lower()), "rocm-gpu")
        memory = next((item for key, item in value.items() if "total memory" in key.lower()), None)
        try:
            memory_bytes = int(memory) if memory is not None else None
        except (TypeError, ValueError):
            memory_bytes = None
        nodes.append(
            HardwareNode(
                node_id=f"gpu:rocm:{index}",
                kind="gpu",
                name=_clean_label(name, fallback="rocm-gpu"),
                backend="rocm",
                memory_bytes=memory_bytes,
                capabilities=["rocm", "device-memory"],
            )
        )
    return nodes
