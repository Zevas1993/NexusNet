from __future__ import annotations

import hashlib
import os
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import torch

from .manifest import ExpertIntegrityError, ExpertTensorManifest


TensorMap = dict[str, torch.Tensor]
CacheKey = tuple[int, str, str]


class TieredExpertStore:
    """Digest-verified storage, RAM, and device caches for expert tensors."""

    def __init__(
        self,
        manifest: ExpertTensorManifest,
        *,
        ram_slots: int,
        hot_slots: int,
        max_shard_bytes: int = 2 * 1024**3,
        max_prefetch_inflight: int = 4,
    ) -> None:
        if ram_slots < 0 or hot_slots < 0:
            raise ValueError("cache slot counts must be non-negative")
        if max_shard_bytes <= 0:
            raise ValueError("max_shard_bytes must be positive")
        if max_prefetch_inflight <= 0:
            raise ValueError("max_prefetch_inflight must be positive")
        self.manifest = manifest
        self.ram_slots = ram_slots
        self.hot_slots = hot_slots
        self.max_shard_bytes = max_shard_bytes
        self.max_prefetch_inflight = max_prefetch_inflight
        self._ram: OrderedDict[int, TensorMap] = OrderedDict()
        self._hot: OrderedDict[CacheKey, TensorMap] = OrderedDict()
        self._pinned_hot_keys: set[CacheKey] = set()
        self._leases: dict[CacheKey, int] = {}
        self._host_inflight: dict[int, Future[TensorMap]] = {}
        self._acquire_inflight: dict[CacheKey, Future[TensorMap]] = {}
        self._lock = RLock()
        self._prefetch_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="nexus-moe-prefetch")
        self._prefetched: set[CacheKey] = set()
        self._prefetch_inflight: dict[CacheKey, Future[TensorMap]] = {}
        self._prefetch_workers: set[Future[TensorMap]] = set()
        self._metrics = {
            "storage_misses": 0,
            "ram_hits": 0,
            "hot_hits": 0,
            "ram_evictions": 0,
            "hot_evictions": 0,
            "bytes_read": 0,
            "prefetch_requests": 0,
            "prefetch_hits": 0,
            "prefetch_failures": 0,
            "prefetch_cancellations": 0,
            "prefetch_coalesced": 0,
            "prefetch_wasted": 0,
            "load_failures": 0,
        }
        self._validate_manifest_paths()

    def acquire(
        self,
        expert_id: int,
        device: torch.device,
        *,
        dtype: torch.dtype | None = None,
        _prefetch: bool = False,
    ) -> TensorMap:
        key = self._cache_key(expert_id, device, dtype)
        with self._lock:
            hot = self._hot.get(key)
            if hot is not None:
                self._metrics["hot_hits"] += 1
                self._mark_prefetch_hit(key, is_prefetch=_prefetch)
                self._hot.move_to_end(key)
                return hot
            inflight = self._acquire_inflight.get(key)
            owner = inflight is None
            if owner:
                inflight = Future()
                self._acquire_inflight[key] = inflight
        assert inflight is not None
        if owner:
            try:
                host = self._host_tensors(expert_id)
                device_tensors = self._to_device(host, device, dtype)
                with self._lock:
                    if self.hot_slots:
                        self._hot[key] = device_tensors
                        self._hot.move_to_end(key)
                        self._trim_hot()
                    inflight.set_result(device_tensors)
            except BaseException as exc:
                inflight.set_exception(exc)
            finally:
                with self._lock:
                    if self._acquire_inflight.get(key) is inflight:
                        self._acquire_inflight.pop(key, None)
        result = inflight.result()
        with self._lock:
            self._mark_prefetch_hit(key, is_prefetch=_prefetch)
        return result

    @contextmanager
    def lease(
        self,
        expert_id: int,
        device: torch.device,
        dtype: torch.dtype | None = None,
    ):
        key = self._cache_key(expert_id, device, dtype)
        tensors = self.acquire(expert_id, device, dtype=dtype)
        with self._lock:
            self._leases[key] = self._leases.get(key, 0) + 1
        try:
            yield tensors
        finally:
            with self._lock:
                remaining = self._leases.get(key, 0) - 1
                if remaining > 0:
                    self._leases[key] = remaining
                else:
                    self._leases.pop(key, None)
                self._trim_hot()
                self._trim_ram()

    def pin(
        self,
        expert_ids: tuple[int, ...],
        device: torch.device,
        dtype: torch.dtype | None = None,
    ) -> None:
        unique_ids = tuple(dict.fromkeys(expert_ids))
        if len(unique_ids) > self.hot_slots:
            raise ValueError("pinned expert count exceeds hot slot budget")
        with self._lock:
            self._pinned_hot_keys = {
                self._cache_key(expert_id, device, dtype) for expert_id in unique_ids
            }
        for expert_id in unique_ids:
            self.acquire(expert_id, device, dtype=dtype)
        with self._lock:
            self._trim_hot()

    def prefetch(
        self,
        expert_id: int,
        device: torch.device,
        dtype: torch.dtype | None = None,
    ) -> Future[TensorMap]:
        key = self._cache_key(expert_id, device, dtype)
        with self._lock:
            self._metrics["prefetch_requests"] += 1
            existing = self._prefetch_inflight.get(key)
            if existing is not None and not existing.done():
                self._metrics["prefetch_coalesced"] += 1
                return existing
            if len(self._prefetch_inflight) >= self.max_prefetch_inflight:
                rejected: Future[TensorMap] = Future()
                rejected.cancel()
                self._metrics["prefetch_cancellations"] += 1
                return rejected
            self._prefetched.add(key)
            reservation: Future[TensorMap] = Future()
            self._prefetch_inflight[key] = reservation

        def load() -> TensorMap:
            try:
                return self.acquire(expert_id, device, dtype=dtype, _prefetch=True)
            except Exception:
                with self._lock:
                    self._prefetched.discard(key)
                    self._metrics["prefetch_failures"] += 1
                raise

        try:
            worker = self._prefetch_executor.submit(load)
        except BaseException as exc:
            with self._lock:
                self._prefetch_inflight.pop(key, None)
                self._prefetched.discard(key)
                self._metrics["prefetch_failures"] += 1
            reservation.set_exception(exc)
            return reservation
        with self._lock:
            self._prefetch_workers.add(worker)

        def transfer(done: Future[TensorMap]) -> None:
            with self._lock:
                self._prefetch_workers.discard(done)
            if reservation.done():
                return
            if done.cancelled():
                reservation.cancel()
                return
            error = done.exception()
            if error is not None:
                reservation.set_exception(error)
            else:
                reservation.set_result(done.result())

        def cleanup(done: Future[TensorMap]) -> None:
            with self._lock:
                if self._prefetch_inflight.get(key) is done:
                    self._prefetch_inflight.pop(key, None)
                if done.cancelled():
                    self._prefetched.discard(key)
                    self._metrics["prefetch_cancellations"] += 1
            if not done.cancelled():
                done.exception()

        worker.add_done_callback(transfer)
        reservation.add_done_callback(cleanup)
        return reservation

    def close(self) -> None:
        with self._lock:
            futures = tuple(self._prefetch_inflight.values())
        for future in futures:
            future.cancel()
        self._prefetch_executor.shutdown(wait=True, cancel_futures=True)

    def evidence(self) -> dict[str, int | str]:
        with self._lock:
            return {
                "manifest_ref": self.manifest.manifest_id,
                **self._metrics,
                "ram_occupancy": len(self._ram),
                "hot_occupancy": len(self._hot),
                "pinned_hot_experts": sorted(
                    {expert_id for expert_id, _, _ in self._pinned_hot_keys}
                ),
                "active_leases": sum(self._leases.values()),
                "inflight_prefetches": len(self._prefetch_inflight),
            }

    def _load_from_storage(self, expert_id: int) -> TensorMap:
        try:
            from safetensors.torch import load
        except ImportError as exc:
            raise RuntimeError("safetensors is required for tiered expert loading") from exc
        record = self.manifest.record(expert_id)
        if record.size_bytes > self.max_shard_bytes:
            raise ExpertIntegrityError(
                f"expert {expert_id} exceeds configured bound of {self.max_shard_bytes} bytes"
            )
        path = self._record_path(record.path)
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path, flags)
        except OSError as exc:
            raise ExpertIntegrityError(f"expert {expert_id} could not be opened safely") from exc
        try:
            stat = os.fstat(descriptor)
            if stat.st_size != record.size_bytes or stat.st_size > self.max_shard_bytes:
                raise ExpertIntegrityError(
                    f"expert {expert_id} size does not match manifest or configured bound"
                )
            with os.fdopen(descriptor, "rb", closefd=False) as handle:
                data = handle.read(self.max_shard_bytes + 1)
        finally:
            os.close(descriptor)
        if len(data) > self.max_shard_bytes:
            raise ExpertIntegrityError(f"expert {expert_id} exceeds configured bound")
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != record.size_bytes or digest != record.sha256:
            raise ExpertIntegrityError(
                f"expert {expert_id} digest mismatch for manifest {self.manifest.manifest_id}"
            )
        with self._lock:
            self._metrics["storage_misses"] += 1
            self._metrics["bytes_read"] += len(data)
        tensors = load(data)
        if tuple(sorted(tensors)) != record.tensor_names:
            raise ExpertIntegrityError(f"expert {expert_id} tensor names do not match manifest")
        return tensors

    def _host_tensors(self, expert_id: int) -> TensorMap:
        with self._lock:
            host = self._ram.get(expert_id)
            if host is not None:
                self._metrics["ram_hits"] += 1
                self._ram.move_to_end(expert_id)
                return host
            inflight = self._host_inflight.get(expert_id)
            owner = inflight is None
            if owner:
                inflight = Future()
                self._host_inflight[expert_id] = inflight
        assert inflight is not None
        if owner:
            try:
                host = self._load_from_storage(expert_id)
                with self._lock:
                    self._insert_ram(expert_id, host)
                    inflight.set_result(host)
            except BaseException as exc:
                with self._lock:
                    self._metrics["load_failures"] += 1
                inflight.set_exception(exc)
            finally:
                with self._lock:
                    if self._host_inflight.get(expert_id) is inflight:
                        self._host_inflight.pop(expert_id, None)
        return inflight.result()

    def _insert_ram(self, expert_id: int, tensors: TensorMap) -> None:
        if self.ram_slots == 0:
            return
        self._ram[expert_id] = tensors
        self._ram.move_to_end(expert_id)
        self._trim_ram()

    def _mark_prefetch_hit(self, key: CacheKey, *, is_prefetch: bool) -> None:
        if not is_prefetch and key in self._prefetched:
            self._prefetched.remove(key)
            self._metrics["prefetch_hits"] += 1

    def _trim_hot(self) -> None:
        while len(self._hot) > self.hot_slots:
            victim = next(
                (
                    key
                    for key in self._hot
                    if key not in self._pinned_hot_keys and self._leases.get(key, 0) == 0
                ),
                None,
            )
            if victim is None:
                return
            if victim in self._prefetched:
                self._prefetched.remove(victim)
                self._metrics["prefetch_wasted"] += 1
            del self._hot[victim]
            self._metrics["hot_evictions"] += 1

    def _trim_ram(self) -> None:
        while len(self._ram) > self.ram_slots:
            victim = next(
                (
                    expert_id
                    for expert_id in self._ram
                    if not any(
                        leased_expert == expert_id and count > 0
                        for (leased_expert, _, _), count in self._leases.items()
                    )
                ),
                None,
            )
            if victim is None:
                return
            unused_prefetches = {
                key
                for key in self._prefetched
                if key[0] == victim and key not in self._hot
            }
            self._prefetched.difference_update(unused_prefetches)
            self._metrics["prefetch_wasted"] += len(unused_prefetches)
            del self._ram[victim]
            self._metrics["ram_evictions"] += 1

    @staticmethod
    def _to_device(
        tensors: TensorMap,
        device: torch.device,
        dtype: torch.dtype | None,
    ) -> TensorMap:
        return {
            name: tensor.to(
                device=device,
                dtype=dtype if tensor.is_floating_point() else tensor.dtype,
                non_blocking=True,
            )
            for name, tensor in tensors.items()
        }

    @staticmethod
    def _cache_key(
        expert_id: int,
        device: torch.device,
        dtype: torch.dtype | None,
    ) -> CacheKey:
        return (expert_id, str(device), str(dtype) if dtype is not None else "source")

    def _validate_manifest_paths(self) -> None:
        seen: set[int] = set()
        for record in self.manifest.experts:
            if record.expert_id in seen:
                raise ValueError("manifest contains duplicate expert ids")
            seen.add(record.expert_id)
            self._record_path(record.path)

    def _record_path(self, relative_path: str) -> Path:
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ExpertIntegrityError("expert path must remain inside manifest root")
        root = Path(self.manifest.root_dir).resolve()
        candidate = root / relative
        if candidate.is_symlink():
            raise ExpertIntegrityError("expert path cannot be a symbolic link")
        path = candidate.resolve()
        if path.parent != root:
            raise ExpertIntegrityError("expert path must remain inside manifest root")
        return path
