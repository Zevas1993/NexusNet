from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import tempfile
from threading import RLock
from types import MappingProxyType
from typing import Annotated, Literal, Mapping

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)

from .contracts import PackLifecycleState, RuntimePackManifest


_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
_REASON_CODE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_MAX_REGISTRY_BYTES = 16 * 1024 * 1024
_MAX_RECORDS = 4096
_MAX_PACK_POINTERS = 1024
_MAX_REASON_CODES = 64
_PATH_LOCKS_GUARD = RLock()
_PATH_LOCKS: dict[str, RLock] = {}


def _shared_path_lock(path: Path) -> RLock:
    key = os.path.normcase(str(path.resolve(strict=False)))
    with _PATH_LOCKS_GUARD:
        lock = _PATH_LOCKS.get(key)
        if lock is None:
            lock = RLock()
            _PATH_LOCKS[key] = lock
        return lock


@contextmanager
def _exclusive_file_lock(path: Path):
    handle = None
    locked = False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("a+b")
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        locked = True
    except OSError:
        if handle is not None:
            handle.close()
        raise RegistryError("registry-lock-failed") from None
    try:
        yield
    finally:
        if handle is not None:
            if locked:
                try:
                    handle.seek(0)
                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
            try:
                handle.close()
            except OSError:
                pass


class RegistryError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class RuntimePackRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest: RuntimePackManifest
    state: PackLifecycleState = PackLifecycleState.AVAILABLE
    install_ref: StrictStr | None = Field(default=None, max_length=512)
    reason_codes: tuple[StrictStr, ...] = Field(
        default=(),
        max_length=_MAX_REASON_CODES,
        validate_default=True,
    )
    updated_at: datetime

    @field_validator("install_ref")
    @classmethod
    def validate_install_ref(cls, value: str | None) -> str | None:
        if value is None:
            return None
        posix_ref = PurePosixPath(value)
        windows_ref = PureWindowsPath(value)
        if (
            not value
            or value != value.strip()
            or _CONTROL_CHARACTERS.search(value)
            or "\\" in value
            or posix_ref.is_absolute()
            or windows_ref.is_absolute()
            or bool(windows_ref.drive)
            or any(part in {"", ".", ".."} for part in value.split("/"))
            or posix_ref.as_posix() != value
        ):
            raise ValueError("install_ref must be a normalized package-relative reference")
        return value

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("updated_at must be timezone-aware")
        return value

    @field_validator("reason_codes")
    @classmethod
    def validate_reason_codes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not _REASON_CODE.fullmatch(reason_code) for reason_code in value):
            raise ValueError("reason_codes must contain stable sanitized codes")
        return value

    @model_validator(mode="after")
    def validate_lifecycle_fields(self) -> "RuntimePackRecord":
        if self.state in {
            PackLifecycleState.STAGED,
            PackLifecycleState.VERIFYING,
            PackLifecycleState.ACTIVE,
            PackLifecycleState.DEGRADED,
            PackLifecycleState.ROLLBACK_AVAILABLE,
        } and self.install_ref is None:
            raise ValueError("installed lifecycle states require install_ref")
        if self.state in {
            PackLifecycleState.AVAILABLE,
            PackLifecycleState.DOWNLOADING,
            PackLifecycleState.REMOVED,
        } and self.install_ref is not None:
            raise ValueError("pre-install and removed lifecycle states cannot retain install_ref")
        return self


def _freeze_records(value: Mapping[str, RuntimePackRecord]) -> Mapping[str, RuntimePackRecord]:
    return MappingProxyType(dict(value))


def _freeze_strings(value: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(value))


FrozenRecordMapping = Annotated[
    Mapping[StrictStr, RuntimePackRecord],
    AfterValidator(_freeze_records),
    PlainSerializer(lambda value: dict(value), return_type=dict),
]
FrozenStringMapping = Annotated[
    Mapping[StrictStr, StrictStr],
    AfterValidator(_freeze_strings),
    PlainSerializer(lambda value: dict(value), return_type=dict),
]


class RegistrySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    records: FrozenRecordMapping = Field(default_factory=dict, max_length=_MAX_RECORDS, validate_default=True)
    active_versions: FrozenStringMapping = Field(
        default_factory=dict,
        max_length=_MAX_PACK_POINTERS,
        validate_default=True,
    )
    previous_versions: FrozenStringMapping = Field(
        default_factory=dict,
        max_length=_MAX_PACK_POINTERS,
        validate_default=True,
    )
    failed_versions: FrozenStringMapping = Field(
        default_factory=dict,
        max_length=_MAX_PACK_POINTERS,
        validate_default=True,
    )

    @model_validator(mode="after")
    def validate_references(self) -> "RegistrySnapshot":
        for key, record in self.records.items():
            expected = f"{record.manifest.pack_id}@{record.manifest.version}"
            if key != expected:
                raise ValueError("record key does not match manifest identity")

        for pack_id, version in self.active_versions.items():
            record = self.records.get(f"{pack_id}@{version}")
            if record is None or record.manifest.pack_id != pack_id or record.state not in {
                PackLifecycleState.ACTIVE,
                PackLifecycleState.DEGRADED,
            }:
                raise ValueError("active version reference is invalid")

        for pack_id, version in self.previous_versions.items():
            record = self.records.get(f"{pack_id}@{version}")
            if record is None or record.manifest.pack_id != pack_id or record.state != PackLifecycleState.ROLLBACK_AVAILABLE:
                raise ValueError("previous version reference is invalid")
            if self.active_versions.get(pack_id) == version:
                raise ValueError("active and previous versions must differ")

        for pack_id, version in self.failed_versions.items():
            record = self.records.get(f"{pack_id}@{version}")
            if record is None or record.manifest.pack_id != pack_id or record.state != PackLifecycleState.QUARANTINED:
                raise ValueError("failed version reference is invalid")
            if self.active_versions.get(pack_id) is not None:
                raise ValueError("active and failed versions cannot coexist")

        for pack_id, previous_version in self.previous_versions.items():
            current_version = self.active_versions.get(pack_id) or self.failed_versions.get(pack_id)
            if current_version is None:
                raise ValueError("previous version lacks an active or failed successor")
            current = self.records.get(f"{pack_id}@{current_version}")
            if current is None or previous_version not in current.manifest.rollback_compatible_from:
                raise ValueError("previous version is not declared rollback compatible")

        for record in self.records.values():
            pack_id = record.manifest.pack_id
            version = record.manifest.version
            if record.state in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
                if self.active_versions.get(pack_id) != version:
                    raise ValueError("active record lacks its active version reference")
            if record.state == PackLifecycleState.ROLLBACK_AVAILABLE:
                if self.previous_versions.get(pack_id) != version:
                    raise ValueError("rollback record lacks its previous version reference")
        return self


_ALLOWED_TRANSITIONS = {
    PackLifecycleState.AVAILABLE: {PackLifecycleState.DOWNLOADING, PackLifecycleState.REMOVED},
    PackLifecycleState.DOWNLOADING: {PackLifecycleState.STAGED, PackLifecycleState.QUARANTINED},
    PackLifecycleState.STAGED: {PackLifecycleState.VERIFYING, PackLifecycleState.QUARANTINED},
    PackLifecycleState.VERIFYING: {PackLifecycleState.QUARANTINED},
    PackLifecycleState.ACTIVE: {PackLifecycleState.DEGRADED, PackLifecycleState.QUARANTINED},
    PackLifecycleState.DEGRADED: {PackLifecycleState.ACTIVE, PackLifecycleState.QUARANTINED},
    PackLifecycleState.QUARANTINED: {PackLifecycleState.STAGED, PackLifecycleState.REMOVED},
    PackLifecycleState.ROLLBACK_AVAILABLE: {PackLifecycleState.REMOVED},
    PackLifecycleState.REMOVED: {PackLifecycleState.AVAILABLE},
}


class RuntimePackRegistry:
    def __init__(self, registry_path: str | Path):
        self._path = Path(registry_path)
        self._lock_path = self._path.with_name(f"{self._path.name}.lock")
        self._lock = RLock()
        self._path_lock = _shared_path_lock(self._path)
        with self._path_lock, _exclusive_file_lock(self._lock_path):
            self._cleanup_stale_temps()
            self._snapshot = self._load()

    @staticmethod
    def _key(pack_id: str, version: str) -> str:
        return f"{pack_id}@{version}"

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _validate_reason_code(reason_code: str) -> str:
        if not isinstance(reason_code, str) or not _REASON_CODE.fullmatch(reason_code):
            raise RegistryError("reason-code-invalid")
        return reason_code

    @staticmethod
    def _updated_record(record: RuntimePackRecord, **updates) -> RuntimePackRecord:
        payload = record.model_dump(mode="json")
        payload.update(updates)
        try:
            return RuntimePackRecord.model_validate(payload)
        except (ValidationError, ValueError, TypeError):
            raise RegistryError("registry-record-invalid") from None

    @staticmethod
    def _append_reason(reason_codes: tuple[str, ...], reason_code: str) -> tuple[str, ...]:
        return (*reason_codes, reason_code)[-_MAX_REASON_CODES:]

    def _new_snapshot(self, **updates) -> RegistrySnapshot:
        payload = self._snapshot.model_dump(mode="json")
        payload.update(updates)
        try:
            return RegistrySnapshot.model_validate(payload)
        except (ValidationError, ValueError, TypeError):
            raise RegistryError("registry-state-invalid") from None

    def _load(self) -> RegistrySnapshot:
        if not self._path.exists():
            return RegistrySnapshot()
        try:
            with self._path.open("rb") as handle:
                payload = handle.read(_MAX_REGISTRY_BYTES + 1)
            if len(payload) > _MAX_REGISTRY_BYTES:
                raise ValueError("registry exceeds size limit")
            return RegistrySnapshot.model_validate_json(payload)
        except (OSError, UnicodeError, ValidationError, ValueError, TypeError):
            raise RegistryError("registry-invalid") from None

    def _cleanup_stale_temps(self) -> None:
        if not self._path.parent.exists():
            return
        try:
            for candidate in self._path.parent.glob(f"{self._path.name}.*.tmp"):
                candidate.unlink(missing_ok=True)
        except OSError:
            raise RegistryError("registry-temp-cleanup-failed") from None

    @contextmanager
    def _mutation(self):
        with self._lock, self._path_lock, _exclusive_file_lock(self._lock_path):
            self._cleanup_stale_temps()
            self._snapshot = self._load()
            yield

    @contextmanager
    def _refreshed_read(self):
        with self._lock, self._path_lock, _exclusive_file_lock(self._lock_path):
            self._snapshot = self._load()
            yield

    def _persist(self, snapshot: RegistrySnapshot) -> None:
        try:
            serialized = snapshot.model_dump_json(indent=2).encode("utf-8")
        except (UnicodeError, ValueError, TypeError):
            raise RegistryError("registry-persist-failed") from None
        if len(serialized) > _MAX_REGISTRY_BYTES:
            raise RegistryError("registry-size-limit")

        temporary_path: Path | None = None
        replaced = False
        persist_failed = False
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._path.parent,
                prefix=f"{self._path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self._path)
            replaced = True
        except (OSError, UnicodeError, ValueError, TypeError):
            persist_failed = True
        finally:
            if temporary_path is not None and not replaced:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
        if persist_failed:
            raise RegistryError("registry-persist-failed") from None
        self._snapshot = snapshot

    def snapshot(self) -> RegistrySnapshot:
        with self._refreshed_read():
            return RegistrySnapshot.model_validate(self._snapshot.model_dump(mode="json"))

    def _cached_get(self, pack_id: str, version: str) -> RuntimePackRecord:
        try:
            return self._snapshot.records[self._key(pack_id, version)]
        except KeyError:
            raise RegistryError("pack-version-not-registered") from None

    def _cached_active(self, pack_id: str) -> RuntimePackRecord:
        version = self._snapshot.active_versions.get(pack_id)
        if version is None:
            raise RegistryError("active-pack-unavailable")
        record = self._cached_get(pack_id, version)
        if record.state not in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
            raise RegistryError("active-pack-unavailable")
        return record

    def register_manifest(self, manifest: RuntimePackManifest) -> RuntimePackRecord:
        with self._mutation():
            key = self._key(manifest.pack_id, manifest.version)
            existing = self._snapshot.records.get(key)
            if existing is not None:
                if existing.manifest != manifest:
                    raise RegistryError("manifest-version-conflict")
                return existing
            record = RuntimePackRecord(manifest=manifest, updated_at=self._now())
            records = {**self._snapshot.records, key: record}
            self._persist(self._new_snapshot(records=records))
            return record

    def get(self, pack_id: str, version: str) -> RuntimePackRecord:
        with self._refreshed_read():
            return self._cached_get(pack_id, version)

    def active(self, pack_id: str) -> RuntimePackRecord:
        with self._refreshed_read():
            return self._cached_active(pack_id)

    def transition(
        self,
        pack_id: str,
        version: str,
        target: PackLifecycleState,
        *,
        install_ref: str | None = None,
        reason_code: str | None = None,
    ) -> RuntimePackRecord:
        with self._mutation():
            current = self._cached_get(pack_id, version)
            try:
                target = PackLifecycleState(target)
            except (TypeError, ValueError):
                raise RegistryError("lifecycle-transition-invalid") from None
            if target not in _ALLOWED_TRANSITIONS[current.state]:
                raise RegistryError("lifecycle-transition-invalid")
            if install_ref is not None and target != PackLifecycleState.STAGED:
                raise RegistryError("install-ref-not-allowed")
            if target == PackLifecycleState.STAGED and install_ref is None and current.install_ref is None:
                raise RegistryError("registry-record-invalid")
            if reason_code is not None:
                self._validate_reason_code(reason_code)
            updated = self._updated_record(
                current,
                state=target,
                install_ref=(
                    None
                    if target == PackLifecycleState.REMOVED
                    else install_ref if install_ref is not None else current.install_ref
                ),
                reason_codes=self._append_reason(current.reason_codes, reason_code) if reason_code else current.reason_codes,
                updated_at=self._now(),
            )
            records = {**self._snapshot.records, self._key(pack_id, version): updated}
            active_versions = dict(self._snapshot.active_versions)
            previous_versions = dict(self._snapshot.previous_versions)
            failed_versions = dict(self._snapshot.failed_versions)
            is_pending_failure = failed_versions.get(pack_id) == version
            if is_pending_failure and previous_versions.get(pack_id) is not None:
                raise RegistryError("quarantine-resolution-required")
            if current.state in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
                if target == PackLifecycleState.QUARANTINED and active_versions.get(pack_id) == version:
                    active_versions.pop(pack_id, None)
                    failed_versions[pack_id] = version
            if target == PackLifecycleState.REMOVED:
                if active_versions.get(pack_id) == version:
                    active_versions.pop(pack_id, None)
                if previous_versions.get(pack_id) == version:
                    previous_versions.pop(pack_id, None)
                if failed_versions.get(pack_id) == version:
                    failed_versions.pop(pack_id, None)
            if target == PackLifecycleState.STAGED and failed_versions.get(pack_id) == version:
                failed_versions.pop(pack_id, None)
            snapshot = self._new_snapshot(
                records=records,
                active_versions=active_versions,
                previous_versions=previous_versions,
                failed_versions=failed_versions,
            )
            self._persist(snapshot)
            return updated

    def activate(self, pack_id: str, version: str) -> RuntimePackRecord:
        with self._mutation():
            candidate = self._cached_get(pack_id, version)
            if candidate.state != PackLifecycleState.VERIFYING:
                raise RegistryError("lifecycle-transition-invalid")
            records = dict(self._snapshot.records)
            active_versions = dict(self._snapshot.active_versions)
            previous_versions = dict(self._snapshot.previous_versions)
            failed_versions = dict(self._snapshot.failed_versions)
            previous = active_versions.get(pack_id)
            if failed_versions.get(pack_id) is not None and previous_versions.get(pack_id) is not None:
                raise RegistryError("quarantine-resolution-required")
            if previous and previous != version:
                if previous not in candidate.manifest.rollback_compatible_from:
                    raise RegistryError("rollback-incompatible")
                older_previous = previous_versions.get(pack_id)
                if older_previous is not None and older_previous != previous:
                    older_key = self._key(pack_id, older_previous)
                    older_record = records.get(older_key)
                    if older_record is None or older_record.state != PackLifecycleState.ROLLBACK_AVAILABLE:
                        raise RegistryError("registry-state-invalid")
                    records[older_key] = self._updated_record(
                        older_record,
                        state=PackLifecycleState.STAGED,
                        updated_at=self._now(),
                    )
                old_key = self._key(pack_id, previous)
                old_record = records.get(old_key)
                if old_record is None or old_record.state not in {
                    PackLifecycleState.ACTIVE,
                    PackLifecycleState.DEGRADED,
                }:
                    raise RegistryError("registry-state-invalid")
                records[old_key] = self._updated_record(
                    old_record,
                    state=PackLifecycleState.ROLLBACK_AVAILABLE,
                    updated_at=self._now(),
                )
                previous_versions[pack_id] = previous
            activated = self._updated_record(
                candidate,
                state=PackLifecycleState.ACTIVE,
                updated_at=self._now(),
            )
            records[self._key(pack_id, version)] = activated
            active_versions[pack_id] = version
            failed_versions.pop(pack_id, None)
            self._persist(
                self._new_snapshot(
                    records=records,
                    active_versions=active_versions,
                    previous_versions=previous_versions,
                    failed_versions=failed_versions,
                )
            )
            return activated

    def rollback(self, pack_id: str, *, reason_code: str) -> RuntimePackRecord:
        with self._mutation():
            self._validate_reason_code(reason_code)
            current_version = self._snapshot.active_versions.get(pack_id)
            failed_version = self._snapshot.failed_versions.get(pack_id)
            target_version = self._snapshot.previous_versions.get(pack_id)
            if target_version is None:
                raise RegistryError("rollback-unavailable")
            target = self._cached_get(pack_id, target_version)
            if target.state != PackLifecycleState.ROLLBACK_AVAILABLE:
                raise RegistryError("rollback-unavailable")
            records = dict(self._snapshot.records)
            if current_version is not None:
                current = self._cached_get(pack_id, current_version)
                if current.state not in {PackLifecycleState.ACTIVE, PackLifecycleState.DEGRADED}:
                    raise RegistryError("rollback-unavailable")
                records[self._key(pack_id, current_version)] = self._updated_record(
                    current,
                    state=PackLifecycleState.QUARANTINED,
                    reason_codes=self._append_reason(current.reason_codes, reason_code),
                    updated_at=self._now(),
                )
            elif failed_version is not None:
                failed = self._cached_get(pack_id, failed_version)
                if failed.state != PackLifecycleState.QUARANTINED:
                    raise RegistryError("rollback-unavailable")
                records[self._key(pack_id, failed_version)] = self._updated_record(
                    failed,
                    reason_codes=self._append_reason(failed.reason_codes, reason_code),
                    updated_at=self._now(),
                )
            else:
                raise RegistryError("rollback-unavailable")
            restored = self._updated_record(
                target,
                state=PackLifecycleState.ACTIVE,
                updated_at=self._now(),
            )
            records[self._key(pack_id, target_version)] = restored
            active_versions = {**self._snapshot.active_versions, pack_id: target_version}
            previous_versions = dict(self._snapshot.previous_versions)
            previous_versions.pop(pack_id, None)
            failed_versions = dict(self._snapshot.failed_versions)
            failed_versions.pop(pack_id, None)
            self._persist(
                self._new_snapshot(
                    records=records,
                    active_versions=active_versions,
                    previous_versions=previous_versions,
                    failed_versions=failed_versions,
                )
            )
            return restored
