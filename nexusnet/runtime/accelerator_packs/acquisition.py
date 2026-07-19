from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import shutil
from typing import BinaryIO, Callable
from urllib.parse import urlsplit
from urllib.request import urlopen
from uuid import uuid4

from .contracts import ArtifactDescriptor


_ARTIFACT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class AcquisitionError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class AcquisitionPolicy:
    allowed_hosts: frozenset[str]
    max_artifact_bytes: int = 8 * 1024 * 1024 * 1024
    disk_reserve_bytes: int = 2 * 1024 * 1024 * 1024
    chunk_bytes: int = 1024 * 1024
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        normalized = frozenset(host.casefold() for host in self.allowed_hosts if host and host == host.strip())
        if normalized != self.allowed_hosts or not normalized:
            raise ValueError("allowed_hosts must contain normalized host names")
        if self.max_artifact_bytes <= 0 or self.disk_reserve_bytes < 0 or self.chunk_bytes <= 0:
            raise ValueError("acquisition byte limits are invalid")
        if not 0 < self.timeout_seconds <= 300:
            raise ValueError("acquisition timeout is invalid")


@dataclass(frozen=True)
class AcquiredArtifact:
    path: Path
    sha256: str
    size_bytes: int
    source_host: str


StreamOpener = Callable[[str, float], BinaryIO]
SignatureVerifier = Callable[[ArtifactDescriptor, Path], bool]
FreeSpaceReader = Callable[[Path], int]


def _open_https(url: str, timeout: float) -> BinaryIO:
    return urlopen(url, timeout=timeout)  # noqa: S310 - HTTPS and host policy are checked first.


def _free_space(path: Path) -> int:
    return shutil.disk_usage(path).free


class ArtifactAcquirer:
    def __init__(
        self,
        *,
        root: str | Path,
        policy: AcquisitionPolicy,
        stream_opener: StreamOpener = _open_https,
        signature_verifier: SignatureVerifier | None = None,
        free_space_reader: FreeSpaceReader = _free_space,
    ) -> None:
        self.root = Path(root).resolve(strict=False)
        self.policy = policy
        self._stream_opener = stream_opener
        self._signature_verifier = signature_verifier
        self._free_space_reader = free_space_reader

    def acquire(self, descriptor: ArtifactDescriptor, *, artifact_name: str) -> AcquiredArtifact:
        host = (urlsplit(descriptor.url).hostname or "").casefold()
        if host not in self.policy.allowed_hosts:
            raise AcquisitionError("artifact-origin-denied")
        if descriptor.size_bytes > self.policy.max_artifact_bytes:
            raise AcquisitionError("artifact-size-denied")
        if not _ARTIFACT_NAME.fullmatch(artifact_name) or artifact_name in {".", ".."}:
            raise AcquisitionError("artifact-name-invalid")

        self.root.mkdir(parents=True, exist_ok=True)
        if self._free_space_reader(self.root) < descriptor.size_bytes + self.policy.disk_reserve_bytes:
            raise AcquisitionError("artifact-disk-budget-insufficient")

        final_path = self.root / artifact_name
        partial_path = self.root / f".{artifact_name}.{uuid4().hex}.partial"
        digest = sha256()
        total = 0
        try:
            with self._stream_opener(descriptor.url, self.policy.timeout_seconds) as source:
                with partial_path.open("xb") as destination:
                    while True:
                        chunk = source.read(self.policy.chunk_bytes)
                        if not chunk:
                            break
                        if not isinstance(chunk, bytes):
                            raise AcquisitionError("artifact-download-invalid")
                        total += len(chunk)
                        if total > descriptor.size_bytes or total > self.policy.max_artifact_bytes:
                            raise AcquisitionError("artifact-size-mismatch")
                        destination.write(chunk)
                        digest.update(chunk)
                    destination.flush()
                    os.fsync(destination.fileno())
            if total != descriptor.size_bytes:
                raise AcquisitionError("artifact-size-mismatch")
            digest_hex = digest.hexdigest()
            if digest_hex != descriptor.sha256:
                raise AcquisitionError("artifact-digest-mismatch")
            if descriptor.signature is not None:
                if self._signature_verifier is None:
                    raise AcquisitionError("artifact-signature-unverified")
                if not self._signature_verifier(descriptor, partial_path):
                    raise AcquisitionError("artifact-signature-invalid")
            os.replace(partial_path, final_path)
            return AcquiredArtifact(
                path=final_path,
                sha256=digest_hex,
                size_bytes=total,
                source_host=host,
            )
        except AcquisitionError:
            partial_path.unlink(missing_ok=True)
            raise
        except Exception:
            partial_path.unlink(missing_ok=True)
            raise AcquisitionError("artifact-download-failed") from None
