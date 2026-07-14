from __future__ import annotations

import hashlib
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import median
from typing import Callable

from .schemas import HardwareCapabilityGraph, TransferEvidence, TransferRequest


class HardwareCalibrationLab:
    def __init__(self, executor: "TransferExecutor", *, calibration_bytes: int = 512 * 1024) -> None:
        if calibration_bytes <= 0 or calibration_bytes > 16 * 1024 * 1024:
            raise ValueError("calibration_bytes must be between 1 and 16777216")
        self.executor = executor
        self.calibration_bytes = calibration_bytes

    def calibrate(self, graph: HardwareCapabilityGraph) -> HardwareCapabilityGraph:
        node_by_id = {node.node_id: node for node in graph.nodes}
        links = []
        for link in graph.links:
            if link.kind == "memory-access":
                request = TransferRequest(kind="pageable", bytes=self.calibration_bytes, chunk_bytes=min(256 * 1024, self.calibration_bytes), repeat_count=3)
            elif link.kind == "storage-transfer":
                request = TransferRequest(
                    kind="storage",
                    bytes=self.calibration_bytes,
                    chunk_bytes=min(256 * 1024, self.calibration_bytes),
                    repeat_count=3,
                    direction="storage-roundtrip",
                )
            else:
                target = node_by_id.get(link.target_node_id)
                backend = target.backend if target is not None else "portable"
                request = TransferRequest(
                    kind="accelerator",
                    bytes=self.calibration_bytes,
                    chunk_bytes=min(256 * 1024, self.calibration_bytes),
                    repeat_count=3,
                    backend=backend,
                    direction="host-to-device",
                )
            evidence = self.executor.execute(request)
            measured = evidence.effective_bandwidth_gib_s if evidence.status == "completed" else None
            links.append(link.model_copy(update={"measured_bandwidth_gib_s": measured}))
        return graph.model_copy(update={"links": links})


class TransferExecutor:
    def __init__(self, *, storage_dir: str | Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        request: TransferRequest,
        cancel_check: Callable[[], bool] | None = None,
    ) -> TransferEvidence:
        if request.kind == "accelerator":
            return self._accelerator(request, cancel_check)
        source = bytes((index * 31 + 17) % 251 for index in range(request.bytes))
        expected = hashlib.sha256(source).hexdigest()
        durations: list[float] = []
        bytes_moved = 0
        checksums: list[str] = []
        overlaps: list[float] = []
        for _ in range(request.repeat_count):
            if cancel_check is not None and cancel_check():
                return self._result(request, "preempted", durations, bytes_moved, False, overlaps, ["serving-preempted"])
            started = time.perf_counter()
            if request.kind == "storage":
                output, moved = self._storage_roundtrip(source, request.chunk_bytes, cancel_check)
            elif request.kind == "double-buffered":
                output, moved, overlap = self._double_buffered(source, request.chunk_bytes, request.compute_iterations, cancel_check)
                overlaps.append(overlap)
            else:
                output, moved = self._pageable(source, request.chunk_bytes, cancel_check)
            elapsed = max((time.perf_counter() - started) * 1000, 1e-9)
            if output is None:
                return self._result(request, "preempted", durations, bytes_moved, False, overlaps, ["serving-preempted"])
            durations.append(elapsed)
            bytes_moved += moved
            checksums.append(hashlib.sha256(output).hexdigest())
        equivalent = bool(checksums) and all(item == expected for item in checksums)
        return self._result(
            request,
            "completed" if equivalent else "failed",
            durations,
            bytes_moved,
            equivalent,
            overlaps,
            [] if equivalent else ["checksum-mismatch"],
        )

    def _pageable(self, source: bytes, chunk_bytes: int, cancel_check: Callable[[], bool] | None):
        target = bytearray(len(source))
        for offset in range(0, len(source), chunk_bytes):
            if cancel_check is not None and cancel_check():
                return None, 0
            target[offset : offset + chunk_bytes] = source[offset : offset + chunk_bytes]
        return bytes(target), len(source)

    def _storage_roundtrip(self, source: bytes, chunk_bytes: int, cancel_check: Callable[[], bool] | None):
        descriptor, name = tempfile.mkstemp(prefix="transfer-", dir=self.storage_dir)
        path = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                for offset in range(0, len(source), chunk_bytes):
                    if cancel_check is not None and cancel_check():
                        return None, 0
                    handle.write(source[offset : offset + chunk_bytes])
                handle.flush()
                os.fsync(handle.fileno())
            target = bytearray()
            with path.open("rb") as handle:
                while True:
                    if cancel_check is not None and cancel_check():
                        return None, 0
                    block = handle.read(chunk_bytes)
                    if not block:
                        break
                    target.extend(block)
            return bytes(target), len(source) * 2
        finally:
            path.unlink(missing_ok=True)

    def _double_buffered(
        self,
        source: bytes,
        chunk_bytes: int,
        compute_iterations: int,
        cancel_check: Callable[[], bool] | None,
    ):
        chunks = [source[offset : offset + chunk_bytes] for offset in range(0, len(source), chunk_bytes)]
        target = bytearray()
        copy_seconds = 0.0
        compute_seconds = 0.0

        def copy_chunk(chunk: bytes) -> bytes:
            started = time.perf_counter()
            copied = bytes(bytearray(chunk))
            nonlocal copy_seconds
            copy_seconds += time.perf_counter() - started
            return copied

        def compute(chunk: bytes) -> None:
            started = time.perf_counter()
            digest = hashlib.sha256(chunk).digest()
            for _ in range(compute_iterations):
                digest = hashlib.sha256(digest).digest()
            nonlocal compute_seconds
            compute_seconds += time.perf_counter() - started

        combined_started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="nexus-transfer") as pool:
            pending = None
            for chunk in chunks:
                if cancel_check is not None and cancel_check():
                    return None, 0, 0.0
                next_copy = pool.submit(copy_chunk, chunk)
                if pending is not None:
                    copied = pending.result()
                    compute(copied)
                    target.extend(copied)
                pending = next_copy
            if pending is not None:
                copied = pending.result()
                compute(copied)
                target.extend(copied)
        combined = max(time.perf_counter() - combined_started, 1e-9)
        potential = min(copy_seconds, compute_seconds)
        overlap = 0.0 if potential <= 0 else min(1.0, max(0.0, (copy_seconds + compute_seconds - combined) / potential))
        return bytes(target), len(source), overlap

    def _accelerator(self, request: TransferRequest, cancel_check: Callable[[], bool] | None) -> TransferEvidence:
        if cancel_check is not None and cancel_check():
            return self._result(request, "preempted", [], 0, False, [], ["serving-preempted"])
        try:
            import torch
        except ImportError:
            return self._result(request, "backend-unavailable", [], 0, False, [], ["torch-unavailable"])
        if request.backend == "metal":
            mps_available = bool(getattr(getattr(torch, "backends", None), "mps", None)) and torch.backends.mps.is_available()
            if not mps_available:
                return self._result(request, "backend-unavailable", [], 0, False, [], ["metal-unavailable"])
            source = torch.arange(request.bytes, dtype=torch.int64).remainder(251).to(torch.uint8)
            expected = hashlib.sha256(source.numpy().tobytes()).hexdigest()
            durations: list[float] = []
            checksums: list[str] = []
            for _ in range(request.repeat_count):
                started = time.perf_counter()
                device = source.to("mps")
                returned = device.to("cpu")
                torch.mps.synchronize()
                durations.append(max((time.perf_counter() - started) * 1000, 1e-9))
                checksums.append(hashlib.sha256(returned.numpy().tobytes()).hexdigest())
            equivalent = all(item == expected for item in checksums)
            return self._result(
                request,
                "completed" if equivalent else "failed",
                durations,
                request.bytes * request.repeat_count * 2,
                equivalent,
                [0.0],
                [] if equivalent else ["checksum-mismatch"],
                synchronization_count=request.repeat_count,
            )
        if request.backend not in {"cuda", "rocm"} or not torch.cuda.is_available():
            return self._result(request, "backend-unavailable", [], 0, False, [], ["accelerator-unavailable"])
        source = torch.arange(request.bytes, dtype=torch.int64).remainder(251).to(torch.uint8).pin_memory()
        expected = hashlib.sha256(source.numpy().tobytes()).hexdigest()
        durations: list[float] = []
        checksums: list[str] = []
        stream = torch.cuda.Stream()
        for _ in range(request.repeat_count):
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            with torch.cuda.stream(stream):
                start.record(stream)
                device = source.to("cuda", non_blocking=True)
                returned = device.to("cpu", non_blocking=True)
                end.record(stream)
            stream.synchronize()
            durations.append(max(float(start.elapsed_time(end)), 1e-9))
            checksums.append(hashlib.sha256(returned.numpy().tobytes()).hexdigest())
        equivalent = all(item == expected for item in checksums)
        return self._result(
            request,
            "completed" if equivalent else "failed",
            durations,
            request.bytes * request.repeat_count * 2,
            equivalent,
            [0.0],
            [] if equivalent else ["checksum-mismatch"],
            synchronization_count=request.repeat_count,
        )

    @staticmethod
    def _result(
        request: TransferRequest,
        status: str,
        durations: list[float],
        bytes_moved: int,
        equivalent: bool,
        overlaps: list[float],
        reasons: list[str],
        synchronization_count: int = 0,
    ) -> TransferEvidence:
        total_seconds = sum(durations) / 1000
        bandwidth = bytes_moved / total_seconds / 1024**3 if total_seconds > 0 else 0.0
        return TransferEvidence(
            status=status,
            kind=request.kind,
            backend=request.backend,
            direction=request.direction,
            bytes_per_repeat=request.bytes,
            bytes_moved=bytes_moved,
            chunk_bytes=request.chunk_bytes,
            repeat_count=len(durations),
            duration_ms=durations,
            cold_duration_ms=durations[0] if durations else None,
            warm_duration_ms=median(durations[1:] or durations) if durations else None,
            effective_bandwidth_gib_s=max(bandwidth, 0.0),
            overlap_ratio=sum(overlaps) / len(overlaps) if overlaps else 0.0,
            synchronization_count=synchronization_count,
            checksum_equivalent=equivalent,
            reason_codes=reasons,
        )
