from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import secrets
import sys
from pathlib import Path
from typing import Any


class ObjectCapabilityRPCFabric:
    def __init__(self) -> None:
        self._objects: dict[str, dict[str, Any]] = {}

    def register(self, value: Any, *, allowed_methods: set[str], owner_ref: str) -> str:
        if not allowed_methods or not owner_ref:
            raise ValueError("object capability requires method rights and owner_ref")
        for method in allowed_methods:
            if not callable(getattr(value, method, None)):
                raise ValueError(f"object does not provide callable method: {method}")
        handle = "ocap:" + secrets.token_urlsafe(32)
        self._objects[handle] = {"value": value, "allowed_methods": set(allowed_methods), "owner_ref": owner_ref}
        return handle

    def invoke(self, handle: str, *, method: str, args: list[Any], kwargs: dict[str, Any]) -> dict[str, Any]:
        capability = self._objects.get(handle)
        if capability is None:
            raise PermissionError("unknown object capability handle")
        if method not in capability["allowed_methods"]:
            raise PermissionError("method is outside object capability rights")
        result = getattr(capability["value"], method)(*args, **kwargs)
        return {
            "decision": "allowed",
            "method": method,
            "owner_ref": capability["owner_ref"],
            "result": result,
            "result_digest": "sha256:" + hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest(),
        }


class IsolationAndSupplyChainRuntime:
    def __init__(self, *, signing_key: bytes) -> None:
        if not signing_key:
            raise ValueError("signing_key is required")
        self.key = bytes(signing_key)

    def check_taint_flow(self, *, labels: set[str], sink: str, allowed_labels: set[str]) -> dict[str, Any]:
        disallowed = sorted(labels - allowed_labels)
        return {
            "sink": sink,
            "decision": "deny" if disallowed else "allow",
            "labels": sorted(labels),
            "disallowed_labels": disallowed,
        }

    def verify_update(self, *, manifest: dict[str, Any], artifacts: dict[str, bytes], signature: str) -> dict[str, Any]:
        canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        expected_signature = hmac.new(self.key, canonical, hashlib.sha256).hexdigest()
        hash_errors = []
        for name, expected_hash in manifest.get("artifacts", {}).items():
            content = artifacts.get(name)
            if content is None or hashlib.sha256(content).hexdigest() != expected_hash:
                hash_errors.append(name)
        extra = sorted(set(artifacts) - set(manifest.get("artifacts", {})))
        verified = hmac.compare_digest(signature, expected_signature) and not hash_errors and not extra
        return {
            "verified": verified,
            "signature_valid": hmac.compare_digest(signature, expected_signature),
            "hash_error_artifacts": sorted(hash_errors),
            "unmanifested_artifacts": extra,
            "decision": "allow-install" if verified else "deny-install",
        }

    @staticmethod
    def verify_reproducible_build(artifacts: list[bytes]) -> dict[str, Any]:
        if len(artifacts) < 2:
            raise ValueError("reproducibility requires at least two independent artifacts")
        digests = [hashlib.sha256(content).hexdigest() for content in artifacts]
        return {"reproducible": len(set(digests)) == 1, "digests": digests, "builder_count": len(artifacts)}

    @staticmethod
    def probe_native_isolation() -> dict[str, dict[str, Any]]:
        probes = {
            "wasm": bool(importlib.util.find_spec("wasmtime") or importlib.util.find_spec("wasmer")),
            "landlock": sys.platform.startswith("linux") and Path("/sys/kernel/security/landlock").exists(),
            "seccomp": sys.platform.startswith("linux") and bool(importlib.util.find_spec("seccomp")),
            "confidential-compute": any(Path(path).exists() for path in ("/dev/sev", "/dev/tdx-guest")),
            "zkvm": bool(importlib.util.find_spec("risc0_zkvm") or importlib.util.find_spec("sp1")),
        }
        return {
            name: {
                "status": "available" if available else "unavailable",
                "execution_allowed": bool(available),
                "fail_closed": True,
                "reason": None if available else "native-provider-not-detected",
            }
            for name, available in probes.items()
        }
