from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import tempfile
from threading import RLock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator, model_validator

from .contracts import WorkloadKind


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+-]{0,255}$")
_PACK_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_DEVICE_FINGERPRINT = re.compile(r"^device::[0-9a-f]{16,64}$")
_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MAX_LEDGER_BYTES = 16 * 1024 * 1024
_MAX_RECORDS = 4096
_PATH_LOCK_GUARD = RLock()
_PATH_LOCKS: dict[str, RLock] = {}


def _path_lock(path: Path) -> RLock:
    key = os.path.normcase(str(path.resolve(strict=False)))
    with _PATH_LOCK_GUARD:
        return _PATH_LOCKS.setdefault(key, RLock())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _validate_aware(value: datetime, *, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value


class CalibrationKey(BaseModel):
    """Exact identity of one measured route and workload profile."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    route_id: StrictStr = Field(min_length=1, max_length=256)
    pack_id: StrictStr = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    pack_version: StrictStr = Field(min_length=1, max_length=128)
    worker_version: StrictStr = Field(min_length=1, max_length=128)
    device_fingerprint: StrictStr = Field(pattern=r"^device::[0-9a-f]{16,64}$")
    driver_version: StrictStr = Field(min_length=1, max_length=128)
    model_hash: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")
    workload: WorkloadKind
    workload_profile_hash: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("route_id", "pack_version", "worker_version", "driver_version")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not _IDENTIFIER.fullmatch(value):
            raise ValueError("calibration identity must be sanitized")
        return value

    def key_ref(self) -> str:
        canonical = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return f"calibration::{sha256(canonical.encode('utf-8')).hexdigest()}"

    def matches_scope(self, *, workload: WorkloadKind, model_hash: str, workload_profile_hash: str) -> bool:
        return (
            self.workload is workload
            and self.model_hash == model_hash
            and self.workload_profile_hash == workload_profile_hash
        )


class CalibrationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: CalibrationKey
    outcome: Literal["passed", "failed", "oom"]
    correctness_passed: StrictBool
    health_passed: StrictBool
    score: StrictFloat | None = None
    latency_ms: StrictFloat | None = Field(default=None, gt=0)
    throughput_units_per_s: StrictFloat | None = Field(default=None, gt=0)
    peak_memory_bytes: StrictInt | None = Field(default=None, ge=0)
    measured_at: datetime
    valid_until: datetime
    evidence_refs: tuple[StrictStr, ...] = Field(min_length=1, max_length=64)

    @field_validator("score", "latency_ms", "throughput_units_per_s")
    @classmethod
    def validate_finite_number(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("calibration metric must be finite")
        return value

    @field_validator("measured_at", "valid_until")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return _validate_aware(value, label="calibration timestamp")

    @field_validator("evidence_refs")
    @classmethod
    def validate_evidence_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not _IDENTIFIER.fullmatch(item) for item in value):
            raise ValueError("calibration evidence references must be sanitized")
        return value

    @model_validator(mode="after")
    def validate_outcome(self) -> "CalibrationRecord":
        if self.valid_until <= self.measured_at:
            raise ValueError("calibration validity window is invalid")
        if self.outcome == "passed":
            if not self.correctness_passed or not self.health_passed or self.score is None:
                raise ValueError("passed calibration requires health, correctness, and score")
        elif self.correctness_passed or self.health_passed or self.score is not None:
            raise ValueError("failed calibration cannot claim verified metrics")
        return self

    def is_stale(self, at: datetime | None = None) -> bool:
        instant = at or _utcnow()
        _validate_aware(instant, label="calibration comparison timestamp")
        return instant >= self.valid_until


class CalibrationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    records: dict[StrictStr, CalibrationRecord] = Field(default_factory=dict, max_length=_MAX_RECORDS)

    @model_validator(mode="after")
    def validate_record_keys(self) -> "CalibrationSnapshot":
        if any(reference != record.key.key_ref() for reference, record in self.records.items()):
            raise ValueError("calibration record reference does not match its exact key")
        return self


class CalibrationLedger:
    """Bounded atomic store for exact-key calibration evidence."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = _path_lock(self.path)
        with self._lock:
            self._cleanup_partials()
            self._snapshot = self._load()

    def _cleanup_partials(self) -> None:
        if not self.path.parent.exists():
            return
        for candidate in self.path.parent.glob(f".{self.path.name}.*.partial"):
            candidate.unlink(missing_ok=True)

    def _load(self) -> CalibrationSnapshot:
        if not self.path.exists():
            return CalibrationSnapshot()
        payload = self.path.read_bytes()
        if len(payload) > _MAX_LEDGER_BYTES:
            raise ValueError("calibration-ledger-size-limit")
        try:
            return CalibrationSnapshot.model_validate_json(payload)
        except (UnicodeError, ValueError, TypeError):
            raise ValueError("calibration-ledger-invalid") from None

    def _persist(self, snapshot: CalibrationSnapshot) -> None:
        payload = snapshot.model_dump_json(indent=2).encode("utf-8")
        if len(payload) > _MAX_LEDGER_BYTES:
            raise ValueError("calibration-ledger-size-limit")
        temporary: Path | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{self.path.name}.",
                suffix=".partial",
                dir=self.path.parent,
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            self._snapshot = snapshot
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def _refresh(self) -> None:
        self._snapshot = self._load()

    def put(self, record: CalibrationRecord) -> CalibrationRecord:
        with self._lock:
            self._refresh()
            records = dict(self._snapshot.records)
            records[record.key.key_ref()] = record
            if len(records) > _MAX_RECORDS:
                raise ValueError("calibration-ledger-record-limit")
            self._persist(CalibrationSnapshot(records=records))
            return record

    def get(self, key: CalibrationKey, *, at: datetime | None = None) -> CalibrationRecord | None:
        with self._lock:
            self._refresh()
            record = self._snapshot.records.get(key.key_ref())
            if record is None or record.key != key or record.is_stale(at):
                return None
            return record

    def verified(self, key: CalibrationKey, *, at: datetime | None = None) -> CalibrationRecord | None:
        record = self.get(key, at=at)
        if (
            record is None
            or record.outcome != "passed"
            or not record.correctness_passed
            or not record.health_passed
            or record.score is None
        ):
            return None
        return record

    def invalidate(
        self,
        *,
        pack_id: str | None = None,
        device_fingerprint: str | None = None,
        driver_version: str | None = None,
    ) -> int:
        if pack_id is None and device_fingerprint is None and driver_version is None:
            raise ValueError("calibration-invalidation-scope-required")
        if pack_id is not None and not _PACK_ID.fullmatch(pack_id):
            raise ValueError("calibration-invalidation-scope-invalid")
        if device_fingerprint is not None and not _DEVICE_FINGERPRINT.fullmatch(device_fingerprint):
            raise ValueError("calibration-invalidation-scope-invalid")
        if driver_version is not None and not _IDENTIFIER.fullmatch(driver_version):
            raise ValueError("calibration-invalidation-scope-invalid")
        with self._lock:
            self._refresh()
            retained = {
                reference: record
                for reference, record in self._snapshot.records.items()
                if not (
                    (pack_id is None or record.key.pack_id == pack_id)
                    and (device_fingerprint is None or record.key.device_fingerprint == device_fingerprint)
                    and (driver_version is None or record.key.driver_version == driver_version)
                )
            }
            removed = len(self._snapshot.records) - len(retained)
            if removed:
                self._persist(CalibrationSnapshot(records=retained))
            return removed

    def summary(self, *, at: datetime | None = None) -> dict[str, int]:
        instant = at or _utcnow()
        _validate_aware(instant, label="calibration comparison timestamp")
        with self._lock:
            self._refresh()
            records = tuple(self._snapshot.records.values())
            return {
                "record_count": len(records),
                "verified_count": sum(
                    1
                    for record in records
                    if not record.is_stale(instant)
                    and record.outcome == "passed"
                    and record.correctness_passed
                    and record.health_passed
                ),
                "stale_count": sum(1 for record in records if record.is_stale(instant)),
                "oom_count": sum(1 for record in records if record.outcome == "oom"),
            }
