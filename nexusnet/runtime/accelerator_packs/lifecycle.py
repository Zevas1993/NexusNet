from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile
from threading import RLock
from typing import Callable, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator, model_validator

from .calibration import CalibrationKey
from .contracts import PackLifecycleState, RuntimePackManifest
from .installer import PackInstaller
from .registry import RegistryError, RuntimePackRegistry


_REASON = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SAFE_TEXT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._:+-]{0,255}$")
_MAX_FILE_BYTES = 16 * 1024 * 1024
_LOCK_GUARD = RLock()
_LOCKS: dict[str, RLock] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _lock_for(path: Path) -> RLock:
    key = os.path.normcase(str(path.resolve(strict=False)))
    with _LOCK_GUARD:
        return _LOCKS.setdefault(key, RLock())


def _atomic_write(path: Path, payload: bytes) -> None:
    if len(payload) > _MAX_FILE_BYTES:
        raise ValueError("lifecycle-store-size-limit")
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".partial",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


class CircuitState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: CalibrationKey
    failure_count: StrictInt = Field(ge=0)
    opened: StrictBool = False
    last_reason_code: StrictStr | None = None
    updated_at: datetime

    @field_validator("last_reason_code")
    @classmethod
    def validate_reason(cls, value: str | None) -> str | None:
        if value is not None and not _REASON.fullmatch(value):
            raise ValueError("circuit reason must be sanitized")
        return value

    @field_validator("updated_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("circuit timestamp must be timezone-aware")
        return value


class CircuitSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    circuits: dict[StrictStr, CircuitState] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_references(self) -> "CircuitSnapshot":
        if any(reference != state.key.key_ref() for reference, state in self.circuits.items()):
            raise ValueError("circuit reference does not match exact key")
        return self


class PackCircuitBreaker:
    def __init__(
        self,
        path: str | Path,
        *,
        failure_threshold: int = 3,
        max_records: int = 1024,
    ) -> None:
        if type(failure_threshold) is not int or not 1 <= failure_threshold <= 100:
            raise ValueError("circuit-failure-threshold-invalid")
        if type(max_records) is not int or not 1 <= max_records <= 4096:
            raise ValueError("circuit-record-limit-invalid")
        self.path = Path(path)
        self.failure_threshold = failure_threshold
        self.max_records = max_records
        self._lock = _lock_for(self.path)
        with self._lock:
            self._cleanup()
            self._snapshot = self._load()

    def _cleanup(self) -> None:
        if self.path.parent.exists():
            for candidate in self.path.parent.glob(f".{self.path.name}.*.partial"):
                candidate.unlink(missing_ok=True)

    def _load(self) -> CircuitSnapshot:
        if not self.path.exists():
            return CircuitSnapshot()
        payload = self.path.read_bytes()
        if len(payload) > _MAX_FILE_BYTES:
            raise ValueError("circuit-store-size-limit")
        try:
            return CircuitSnapshot.model_validate_json(payload)
        except (ValueError, TypeError, UnicodeError):
            raise ValueError("circuit-store-invalid") from None

    def _persist(self, circuits: dict[str, CircuitState]) -> None:
        snapshot = CircuitSnapshot(circuits=circuits)
        _atomic_write(self.path, snapshot.model_dump_json(indent=2).encode("utf-8"))
        self._snapshot = snapshot

    def _refresh(self) -> None:
        self._snapshot = self._load()

    def state(self, key: CalibrationKey) -> CircuitState:
        with self._lock:
            self._refresh()
            return self._snapshot.circuits.get(
                key.key_ref(),
                CircuitState(key=key, failure_count=0, opened=False, updated_at=_utcnow()),
            )

    def record_failure(self, key: CalibrationKey, *, reason_code: str) -> CircuitState:
        if not _REASON.fullmatch(reason_code):
            raise ValueError("circuit-reason-invalid")
        with self._lock:
            self._refresh()
            circuits = dict(self._snapshot.circuits)
            prior = circuits.get(key.key_ref())
            count = (prior.failure_count if prior is not None else 0) + 1
            state = CircuitState(
                key=key,
                failure_count=count,
                opened=count >= self.failure_threshold,
                last_reason_code=reason_code,
                updated_at=_utcnow(),
            )
            circuits[key.key_ref()] = state
            if len(circuits) > self.max_records:
                removable = sorted(
                    (item for item in circuits.values() if not item.opened and item.key.key_ref() != key.key_ref()),
                    key=lambda item: item.updated_at,
                )
                while len(circuits) > self.max_records and removable:
                    circuits.pop(removable.pop(0).key.key_ref(), None)
            if len(circuits) > self.max_records:
                raise ValueError("circuit-record-limit")
            self._persist(circuits)
            return state

    def record_success(self, key: CalibrationKey) -> None:
        self.reset(key)

    def reset(self, key: CalibrationKey) -> None:
        with self._lock:
            self._refresh()
            circuits = dict(self._snapshot.circuits)
            if circuits.pop(key.key_ref(), None) is not None:
                self._persist(circuits)

    def summary(self) -> dict[str, object]:
        with self._lock:
            self._refresh()
            states = tuple(sorted(self._snapshot.circuits.values(), key=lambda item: item.key.key_ref()))
            return {
                "circuit_count": len(states),
                "open_count": sum(1 for state in states if state.opened),
                "circuits": [
                    {
                        "key_ref": state.key.key_ref(),
                        "failure_count": state.failure_count,
                        "opened": state.opened,
                        "reason_code": state.last_reason_code,
                    }
                    for state in states
                ],
            }


class ProvenanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    publisher: StrictStr
    license_id: StrictStr
    artifact_count: StrictInt = Field(ge=0)
    origin_count: StrictInt = Field(ge=0)
    signature_count: StrictInt = Field(ge=0)
    manifest_digest_sha256: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("publisher", "license_id")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not _SAFE_TEXT.fullmatch(value):
            raise ValueError("provenance text must be sanitized")
        return value


class SbomSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_count: StrictInt = Field(ge=1)
    digest_sha256: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")
    license_ids: tuple[StrictStr, ...] = Field(min_length=1, max_length=64)

    @field_validator("license_ids")
    @classmethod
    def validate_licenses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not _SAFE_TEXT.fullmatch(item) for item in value):
            raise ValueError("SBOM licenses must be sanitized")
        return value


class LifecycleReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["observe", "quarantine", "rollback", "repair", "update", "uninstall"]
    outcome: Literal["passed", "degraded", "failed"]
    pack_id: StrictStr = Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")
    pack_version: StrictStr = Field(min_length=1, max_length=128)
    reason_codes: tuple[StrictStr, ...] = Field(min_length=1, max_length=32)
    provenance: ProvenanceSummary
    sbom: SbomSummary
    created_at: datetime

    @field_validator("reason_codes")
    @classmethod
    def validate_reasons(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not _REASON.fullmatch(item) for item in value):
            raise ValueError("lifecycle reasons must be sanitized")
        return value

    @field_validator("created_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("lifecycle receipt timestamp must be timezone-aware")
        return value


class ReceiptSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    receipts: tuple[LifecycleReceipt, ...] = ()


QuarantineSink = Callable[[str, str], object]


class PackLifecycleManager:
    def __init__(
        self,
        *,
        registry: RuntimePackRegistry,
        installer: PackInstaller,
        circuit_breaker: PackCircuitBreaker,
        receipt_path: str | Path,
        quarantine_sink: QuarantineSink | None = None,
        max_receipts: int = 256,
    ) -> None:
        if type(max_receipts) is not int or not 1 <= max_receipts <= 4096:
            raise ValueError("lifecycle-receipt-limit-invalid")
        self.registry = registry
        self.installer = installer
        self.circuit_breaker = circuit_breaker
        self.receipt_path = Path(receipt_path)
        self.quarantine_sink = quarantine_sink
        self.max_receipts = max_receipts
        self._receipt_lock = _lock_for(self.receipt_path)

    @staticmethod
    def _provenance(manifest: RuntimePackManifest) -> ProvenanceSummary:
        payload = manifest.model_dump(mode="json")
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        origins = {urlsplit(artifact.url).hostname for artifact in manifest.artifacts}
        return ProvenanceSummary(
            publisher=manifest.publisher,
            license_id=manifest.license_id,
            artifact_count=len(manifest.artifacts),
            origin_count=len(origins),
            signature_count=sum(1 for artifact in manifest.artifacts if artifact.signature is not None),
            manifest_digest_sha256=digest,
        )

    @staticmethod
    def _sbom(manifest: RuntimePackManifest) -> SbomSummary:
        components = [
            f"pack:{manifest.pack_id}@{manifest.version}",
            *sorted(f"constraint:{name}" for name in manifest.dependency_constraints),
        ]
        digest = sha256("\n".join(components).encode("utf-8")).hexdigest()
        return SbomSummary(
            component_count=len(components),
            digest_sha256=digest,
            license_ids=(manifest.license_id,),
        )

    def _receipt(
        self,
        manifest: RuntimePackManifest,
        *,
        action: str,
        outcome: str,
        reason_codes: tuple[str, ...],
    ) -> LifecycleReceipt:
        receipt = LifecycleReceipt(
            action=action,
            outcome=outcome,
            pack_id=manifest.pack_id,
            pack_version=manifest.version,
            reason_codes=reason_codes,
            provenance=self._provenance(manifest),
            sbom=self._sbom(manifest),
            created_at=_utcnow(),
        )
        self._append_receipt(receipt)
        return receipt

    def _append_receipt(self, receipt: LifecycleReceipt) -> None:
        with self._receipt_lock:
            existing = self._load_receipts()
            retained = (*existing, receipt)[-self.max_receipts :]
            snapshot = ReceiptSnapshot(receipts=retained)
            _atomic_write(self.receipt_path, snapshot.model_dump_json(indent=2).encode("utf-8"))

    def _load_receipts(self) -> tuple[LifecycleReceipt, ...]:
        if not self.receipt_path.exists():
            return ()
        payload = self.receipt_path.read_bytes()
        if len(payload) > _MAX_FILE_BYTES:
            raise ValueError("lifecycle-receipt-store-size-limit")
        try:
            return ReceiptSnapshot.model_validate_json(payload).receipts
        except (ValueError, TypeError, UnicodeError):
            raise ValueError("lifecycle-receipt-store-invalid") from None

    def receipts(self) -> tuple[LifecycleReceipt, ...]:
        with self._receipt_lock:
            return self._load_receipts()

    def record_worker_failure(self, key: CalibrationKey, *, reason_code: str) -> LifecycleReceipt:
        state = self.circuit_breaker.record_failure(key, reason_code=reason_code)
        record = self.registry.get(key.pack_id, key.pack_version)
        if not state.opened:
            return self._receipt(
                record.manifest,
                action="observe",
                outcome="degraded",
                reason_codes=(reason_code,),
            )

        if record.state in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
            self.registry.transition(
                key.pack_id,
                key.pack_version,
                PackLifecycleState.QUARANTINED,
                reason_code="circuit-open",
            )
        if self.quarantine_sink is not None:
            self.quarantine_sink(key.pack_id, key.pack_version)
        try:
            self.registry.rollback(key.pack_id, reason_code="circuit-open-rollback")
            return self._receipt(
                record.manifest,
                action="rollback",
                outcome="passed",
                reason_codes=("circuit-open", "circuit-open-rollback"),
            )
        except RegistryError:
            return self._receipt(
                record.manifest,
                action="quarantine",
                outcome="degraded",
                reason_codes=("circuit-open", "rollback-unavailable"),
            )

    def repair(self, key: CalibrationKey) -> LifecycleReceipt:
        record = self.installer.repair(key.pack_id, key.pack_version)
        self.circuit_breaker.reset(key)
        return self._receipt(
            record.manifest,
            action="repair",
            outcome="passed",
            reason_codes=("pack-repaired",),
        )

    def update(self, manifest: RuntimePackManifest, *, consent: bool) -> LifecycleReceipt:
        record = self.installer.update(manifest, consent=consent)
        return self._receipt(
            record.manifest,
            action="update",
            outcome="passed",
            reason_codes=("pack-updated",),
        )

    def uninstall(self, pack_id: str, version: str) -> LifecycleReceipt:
        snapshot = self.registry.snapshot()
        if snapshot.active_versions.get(pack_id) == version and snapshot.previous_versions.get(pack_id) is not None:
            self.installer.rollback(pack_id, reason_code="pack-uninstall-rollback")
        record = self.installer.uninstall(pack_id, version)
        return self._receipt(
            record.manifest,
            action="uninstall",
            outcome="passed",
            reason_codes=("pack-uninstalled",),
        )

    def certification_summary(self, manifest: RuntimePackManifest) -> dict[str, object]:
        return {
            "pack_id": manifest.pack_id,
            "pack_version": manifest.version,
            "provenance": self._provenance(manifest).model_dump(mode="json"),
            "sbom": self._sbom(manifest).model_dump(mode="json"),
        }
