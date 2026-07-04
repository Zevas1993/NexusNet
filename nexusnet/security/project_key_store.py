from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from pathlib import Path


class ProjectLocalSigningKeyStore:
    SCHEMA_VERSION = "project_local_signing_key.v0.1"
    KDF = "pbkdf2_hmac_sha256"
    CIPHER = "hmac_sha256_stream_xor_v0"
    ITERATIONS = 210_000

    @classmethod
    def create(cls, path: Path, *, seed: bytes, passphrase: str) -> dict[str, object]:
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes")
        if not passphrase:
            raise ValueError("Project-local signing key passphrase is required")
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(16)
        enc_key, mac_key = cls._derive_keys(passphrase, salt, cls.ITERATIONS)
        ciphertext = cls._xor(seed, cls._stream(enc_key, nonce, len(seed)))
        envelope = {
            "schema_version": cls.SCHEMA_VERSION,
            "storage_scope": "project_local_encrypted_file",
            "kdf": cls.KDF,
            "cipher": cls.CIPHER,
            "iterations": cls.ITERATIONS,
            "salt": cls._b64(salt),
            "nonce": cls._b64(nonce),
            "ciphertext": cls._b64(ciphertext),
            "plaintext_length": len(seed),
            "secret_persisted": False,
        }
        envelope["tag"] = cls._tag(mac_key, envelope)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {
            "schema_version": "project_local_signing_key_record.v0.1",
            "storage_scope": "project_local_encrypted_file",
            "key_file_path": str(path),
            "secret_persisted": False,
        }

    @classmethod
    def load_seed(cls, path: Path, *, passphrase: str) -> bytes:
        if not passphrase:
            raise ValueError("Project-local signing key passphrase is required")
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            salt = cls._unb64(str(envelope["salt"]))
            nonce = cls._unb64(str(envelope["nonce"]))
            ciphertext = cls._unb64(str(envelope["ciphertext"]))
            iterations = int(envelope["iterations"])
            stored_tag = str(envelope["tag"])
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Project-local signing key file is invalid") from exc
        enc_key, mac_key = cls._derive_keys(passphrase, salt, iterations)
        expected_tag = cls._tag(mac_key, envelope)
        if not hmac.compare_digest(stored_tag, expected_tag):
            raise ValueError("Project-local signing key decrypt failed")
        seed = cls._xor(ciphertext, cls._stream(enc_key, nonce, len(ciphertext)))
        if len(seed) != 32:
            raise ValueError("Project-local signing key decrypt failed")
        return seed

    @classmethod
    def _derive_keys(cls, passphrase: str, salt: bytes, iterations: int) -> tuple[bytes, bytes]:
        key_material = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations, dklen=64)
        return key_material[:32], key_material[32:]

    @staticmethod
    def _stream(key: bytes, nonce: bytes, length: int) -> bytes:
        output = bytearray()
        counter = 0
        while len(output) < length:
            output.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
            counter += 1
        return bytes(output[:length])

    @staticmethod
    def _xor(left: bytes, right: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(left, right))

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.b64encode(value).decode("ascii")

    @staticmethod
    def _unb64(value: str) -> bytes:
        return base64.b64decode(value.encode("ascii"), validate=True)

    @classmethod
    def _tag(cls, mac_key: bytes, envelope: dict[str, object]) -> str:
        signed = {key: value for key, value in envelope.items() if key != "tag"}
        payload = json.dumps(signed, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return hmac.new(mac_key, payload, hashlib.sha256).hexdigest()
