from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from nexusnet.security.assimilation_runtime import IsolationAndSupplyChainRuntime, ObjectCapabilityRPCFabric


class _Calculator:
    def add(self, left, right):
        return left + right

    def reset(self):
        return "reset"


def test_object_capability_rpc_uses_opaque_handles_and_method_rights():
    fabric = ObjectCapabilityRPCFabric()
    handle = fabric.register(_Calculator(), allowed_methods={"add"}, owner_ref="service:math")

    assert "service:math" not in handle
    assert fabric.invoke(handle, method="add", args=[2, 3], kwargs={})["result"] == 5
    with pytest.raises(PermissionError):
        fabric.invoke(handle, method="reset", args=[], kwargs={})


def test_taint_update_reproducibility_and_native_isolation_are_fail_closed():
    runtime = IsolationAndSupplyChainRuntime(signing_key=b"supply-key")
    taint = runtime.check_taint_flow(
        labels={"private", "untrusted"},
        sink="public-network",
        allowed_labels={"public", "verified"},
    )
    assert taint["decision"] == "deny"

    artifact = b"runtime-binary"
    manifest = {"version": "1.2.3", "artifacts": {"runtime.bin": hashlib.sha256(artifact).hexdigest()}}
    signature = hmac.new(b"supply-key", json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
    update = runtime.verify_update(manifest=manifest, artifacts={"runtime.bin": artifact}, signature=signature)
    assert update["verified"] is True
    assert runtime.verify_reproducible_build([artifact, artifact])["reproducible"] is True
    assert runtime.verify_reproducible_build([artifact, b"different"])["reproducible"] is False

    profiles = runtime.probe_native_isolation()
    assert set(profiles) == {"wasm", "landlock", "seccomp", "confidential-compute", "zkvm"}
    assert all(item["status"] in {"available", "unavailable"} for item in profiles.values())
    assert all(item["fail_closed"] is True for item in profiles.values())
