from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any


CANON_CONTRACT_SCHEMA = "nexusnet-whole-project-canon-contract-ledger-v1"
CANON_CONTRACT_SURFACE_ID = "whole-project-canon-contract-ledger"
CANON_CONTRACT_RECEIPT_SCHEMA = "nexusnet-whole-project-canon-contract-receipt-v1"
CANON_CONTRACT_RECEIPT_SURFACE_ID = "whole-project-canon-contract-receipt"

CANON_CONTRACT_SOURCE_REFS = (
    "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
    "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md",
    "docs/research/CANON_DEEP_DETAIL_ADDENDUM_2026-05-31.md",
    "docs/research/CANON_VS_ASSIMILATION_IMPROVEMENTS_2026-05-31.md",
    "docs/research/CANON_IMPLEMENTATION_LEDGER.md",
    "docs/assimilation/NEXUSNET_ALL_ASSIMILATION_TARGETS_CONSOLIDATED_2026-05-31.md",
    "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
)

def build_canon_contract_ledger(
    project_root: Path | str,
    runtime: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a sanitized whole-project canon contract ledger from local canon files and runtime evidence."""

    root = Path(project_root)
    source_manifest = build_canon_source_manifest(root)
    runtime_evidence = runtime if isinstance(runtime, dict) else {}
    contracts = [_contract_row(spec, runtime_evidence) for spec in _contract_specs()]
    evidence_present_count = sum(1 for contract in contracts if contract["status"] == "evidence-present")
    partial_count = sum(1 for contract in contracts if contract["status"] == "partial")
    missing_count = sum(1 for contract in contracts if contract["status"] == "missing")
    coverage_status = (
        "covered"
        if missing_count == 0 and partial_count == 0 and source_manifest["missing_source_count"] == 0
        else "missing"
        if source_manifest["ingested_source_count"] == 0 or missing_count == len(contracts)
        else "partial"
    )
    return {
        "schema_version": CANON_CONTRACT_SCHEMA,
        "surface_id": CANON_CONTRACT_SURFACE_ID,
        "status_label": "LOCKED CANON",
        "honest_status_label": "whole-project-canon-bound-runtime-contracts",
        "product_surface": "wrapper",
        "product_scope": "whole-system",
        "source_manifest": source_manifest,
        "contract_count": len(contracts),
        "evidence_present_count": evidence_present_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "coverage_status": coverage_status,
        "contracts": contracts,
        "evidence_refs": _dedupe(
            [
                "canon-contract-source-manifest::local-files",
                *[f"canon-source::{source['source_ref']}" for source in source_manifest["sources"] if source["status"] == "ingested"],
                *[ref for contract in contracts for ref in contract["evidence_refs"]],
            ]
        )[:40],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-canon-source-refs-hashes-counts-headings-keyword-counts-and-runtime-evidence-refs-only-no-raw-canon-text-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "canon-contract-ledger-is-read-only-evidence-no-active-production-mutation",
    }


def build_canon_source_manifest(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    repo_root = Path(__file__).resolve().parents[2]
    fingerprint = _canon_source_fingerprint(project_root=root, repo_root=repo_root)
    return deepcopy(
        _cached_canon_source_manifest(
            str(root),
            str(repo_root),
            fingerprint,
        )
    )


@lru_cache(maxsize=64)
def _cached_canon_source_manifest(
    project_root: str,
    repo_root: str,
    source_fingerprint: tuple[tuple[str, str, str, int, int, int], ...],
) -> dict[str, Any]:
    # source_fingerprint intentionally participates in the cache key. The source
    # records are rebuilt only when a resolved file's identity or stat changes.
    _ = source_fingerprint
    root = Path(project_root)
    resolved_repo_root = Path(repo_root)
    sources = [
        _source_record(source_ref, project_root=root, repo_root=resolved_repo_root)
        for source_ref in CANON_CONTRACT_SOURCE_REFS
    ]
    ingested_count = sum(1 for source in sources if source["status"] == "ingested")
    total_bytes = sum(int(source.get("byte_count") or 0) for source in sources)
    return {
        "schema_version": "nexusnet-canon-source-manifest-v1",
        "surface_id": "whole-project-canon-source-manifest",
        "source_refs": list(CANON_CONTRACT_SOURCE_REFS),
        "source_count": len(CANON_CONTRACT_SOURCE_REFS),
        "ingested_source_count": ingested_count,
        "missing_source_count": len(CANON_CONTRACT_SOURCE_REFS) - ingested_count,
        "total_byte_count": total_bytes,
        "sources": sources,
        "raw_content_included": False,
        "privacy_boundary": "source-refs-byte-counts-sha256-heading-samples-and-keyword-counts-only-no-raw-canon-text-or-local-paths",
    }


def _canon_source_fingerprint(
    *,
    project_root: Path,
    repo_root: Path,
) -> tuple[tuple[str, str, str, int, int, int], ...]:
    fingerprint: list[tuple[str, str, str, int, int, int]] = []
    for source_ref in CANON_CONTRACT_SOURCE_REFS:
        resolved: tuple[Path, str] | None = None
        for candidate, resolved_from in (
            (project_root / source_ref, "project-root"),
            (repo_root / source_ref, "repo-root"),
        ):
            if candidate.is_file():
                resolved = (candidate.resolve(), resolved_from)
                break
        if resolved is None:
            fingerprint.append((source_ref, "missing", "", 0, 0, 0))
            continue
        path, resolved_from = resolved
        try:
            stat = path.stat()
        except OSError:
            fingerprint.append((source_ref, "missing", "", 0, 0, 0))
            continue
        fingerprint.append(
            (
                source_ref,
                resolved_from,
                str(path),
                int(stat.st_size),
                int(stat.st_mtime_ns),
                int(stat.st_ctime_ns),
            )
        )
    return tuple(fingerprint)


def compact_canon_contract_ledger(ledger: dict[str, Any] | None) -> dict[str, Any]:
    source_manifest = ledger.get("source_manifest") if isinstance(ledger, dict) else {}
    source_refs = (
        list(source_manifest.get("source_refs") or [])
        if isinstance(source_manifest, dict)
        else list(ledger.get("source_refs") or [])
        if isinstance(ledger, dict)
        else []
    )
    return {
        "surface_id": CANON_CONTRACT_SURFACE_ID,
        "schema_version": CANON_CONTRACT_SCHEMA,
        "coverage_status": ledger.get("coverage_status") if isinstance(ledger, dict) else "missing",
        "contract_count": int(ledger.get("contract_count") or 0) if isinstance(ledger, dict) else 0,
        "evidence_present_count": int(ledger.get("evidence_present_count") or 0) if isinstance(ledger, dict) else 0,
        "partial_count": int(ledger.get("partial_count") or 0) if isinstance(ledger, dict) else 0,
        "missing_count": int(ledger.get("missing_count") or 0) if isinstance(ledger, dict) else 0,
        "source_count": int(
            (source_manifest.get("source_count") if isinstance(source_manifest, dict) else ledger.get("source_count"))
            or 0
        )
        if isinstance(ledger, dict)
        else 0,
        "ingested_source_count": int(source_manifest.get("ingested_source_count") or 0)
        if isinstance(source_manifest, dict)
        else int(ledger.get("ingested_source_count") or 0)
        if isinstance(ledger, dict)
        else 0,
        "missing_source_count": int(source_manifest.get("missing_source_count") or 0)
        if isinstance(source_manifest, dict)
        else int(ledger.get("missing_source_count") or 0)
        if isinstance(ledger, dict)
        else 0,
        "source_refs": source_refs,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "compact-canon-contract-counts-source-refs-and-status-only-no-raw-canon-text-or-local-paths",
    }


def build_canon_contract_receipt(
    *,
    ledger: dict[str, Any],
    interaction: dict[str, Any],
    forward_pass_receipt: dict[str, Any],
) -> dict[str, Any]:
    trace_ref = f"trace::{_safe_ref(str(interaction.get('trace_id') or 'unknown'))}"
    forward_pass_receipt_id = str(forward_pass_receipt.get("receipt_id") or interaction.get("forward_pass_receipt_id") or "")
    gaps = compact_canon_contract_gaps(ledger)
    compact_ledger = compact_canon_contract_ledger(ledger)
    receipt_seed = "|".join(
        [
            trace_ref,
            forward_pass_receipt_id,
            str(compact_ledger.get("coverage_status") or ""),
            str(compact_ledger.get("contract_count") or 0),
            ",".join(row["contract_id"] for row in gaps),
        ]
    )
    receipt_id = f"canon-contract-receipt::{_safe_ref(str(interaction.get('trace_id') or 'trace'))}::{_digest(receipt_seed)}"
    return {
        "schema_version": CANON_CONTRACT_RECEIPT_SCHEMA,
        "surface_id": CANON_CONTRACT_RECEIPT_SURFACE_ID,
        "receipt_id": receipt_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status_label": "LOCKED CANON",
        "coverage_status": compact_ledger["coverage_status"],
        "status": compact_ledger["coverage_status"],
        "session_ref_digest": interaction.get("session_ref_digest") if isinstance(interaction.get("session_ref_digest"), str) else None,
        "trace_ref": trace_ref,
        "forward_pass_receipt_id": forward_pass_receipt_id,
        "forward_pass_status": forward_pass_receipt.get("status") or interaction.get("forward_pass_coverage_status") or "unknown",
        "ledger": compact_ledger,
        "contract_count": compact_ledger["contract_count"],
        "evidence_present_count": compact_ledger["evidence_present_count"],
        "partial_count": compact_ledger["partial_count"],
        "missing_count": compact_ledger["missing_count"],
        "gap_count": len(gaps),
        "gaps": gaps,
        "evidence_refs": _dedupe(
            [
                trace_ref,
                f"forward-pass::{forward_pass_receipt_id}" if forward_pass_receipt_id else "",
                "canon-contract-ledger::whole-project-canon-contract-ledger",
                *[ref for gap in gaps for ref in gap.get("evidence_refs", [])],
            ]
        )[:40],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-canon-contract-receipt-ids-counts-statuses-and-evidence-refs-only-no-raw-canon-text-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "forward-pass-canon-contract-receipt-only-no-active-production-mutation",
    }


def compact_canon_contract_gaps(ledger: dict[str, Any] | None, *, limit: int = 12) -> list[dict[str, Any]]:
    contracts = ledger.get("contracts") if isinstance(ledger, dict) else []
    gaps: list[dict[str, Any]] = []
    for contract in contracts if isinstance(contracts, list) else []:
        if not isinstance(contract, dict):
            continue
        status = str(contract.get("status") or "missing")
        if status == "evidence-present":
            continue
        gaps.append(
            {
                "contract_id": str(contract.get("contract_id") or "canon-contract"),
                "label": str(contract.get("label") or contract.get("contract_id") or "Canon contract"),
                "status": status,
                "blockers": [str(item) for item in (contract.get("blockers") or []) if str(item or "")][:6],
                "evidence_refs": [str(item) for item in (contract.get("evidence_refs") or []) if str(item or "")][:6],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
        )
    return gaps[:limit]


def empty_canon_contract_ledger() -> dict[str, Any]:
    return build_canon_contract_ledger(Path.cwd(), {})


def _source_record(source_ref: str, *, project_root: Path, repo_root: Path) -> dict[str, Any]:
    candidates = ((project_root / source_ref, "project-root"), (repo_root / source_ref, "repo-root"))
    for path, resolved_from in candidates:
        if path.is_file():
            return _ingested_source_record(source_ref, path=path, resolved_from=resolved_from)
    return {
        "source_ref": source_ref,
        "priority": CANON_CONTRACT_SOURCE_REFS.index(source_ref) + 1,
        "status": "missing",
        "resolved_from": None,
        "byte_count": 0,
        "sha256": None,
        "heading_count": 0,
        "sample_headings": [],
        "keyword_counts": {},
        "raw_content_included": False,
    }


def _ingested_source_record(source_ref: str, *, path: Path, resolved_from: str) -> dict[str, Any]:
    digest = hashlib.sha256()
    byte_count = 0
    heading_count = 0
    sample_headings: list[str] = []
    keyword_pairs = (
        ("wrapper", "wrapper"),
        ("federated", "federated"),
        ("federation", "federation"),
        ("assimilation", "assimilation"),
        ("dream", "dream"),
        ("research", "research"),
        ("self-repair", "self-repair"),
        ("self repair", "self-repair"),
        ("autonomous", "autonomous"),
        ("context", "context"),
        ("cache", "cache"),
        ("expert", "expert"),
        ("teacher", "teacher"),
        ("ao", "ao"),
        ("visualizer", "visualizer"),
        ("control panel", "control-panel"),
    )
    keyword_counts: dict[str, int] = {value: 0 for _, value in keyword_pairs}
    with path.open("rb") as handle:
        for raw_line in handle:
            byte_count += len(raw_line)
            digest.update(raw_line)
            line = raw_line.decode("utf-8", errors="ignore")
            stripped = line.strip()
            if stripped.startswith("#"):
                heading_count += 1
                if len(sample_headings) < 8:
                    sample_headings.append(_sanitize_heading(stripped))
            lowered = line.lower()
            for needle, bucket in keyword_pairs:
                if needle in lowered:
                    keyword_counts[bucket] = keyword_counts.get(bucket, 0) + lowered.count(needle)
    return {
        "source_ref": source_ref,
        "priority": CANON_CONTRACT_SOURCE_REFS.index(source_ref) + 1,
        "status": "ingested",
        "resolved_from": resolved_from,
        "byte_count": byte_count,
        "sha256": f"sha256:{digest.hexdigest()}",
        "heading_count": heading_count,
        "sample_headings": sample_headings,
        "keyword_counts": {key: count for key, count in keyword_counts.items() if count > 0},
        "raw_content_included": False,
    }


def _sanitize_heading(heading: str) -> str:
    cleaned = " ".join(heading.replace("\t", " ").split())
    return cleaned[:160]


def _safe_ref(value: str) -> str:
    cleaned = value.replace("\\", "/")
    for token in (":", " ", "\t", "\r", "\n"):
        cleaned = cleaned.replace(token, "_")
    return cleaned[:160] or "unknown"


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _contract_row(spec: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    evidence = [runtime.get(key) for key in spec["runtime_keys"] if isinstance(runtime.get(key), dict)]
    present = [item for item in evidence if _evidence_present(item)]
    blockers = list(spec.get("blockers") or [])
    if not evidence:
        status = "missing"
        blockers.append("runtime_evidence_missing")
    elif len(present) == len(spec["runtime_keys"]):
        status = "evidence-present"
    else:
        status = "partial"
        missing_keys = [
            key
            for key in spec["runtime_keys"]
            if not isinstance(runtime.get(key), dict) or not _evidence_present(runtime.get(key))
        ]
        blockers.extend(f"{key}_not_evidence_present" for key in missing_keys)
    return {
        "contract_id": spec["contract_id"],
        "label": spec["label"],
        "canonical_intent": spec["canonical_intent"],
        "runtime_keys": list(spec["runtime_keys"]),
        "status": status,
        "evidence_refs": _dedupe(spec["evidence_refs"] + [_evidence_ref(key, runtime.get(key)) for key in spec["runtime_keys"]]),
        "blockers": blockers,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _contract_specs() -> list[dict[str, Any]]:
    return [
        _spec("wrapper-product-surface", "Wrapper product surface", "The wrapper is the initial release product surface and boot entrypoint.", ["entrypoint", "session_history"], ["/ui/wrapper/", "/ops/wrapper/release-runtime"]),
        _spec("model-wrapping-provider-path", "Model wrapping provider path", "Local/API model wrapping must be visible through provider readiness and runtime decisions.", ["provider_readiness", "runtime_decision_ledger"], ["/ops/wrapper/release-runtime", "/ops/brain/canon/runtime-decision-ledger"]),
        _spec("continuous-assimilation-global-growth", "Continuous assimilation and growth", "End-user wrapper use routes learning into per-user and global expert growth state.", ["continuous_assimilation", "global_growth"], ["/ops/wrapper/release-runtime"]),
        _spec("federated-learning-packets", "Federated learning packets", "Real wrapper/model interactions emit sanitized federated packets and accept inbound shadow packets.", ["federated_packet_outbox", "federated_packet_inbox"], ["/ops/wrapper/federated-packets", "/ops/wrapper/federated-packets/imports"]),
        _spec("dream-research-improvement-loop", "Dream research improvement loop", "Wrapper use can generate dream/research items and proposal evidence.", ["dream_research_queue", "autonomous_updates"], ["/ops/wrapper/release-runtime", "/ops/brain/self-improvement"]),
        _spec("governed-self-repair-updates", "Governed self repair updates", "Autonomous updates must stay admin-approved, sandbox-tested, rollbackable, and mutation bounded.", ["autonomous_updates", "self_repair_ledger", "native_runtime_growth_governance"], ["/ops/wrapper/status-card", "/ops/wrapper/release-readiness"]),
        _spec("teacher-expert-birth-registry", "Teacher expert birth registry", "Teacher/expert registry and birth substrate must be visible to the release surface.", ["teacher_expert_birth_registry"], ["/ops/brain/canon/teacher-expert-birth-registry"]),
        _spec("developmental-growth-promotion", "Developmental growth promotion", "Developmental cortex, growth archive, growth engine, and promotion governance are whole-system release surfaces.", ["developmental_growth_promotion", "developmental_release_contract"], ["/ops/brain/canon/developmental-cortex", "/ops/wrapper/release-runtime"]),
        _spec("authority-eval-tool-governance", "Authority eval tool governance", "Authority, evidence, eval federation, tool action, and runtime decision receipts gate production mutation.", ["authority_evidence_tool_governance"], ["/ops/brain/canon/authority-spine", "/ops/brain/canon/evidence-store"]),
        _spec("ao-runtime-governance", "AO runtime governance", "Canonical and domain AO receipt coverage must be visible at runtime.", ["canonical_ao_coverage", "domain_ao_routing", "ao_execution_receipts"], ["/ops/wrapper/release-runtime"]),
        _spec("context-cache-truth", "Context and cache truth", "1M+ context claims are separated from measured host/cache capability.", ["effective_context_cache", "context_window_posture", "context_capability_envelope"], ["/ops/wrapper/release-runtime", "/ops/brain/cache-ledger"]),
        _spec("production-spine-release-lifecycle", "Production spine release lifecycle", "The production spine release lifecycle, rollup, first-run gate, and smoke history remain whole-system governed evidence.", ["production_spine_release_lifecycle", "release_manifest_status_rollup", "first_run_readiness", "release_run_history"], ["/ops/wrapper/release-product-smoke/run", "/ops/wrapper/production-spine-release-lifecycle/run"]),
        _spec("control-panel-visualizer-status", "Control panel visualizer status", "Control panel and visualizer must expose honest whole-project status labels and gaps.", ["live_wrapper_telemetry", "whole_system_forward_pass_enforcement_matrix"], ["/ui/control-panel/", "/ui/visualizer/"]),
    ]


def _spec(contract_id: str, label: str, canonical_intent: str, runtime_keys: list[str], evidence_refs: list[str]) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "label": label,
        "canonical_intent": canonical_intent,
        "runtime_keys": runtime_keys,
        "evidence_refs": evidence_refs,
    }


def _evidence_present(value: dict[str, Any]) -> bool:
    if value.get("raw_content_included") is True or value.get("active_production_mutation_allowed") is True:
        return False
    if (
        value.get("surface_id") == "native-runtime-growth-governance"
        and value.get("status") == "not-triggered"
        and value.get("native_hive_runtime_growth") is False
        and value.get("active_production_mutated") is False
        and value.get("raw_content_included") is False
    ):
        return True
    if (
        value.get("surface_id") == "release-wrapper-context-capability-envelope"
        and value.get("hardware_backed") is True
        and bool(value.get("latest_cache_entry_id"))
        and bool(value.get("latest_runtime_scorecard_id"))
        and str(value.get("latest_runtime_scorecard_status") or "") == "measured"
        and int(value.get("envelope_count") or 0) > 0
    ):
        return True
    positive_statuses = {
        "pass",
        "go",
        "ready",
        "ready-shadow",
        "live-bound",
        "live-evidence",
        "replayed",
        "replayed-evidence",
        "covered",
        "completed",
        "measured",
        "shadow-ready",
        "release-product-smoke-passed",
        "approved-shadow-release-lifecycle",
    }
    negative_statuses = {
        "blocked",
        "degraded",
        "missing",
        "no-go",
        "not-configured",
        "not-recorded",
        "not-run",
        "partial",
        "static-canon",
        "unknown",
    }
    for key in ("status", "latest_status", "runtime_state", "coverage_status", "decision", "go_no_go"):
        status = str(value.get(key) or "")
        if status in positive_statuses:
            return True
        if status in negative_statuses or status.startswith("not-"):
            return False
    for key in (
        "event_count",
        "entry_count",
        "run_count",
        "receipt_count",
        "proposal_count",
        "packet_count",
        "accepted_import_count",
        "decision_count",
        "users",
        "global_captures",
        "execution_count",
    ):
        if int(value.get(key) or 0) > 0:
            return True
    if value.get("surface_id") and not any(key in value for key in ("status", "latest_status", "runtime_state")):
        return True
    return bool(value)


def _evidence_ref(key: str, value: Any) -> str:
    if not isinstance(value, dict):
        return f"{key}::missing"
    for id_key in ("surface_id", "latest_status", "status", "runtime_state"):
        if value.get(id_key):
            return f"{key}::{value[id_key]}"
    return f"{key}::present"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            deduped.append(text)
            seen.add(text)
    return deduped
