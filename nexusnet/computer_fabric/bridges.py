from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import socket
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from nexus.schemas import utcnow


class BridgeAdapter(Protocol):
    def probe(self) -> dict[str, object]: ...

    def send(self, destination: str, payload: dict[str, object]) -> dict[str, object]: ...


class LocalArtifactBridgeAdapter:
    """A real local transport that appends sanitized messages to the artifact outbox."""

    def __init__(self, *, artifacts_dir: Path) -> None:
        self.outbox_dir = Path(artifacts_dir) / "bridges" / "outbox"
        self.outbox_dir.mkdir(parents=True, exist_ok=True)

    def probe(self) -> dict[str, object]:
        return {"healthy": self.outbox_dir.is_dir(), "detail": "local artifact outbox"}

    def send(self, destination: str, payload: dict[str, object]) -> dict[str, object]:
        message_id = f"bridge_message_{uuid4().hex[:16]}"
        path = self.outbox_dir / f"{message_id}.json"
        path.write_text(
            json.dumps(
                {
                    "message_id": message_id,
                    "destination": destination,
                    "payload": payload,
                    "created_at": utcnow().isoformat(),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return {"transport_id": message_id, "artifact_path": str(path)}


class JsonHttpBridgeAdapter:
    MAX_RESPONSE_BYTES = 65_536

    def __init__(
        self,
        *,
        endpoint: str,
        headers: Mapping[str, str] | None = None,
        allow_private_network: bool = False,
        timeout_seconds: int = 15,
    ) -> None:
        _validate_http_endpoint(endpoint, allow_private_network=allow_private_network)
        self.endpoint = endpoint
        self.headers = {str(key): str(value) for key, value in (headers or {}).items()}
        self.allow_private_network = allow_private_network
        self.timeout_seconds = timeout_seconds

    def probe(self) -> dict[str, object]:
        request = Request(self.endpoint, headers={"User-Agent": "NexusNet-Bridge/1.0"}, method="HEAD")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                _validate_http_endpoint(response.geturl(), allow_private_network=self.allow_private_network)
                status_code = int(response.status)
        except HTTPError as exc:
            status_code = int(exc.code)
        except OSError as exc:
            return {"healthy": False, "detail": type(exc).__name__}
        return {"healthy": status_code < 500, "detail": f"http:{status_code}", "status_code": status_code}

    def send(self, destination: str, payload: dict[str, object]) -> dict[str, object]:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = {"User-Agent": "NexusNet-Bridge/1.0", "Content-Type": "application/json", **self.headers}
        request = Request(self.endpoint, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                _validate_http_endpoint(response.geturl(), allow_private_network=self.allow_private_network)
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
                if len(raw) > self.MAX_RESPONSE_BYTES:
                    raise RuntimeError("bridge response exceeds bounded size")
                status_code = int(response.status)
        except HTTPError as exc:
            raise RuntimeError(f"bridge HTTP dispatch failed: {exc.code}") from exc
        text = raw.decode("utf-8", errors="replace")
        try:
            response_payload: object = json.loads(text) if text else {}
        except json.JSONDecodeError:
            response_payload = {"text": text[:4096]}
        return {
            "transport_id": f"http_{hashlib.sha256(body).hexdigest()[:16]}",
            "status_code": status_code,
            "response": response_payload,
            "endpoint_digest": hashlib.sha256(self.endpoint.encode("utf-8")).hexdigest(),
        }


class BridgeManager:
    def __init__(self, *, artifacts_dir: Path, adapters: Mapping[str, BridgeAdapter] | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.bridges_dir = self.artifacts_dir / "bridges"
        self.receipts_dir = self.bridges_dir / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_path = self.bridges_dir / "catalog.json"
        self._adapters = dict(adapters or {})
        self._bridges: dict[str, dict[str, Any]] = {}
        self._commitments: dict[str, dict[str, Any]] = {}
        self._load_persisted_state()

    def register_adapter(self, transport: str, adapter: BridgeAdapter) -> None:
        self._adapters[transport] = adapter

    def register_bridge(self, spec: dict[str, Any]) -> dict[str, Any]:
        bridge_id = str(spec.get("bridge_id") or "").strip()
        transport = str(spec.get("transport") or "").strip()
        permissions = sorted({str(item) for item in spec.get("permissions") or []})
        if not bridge_id or not transport:
            raise ValueError("bridge_id and transport are required")
        if transport not in self._adapters:
            raise ValueError(f"transport adapter is not registered: {transport}")
        bridge = {
            "bridge_id": bridge_id,
            "transport": transport,
            "permissions": permissions,
            "redaction_policy": str(spec.get("redaction_policy") or "pii-secrets-local-paths"),
        }
        self._bridges[bridge_id] = bridge
        self._persist_catalog()
        return deepcopy(bridge)

    def probe(self, bridge_id: str) -> dict[str, Any]:
        bridge = self._bridge(bridge_id)
        result = dict(self._adapters[bridge["transport"]].probe())
        return {"bridge_id": bridge_id, **result}

    def summary(self) -> dict[str, Any]:
        commitments = sorted(
            self._commitments.values(),
            key=lambda item: item.get("created_at") or "",
            reverse=True,
        )
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "bridge-manager",
            "runtime_state": "live-bound",
            "bridge_count": len(self._bridges),
            "adapter_transports": sorted(self._adapters),
            "bridges": [deepcopy(self._bridges[key]) for key in sorted(self._bridges)],
            "commitment_count": len(commitments),
            "recent_commitments": [
                {
                    "commitment_id": item["commitment_id"],
                    "bridge_id": item["bridge_id"],
                    "state": item["state"],
                    "created_at": item["created_at"],
                }
                for item in commitments[:20]
            ],
            "raw_payload_exposed": False,
        }

    def prepare_outbound(
        self,
        *,
        bridge_id: str,
        destination: str,
        payload: dict[str, object],
    ) -> dict[str, Any]:
        bridge = self._bridge(bridge_id)
        if "send" not in bridge["permissions"]:
            raise PermissionError(f"bridge does not permit send: {bridge_id}")
        sanitized_payload = _redact(deepcopy(payload))
        commitment_id = f"bridge_commitment_{uuid4().hex[:16]}"
        commitment = {
            "commitment_id": commitment_id,
            "bridge_id": bridge_id,
            "destination": destination,
            "sanitized_payload": sanitized_payload,
            "payload_digest": hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest(),
            "state": "pending_approval",
            "approved_by": None,
            "created_at": utcnow().isoformat(),
        }
        self._commitments[commitment_id] = commitment
        self._persist(commitment)
        return deepcopy(commitment)

    def approve(self, commitment_id: str, *, approved_by: str) -> dict[str, Any]:
        commitment = self._commitment(commitment_id)
        if not approved_by.strip():
            raise ValueError("approved_by is required")
        commitment["state"] = "approved"
        commitment["approved_by"] = approved_by.strip()
        commitment["approved_at"] = utcnow().isoformat()
        self._persist(commitment)
        return deepcopy(commitment)

    def dispatch(self, commitment_id: str) -> dict[str, Any]:
        commitment = self._commitment(commitment_id)
        if commitment["state"] != "approved":
            raise PermissionError("outbound commitment requires operator approval")
        bridge = self._bridge(commitment["bridge_id"])
        adapter = self._adapters[bridge["transport"]]
        health = dict(adapter.probe())
        if health.get("healthy") is not True:
            raise RuntimeError(f"bridge transport is unhealthy: {health.get('detail', 'unknown')}")
        transport_receipt = adapter.send(commitment["destination"], deepcopy(commitment["sanitized_payload"]))
        commitment["state"] = "dispatched"
        commitment["dispatched_at"] = utcnow().isoformat()
        commitment["transport_health"] = health
        commitment["transport_receipt"] = transport_receipt
        self._persist(commitment)
        return deepcopy(commitment)

    def _bridge(self, bridge_id: str) -> dict[str, Any]:
        try:
            return self._bridges[bridge_id]
        except KeyError as exc:
            raise KeyError(f"unknown bridge: {bridge_id}") from exc

    def _commitment(self, commitment_id: str) -> dict[str, Any]:
        if commitment_id not in self._commitments:
            path = self.receipts_dir / f"{commitment_id}.json"
            if path.exists():
                self._commitments[commitment_id] = json.loads(path.read_text(encoding="utf-8"))
        try:
            return self._commitments[commitment_id]
        except KeyError as exc:
            raise KeyError(f"unknown commitment: {commitment_id}") from exc

    def _persist(self, payload: dict[str, Any]) -> None:
        path = self.receipts_dir / f"{payload['commitment_id']}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def _persist_catalog(self) -> None:
        temporary = self.catalog_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"bridges": list(self._bridges.values())}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.catalog_path)

    def _load_persisted_state(self) -> None:
        if self.catalog_path.is_file():
            try:
                catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                catalog = {}
            for bridge in catalog.get("bridges") or []:
                if not isinstance(bridge, dict):
                    continue
                bridge_id = str(bridge.get("bridge_id") or "")
                if bridge_id:
                    self._bridges[bridge_id] = bridge
        for path in self.receipts_dir.glob("bridge_commitment_*.json"):
            try:
                commitment = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            commitment_id = str(commitment.get("commitment_id") or "")
            if commitment_id:
                self._commitments[commitment_id] = commitment


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_SECRET = re.compile(r"\b(?:sk|ghp|hf)[_-][A-Za-z0-9_-]{6,}\b", re.IGNORECASE)
_WINDOWS_PATH = re.compile(r"\b[A-Za-z]:\\[^\s]+")


def _redact(value: Any) -> Any:
    if isinstance(value, str):
        value = _EMAIL.sub("[REDACTED_EMAIL]", value)
        value = _SECRET.sub("[REDACTED_SECRET]", value)
        return _WINDOWS_PATH.sub("[REDACTED_LOCAL_PATH]", value)
    if isinstance(value, dict):
        return {str(key): _redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _validate_http_endpoint(endpoint: str, *, allow_private_network: bool) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("bridge endpoint must use http or https")
    if allow_private_network:
        return
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port or 443)}
    except socket.gaierror as exc:
        raise ValueError(f"bridge endpoint host could not be resolved: {parsed.hostname}") from exc
    for raw_address in addresses:
        address = ipaddress.ip_address(raw_address)
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            raise ValueError("bridge endpoint resolves to a private network")
