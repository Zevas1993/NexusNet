from __future__ import annotations

import hashlib
import hmac
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvidenceStandardsRuntime:
    """Content-addressed evidence DAG with signed local receipts and provenance exports."""

    def __init__(self, *, artifacts_dir: Path | str, signing_key: bytes) -> None:
        if not signing_key:
            raise ValueError("signing_key is required")
        self.key = bytes(signing_key)
        self.root = Path(artifacts_dir) / "evidence-standards"
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "state.json"
        if not self.state_path.exists():
            self._save({"nodes": {}, "transparency_log": []})

    def add_node(self, *, kind: str, subject_ref: str, payload: dict[str, Any], source_refs: list[str], parent_refs: list[str]) -> dict[str, Any]:
        state = self._load()
        missing = [ref for ref in parent_refs if ref not in state["nodes"]]
        if missing:
            raise ValueError(f"unknown parent refs: {missing}")
        if not kind or not subject_ref or not source_refs:
            raise ValueError("evidence node requires kind, subject_ref, and source_refs")
        base = {
            "kind": kind,
            "subject_ref": subject_ref,
            "payload": deepcopy(payload),
            "source_refs": sorted(set(source_refs)),
            "parent_refs": list(dict.fromkeys(parent_refs)),
        }
        content_hash = "sha256:" + hashlib.sha256(self._canonical(base)).hexdigest()
        node = {**base, "content_hash": content_hash}
        state["nodes"][content_hash] = node
        self._save(state)
        return deepcopy(node)

    def verify_dag(self) -> dict[str, Any]:
        state = self._load()
        errors: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(ref: str) -> None:
            if ref in visiting:
                errors.append(f"cycle:{ref}")
                return
            if ref in visited:
                return
            node = state["nodes"].get(ref)
            if node is None:
                errors.append(f"missing:{ref}")
                return
            expected = "sha256:" + hashlib.sha256(
                self._canonical({key: node[key] for key in ("kind", "subject_ref", "payload", "source_refs", "parent_refs")})
            ).hexdigest()
            if expected != ref:
                errors.append(f"hash:{ref}")
            visiting.add(ref)
            for parent in node["parent_refs"]:
                visit(parent)
            visiting.remove(ref)
            visited.add(ref)

        for ref in sorted(state["nodes"]):
            visit(ref)
        return {"valid": not errors, "errors": sorted(set(errors)), "node_count": len(state["nodes"])}

    def issue_time_receipt(self, *, subject_ref: str) -> dict[str, Any]:
        return self._signed({
            "receipt_kind": "TrustedTimeReceipt",
            "subject_ref": subject_ref,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "assurance": "local-signed-clock-not-external-tsa",
        })

    def append_transparency_receipt(self, *, subject_ref: str, evidence_refs: list[str]) -> dict[str, Any]:
        if not evidence_refs:
            raise ValueError("transparency receipt requires evidence_refs")
        state = self._load()
        record = self._signed({
            "receipt_kind": "TransparencyReceipt",
            "subject_ref": subject_ref,
            "evidence_refs": sorted(set(evidence_refs)),
            "sequence": len(state["transparency_log"]) + 1,
            "previous_receipt_hash": state["transparency_log"][-1]["receipt_hash"] if state["transparency_log"] else None,
            "standard_posture": "scitt-inspired-not-standards-conformant",
        })
        state["transparency_log"].append(record)
        self._save(state)
        return deepcopy(record)

    def issue_content_credential(self, *, subject_ref: str, claim_refs: list[str], issuer_ref: str) -> dict[str, Any]:
        if not claim_refs:
            raise ValueError("content credential requires claim_refs")
        return self._signed({
            "receipt_kind": "ContentCredential",
            "subject_ref": subject_ref,
            "claim_refs": sorted(set(claim_refs)),
            "issuer_ref": issuer_ref,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "standard_posture": "c2pa-inspired-manifest-not-c2pa-binary",
        })

    def verify_signed_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        signature = str(receipt.get("signature") or "")
        unsigned = {key: value for key, value in receipt.items() if key not in {"signature", "receipt_hash"}}
        expected = hmac.new(self.key, self._canonical(unsigned), hashlib.sha256).hexdigest()
        receipt_hash = "sha256:" + hashlib.sha256(self._canonical(unsigned)).hexdigest()
        return {"valid": hmac.compare_digest(signature, expected) and receipt.get("receipt_hash") == receipt_hash, "receipt_hash": receipt_hash}

    def export_provenance_crate(self, *, crate_id: str, root_refs: list[str]) -> dict[str, Any]:
        state = self._load()
        if not root_refs:
            raise ValueError("provenance crate requires root_refs")
        closure: set[str] = set()

        def include(ref: str) -> None:
            node = state["nodes"].get(ref)
            if node is None:
                raise ValueError(f"unknown crate root or parent: {ref}")
            if ref in closure:
                return
            for parent in node["parent_refs"]:
                include(parent)
            closure.add(ref)

        for ref in root_refs:
            include(ref)
        replay_order = self._topological_order(state["nodes"], closure)
        crate = {
            "schema_version": "nexusnet-provenance-crate-v1",
            "standard_posture": "ro-crate-prov-inspired-json-not-conformance-claim",
            "crate_id": crate_id,
            "status": "exported",
            "root_refs": list(root_refs),
            "entities": [deepcopy(state["nodes"][ref]) for ref in replay_order],
            "replay_order": replay_order,
        }
        path = self.root / f"crate-{hashlib.sha256(crate_id.encode()).hexdigest()[:16]}.json"
        self._write(path, crate)
        crate["artifact_path"] = str(path)
        return crate

    @staticmethod
    def _topological_order(nodes: dict[str, dict[str, Any]], closure: set[str]) -> list[str]:
        order: list[str] = []
        visited: set[str] = set()

        def visit(ref: str) -> None:
            if ref in visited:
                return
            for parent in nodes[ref]["parent_refs"]:
                if parent in closure:
                    visit(parent)
            visited.add(ref)
            order.append(ref)

        for ref in sorted(closure):
            visit(ref)
        return order

    def _signed(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            **payload,
            "receipt_hash": "sha256:" + hashlib.sha256(self._canonical(payload)).hexdigest(),
            "signature": hmac.new(self.key, self._canonical(payload), hashlib.sha256).hexdigest(),
        }

    def _load(self) -> dict[str, Any]:
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self._write(self.state_path, payload)

    @staticmethod
    def _write(path: Path, payload: dict[str, Any]) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, path)

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
