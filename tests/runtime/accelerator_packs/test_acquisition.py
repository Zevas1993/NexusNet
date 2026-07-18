from hashlib import sha256
from io import BytesIO

import pytest

from nexusnet.runtime.accelerator_packs.acquisition import (
    AcquisitionError,
    AcquisitionPolicy,
    ArtifactAcquirer,
)
from nexusnet.runtime.accelerator_packs.contracts import ArtifactDescriptor


def _descriptor(payload: bytes, *, host: str = "downloads.nexusnet.local") -> ArtifactDescriptor:
    return ArtifactDescriptor(
        url=f"https://{host}/packs/worker.bin",
        size_bytes=len(payload),
        sha256=sha256(payload).hexdigest(),
    )


def test_artifact_acquirer_streams_verified_payload_into_atomic_final_path(tmp_path):
    payload = b"verified-pack-payload"
    acquirer = ArtifactAcquirer(
        root=tmp_path / "cache",
        policy=AcquisitionPolicy(
            allowed_hosts=frozenset({"downloads.nexusnet.local"}),
            max_artifact_bytes=1024,
            disk_reserve_bytes=0,
        ),
        stream_opener=lambda _url, _timeout: BytesIO(payload),
        free_space_reader=lambda _path: 4096,
    )

    acquired = acquirer.acquire(_descriptor(payload), artifact_name="worker.bin")

    assert acquired.path.read_bytes() == payload
    assert acquired.size_bytes == len(payload)
    assert acquired.sha256 == sha256(payload).hexdigest()
    assert acquired.path.name == "worker.bin"
    assert list((tmp_path / "cache").glob("*.partial")) == []


@pytest.mark.parametrize(
    ("descriptor", "policy", "expected"),
    [
        (_descriptor(b"payload", host="private.invalid"), AcquisitionPolicy(allowed_hosts=frozenset({"downloads.nexusnet.local"})), "artifact-origin-denied"),
        (_descriptor(b"payload"), AcquisitionPolicy(allowed_hosts=frozenset({"downloads.nexusnet.local"}), max_artifact_bytes=3), "artifact-size-denied"),
    ],
)
def test_artifact_acquirer_rejects_disallowed_origin_and_size_before_opening(tmp_path, descriptor, policy, expected):
    opened = False

    def opener(_url, _timeout):
        nonlocal opened
        opened = True
        return BytesIO(b"payload")

    with pytest.raises(AcquisitionError, match=expected):
        ArtifactAcquirer(root=tmp_path, policy=policy, stream_opener=opener).acquire(
            descriptor,
            artifact_name="worker.bin",
        )

    assert opened is False


def test_artifact_acquirer_removes_partial_output_on_digest_failure(tmp_path):
    expected = b"expected"
    actual = b"tampered"
    acquirer = ArtifactAcquirer(
        root=tmp_path,
        policy=AcquisitionPolicy(
            allowed_hosts=frozenset({"downloads.nexusnet.local"}),
            disk_reserve_bytes=0,
        ),
        stream_opener=lambda _url, _timeout: BytesIO(actual),
        free_space_reader=lambda _path: 4096,
    )

    with pytest.raises(AcquisitionError, match="artifact-digest-mismatch"):
        acquirer.acquire(_descriptor(expected), artifact_name="worker.bin")

    assert list(tmp_path.iterdir()) == []


def test_artifact_acquirer_enforces_disk_reserve_before_opening(tmp_path):
    payload = b"payload"
    opened = False

    def opener(_url, _timeout):
        nonlocal opened
        opened = True
        return BytesIO(payload)

    acquirer = ArtifactAcquirer(
        root=tmp_path,
        policy=AcquisitionPolicy(
            allowed_hosts=frozenset({"downloads.nexusnet.local"}),
            disk_reserve_bytes=100,
        ),
        stream_opener=opener,
        free_space_reader=lambda _path: len(payload) + 99,
    )

    with pytest.raises(AcquisitionError, match="artifact-disk-budget-insufficient"):
        acquirer.acquire(_descriptor(payload), artifact_name="worker.bin")

    assert opened is False


def test_artifact_acquirer_requires_and_enforces_declared_signature(tmp_path):
    payload = b"signed-payload"
    descriptor = ArtifactDescriptor(
        url="https://downloads.nexusnet.local/packs/signed.bin",
        size_bytes=len(payload),
        sha256=sha256(payload).hexdigest(),
        signature="publisher-signature",
        signature_kind="publisher-native",
    )
    policy = AcquisitionPolicy(
        allowed_hosts=frozenset({"downloads.nexusnet.local"}),
        disk_reserve_bytes=0,
    )

    with pytest.raises(AcquisitionError, match="artifact-signature-unverified"):
        ArtifactAcquirer(
            root=tmp_path / "missing-verifier",
            policy=policy,
            stream_opener=lambda _url, _timeout: BytesIO(payload),
            free_space_reader=lambda _path: 4096,
        ).acquire(descriptor, artifact_name="signed.bin")

    with pytest.raises(AcquisitionError, match="artifact-signature-invalid"):
        ArtifactAcquirer(
            root=tmp_path / "invalid-signature",
            policy=policy,
            stream_opener=lambda _url, _timeout: BytesIO(payload),
            signature_verifier=lambda _descriptor, _path: False,
            free_space_reader=lambda _path: 4096,
        ).acquire(descriptor, artifact_name="signed.bin")
