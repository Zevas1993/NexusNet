from __future__ import annotations

import hashlib
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from threading import RLock

import torch

from .manifest import ExpertTensorManifest


class ExpertIntegrityError(RuntimeError):
    pass


TensorMap = dict[str, torch.Tensor]


class TieredExpertStore:
    """Digest-verified storage, RAM, and device caches for expert tensors."""

    def __init__(
        self,
        manifest: ExpertTensorManifest,
        *,
        ram_slots: int,
        hot_slots: int,
    ) -> None:
        if ram_slots < 0 or hot_slots < 0:
            raise ValueError("cache slot counts must be non-negative")
        self.manifest = manifest
        self.ram_slots = ram_slots
        self.hot_slots = hot_slots
        self._ram: OrderedDict[int, TensorMap] = OrderedDict()
        self._hot: OrderedDict[tuple[int, str], TensorMap] = OrderedDict()
        self._pinned_hot_keys: set[tuple[int, str]] = set()
        self._lock = RLock()
        self._prefetch_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="nexus-moe-prefetch")
        self._prefetched: set[tuple[int, str]] = set()
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
        }
        self._validate_manifest_paths()

    def acquire(
        self,
        expert_id: int,
        device: torch.device,
        *,
        _prefetch: bool = False,
    ) -> TensorMap:
        key = (expert_id, str(device))
        with self._lock:
            hot = self._hot.get(key)
            if hot is not None:
                self._metrics["hot_hits"] += 1
                self._mark_prefetch_hit(key, is_prefetch=_prefetch)
                self._hot.move_to_end(key)
                return hot

            host = self._ram.get(expert_id)
            if host is not None:
                self._metrics["ram_hits"] += 1
                self._mark_prefetch_hit(key, is_prefetch=_prefetch)
                self._ram.move_to_end(expert_id)
            else:
                host = self._load_from_storage(expert_id)
                self._insert_ram(expert_id, host)

            if self.hot_slots == 0:
                return host if device.type == "cpu" else self._to_device(host, device)
            device_tensors = host if device.type == "cpu" else self._to_device(host, device)
            self._hot[key] = device_tensors
            self._hot.move_to_end(key)
            self._trim_hot()
            return device_tensors

    def pin(self, expert_ids: tuple[int, ...], device: torch.device) -> None:
        unique_ids = tuple(dict.fromkeys(expert_ids))
        if len(unique_ids) > self.hot_slots:
            raise ValueError("pinned expert count exceeds hot slot budget")
        device_ref = str(device)
        with self._lock:
            self._pinned_hot_keys = {(expert_id, device_ref) for expert_id in unique_ids}
        for expert_id in unique_ids:
            self.acquire(expert_id, device)
        with self._lock:
            self._trim_hot()

    def prefetch(self, expert_id: int, device: torch.device) -> Future[TensorMap]:
        key = (expert_id, str(device))
        with self._lock:
            self._metrics["prefetch_requests"] += 1
            self._prefetched.add(key)

        def load() -> TensorMap:
            try:
                return self.acquire(expert_id, device, _prefetch=True)
            except Exception:
                with self._lock:
                    self._prefetched.discard(key)
                    self._metrics["prefetch_failures"] += 1
                raise

        return self._prefetch_executor.submit(load)

    def close(self) -> None:
        self._prefetch_executor.shutdown(wait=True, cancel_futures=True)

    def evidence(self) -> dict[str, int | str]:
        with self._lock:
            return {
                "manifest_ref": self.manifest.manifest_id,
                **self._metrics,
                "ram_occupancy": len(self._ram),
                "hot_occupancy": len(self._hot),
                "pinned_hot_experts": sorted(expert_id for expert_id, _ in self._pinned_hot_keys),
            }

    def _load_from_storage(self, expert_id: int) -> TensorMap:
        try:
            from safetensors.torch import load_file
        except ImportError as exc:
            raise RuntimeError("safetensors is required for tiered expert loading") from exc
        record = self.manifest.record(expert_id)
        path = self._record_path(record.path)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != record.size_bytes or digest != record.sha256:
            raise ExpertIntegrityError(
                f"expert {expert_id} digest mismatch for manifest {self.manifest.manifest_id}"
            )
        self._metrics["storage_misses"] += 1
        self._metrics["bytes_read"] += len(data)
        tensors = load_file(str(path), device="cpu")
        if tuple(sorted(tensors)) != record.tensor_names:
            raise ExpertIntegrityError(f"expert {expert_id} tensor names do not match manifest")
        return tensors

    def _insert_ram(self, expert_id: int, tensors: TensorMap) -> None:
        if self.ram_slots == 0:
            return
        self._ram[expert_id] = tensors
        self._ram.move_to_end(expert_id)
        while len(self._ram) > self.ram_slots:
            self._ram.popitem(last=False)
            self._metrics["ram_evictions"] += 1

    def _mark_prefetch_hit(self, key: tuple[int, str], *, is_prefetch: bool) -> None:
        if not is_prefetch and key in self._prefetched:
            self._prefetched.remove(key)
            self._metrics["prefetch_hits"] += 1

    def _trim_hot(self) -> None:
        while len(self._hot) > self.hot_slots:
            victim = next(
                (key for key in self._hot if key not in self._pinned_hot_keys),
                None,
            )
            if victim is None:
                raise RuntimeError("hot cache exceeds slot budget with only pinned entries")
            del self._hot[victim]
            self._metrics["hot_evictions"] += 1

    @staticmethod
    def _to_device(tensors: TensorMap, device: torch.device) -> TensorMap:
        return {name: tensor.to(device=device, non_blocking=True) for name, tensor in tensors.items()}

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
        path = (root / relative).resolve()
        if path.parent != root:
            raise ExpertIntegrityError("expert path must remain inside manifest root")
        return path
