from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[2]
_ONLINE_DIR = _REPO_ROOT / "docs" / "assimilation" / "online" / "2026-05-06"
_VIDEO_DIR = _REPO_ROOT / "docs" / "assimilation" / "videos" / "2026-05-06"

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_PRIORITY_RE = re.compile(r"\bP([0-9])\b")
_NUMBERED_RE = re.compile(r"^[0-9]+-.*\.md$")
_GOVERNED_ASSIMILATION_SURFACES = (
    "/ops/brain/canon/developmental-cortex",
    "/ops/brain/canon/authority-spine",
    "/ops/brain/canon/evidence-store",
    "/ops/brain/canon/tool-action-harness",
    "/ops/brain/canon/runtime-decision-ledger",
)


@lru_cache(maxsize=1)
def _complete_assimilation_compact() -> dict[str, Any]:
    from nexusnet.operations.complete_assimilation import CompleteAssimilationRuntime

    report = CompleteAssimilationRuntime().completeness_report()
    return {
        "consolidated_source_count": report["consolidated_source_count"],
        "numbered_target_count": report["numbered_target_count"],
        "ledger_entry_count": report["ledger_entry_count"],
        "native_cluster_count": report["native_cluster_count"],
        "implemented_numbered_target_count": report["implemented_numbered_target_count"],
        "implemented_ledger_candidate_count": report["implemented_ledger_candidate_count"],
        "unimplemented_target_ids": sorted(
            set(report["unimplemented_numbered_target_ids"] + report["unimplemented_ledger_entry_ids"])
        ),
        "canon_excluded_numbered_target_ids": report["canon_excluded_numbered_target_ids"],
        "overall_runtime_state": report["overall_runtime_state"],
    }


def _numbered_specs(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if _NUMBERED_RE.match(p.name))


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.strip().lower() == f"## {heading}".lower():
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def _bullets(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
    return items


def _first_paragraph(block: str) -> str:
    for chunk in block.split("\n\n"):
        cleaned = chunk.strip()
        if cleaned:
            return " ".join(cleaned.split())
    return ""


def _title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _status_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip().lower().startswith("status:"):
            return line.split(":", 1)[1].strip()
    return ""


def _implementation_contract(*, spec_path: str, spec_sha256: str) -> dict[str, Any]:
    """Bind every source-pinned target to the live, non-mutating Canon spine."""
    return {
        "authority": "NexusBrain",
        "execution_mode": "evidence-only",
        "production_mutation_allowed": False,
        "promotion_requires_target_evidence": True,
        "source_integrity_ref": spec_sha256,
        "target_spec_ref": spec_path,
        "governed_surfaces": list(_GOVERNED_ASSIMILATION_SURFACES),
        "rollback_or_sidebar_rule": (
            "Keep the target evidence-only and side-bar its candidate record when source, "
            "sandbox, policy, evaluation, artifact-trust, or rollback evidence fails."
        ),
    }


def _parse_spec(path: Path, source_kind: str) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    status = _status_line(text)
    priority_match = _PRIORITY_RE.search(status)
    priority = f"P{priority_match.group(1)}" if priority_match else "candidate"
    source_block = _section(text, "Source Evidence") or text
    spec_path = path.relative_to(_REPO_ROOT).as_posix()
    spec_sha256 = "sha256:" + hashlib.sha256(raw).hexdigest()
    return {
        "target_id": path.stem,
        "source_kind": source_kind,
        "title": _title(text),
        "priority": priority,
        "status_line": status,
        "lifecycle_state": "started-research-candidate",
        "production_promotion_allowed": False,
        "assimilation_target": _first_paragraph(_section(text, "NexusNet Assimilation Target")),
        "proposed_components": _bullets(_section(text, "Proposed NexusNet Components")),
        "promotion_gates": _bullets(_section(text, "Promotion Gates")) or _bullets(_section(text, "Common Promotion Gates")),
        "risks": _bullets(_section(text, "Risks")),
        "source_urls": _URL_RE.findall(source_block),
        "spec_path": spec_path,
        "spec_sha256": spec_sha256,
        "implementation_contract": _implementation_contract(spec_path=spec_path, spec_sha256=spec_sha256),
        "promotion_boundary": "research-only-until-source-license-privacy-security-eval-rollback-governance-gates-pass",
    }


@lru_cache(maxsize=1)
def _load_targets() -> tuple[dict[str, Any], ...]:
    targets: list[dict[str, Any]] = []
    for path in _numbered_specs(_ONLINE_DIR):
        targets.append(_parse_spec(path, "online"))
    for path in _numbered_specs(_VIDEO_DIR):
        targets.append(_parse_spec(path, "video"))
    return tuple(targets)


class AssimilationTargetCatalog:
    """Started register for every numbered assimilation-target spec.

    Each numbered online/video spec is parsed into a tracked research candidate. Starting a
    target means it is registered, parsed, source-pinned, and operator-visible at the gated
    lifecycle state. No target is promoted to production behavior here: every record stays
    research-only until the full source/license/privacy/security/eval/rollback/governance
    gates pass.
    """

    def __init__(self, *, runtime: Any | None = None) -> None:
        self._targets = [dict(target) for target in _load_targets()]
        self._by_id = {target["target_id"]: target for target in self._targets}
        if runtime is None:
            from nexusnet.operations.corpus_runtime import CorpusAssimilationRuntime

            runtime = CorpusAssimilationRuntime(targets=self._targets)
        self._runtime = runtime

    def get(self, target_id: str) -> dict[str, Any] | None:
        target = self._by_id.get(target_id)
        if target is None:
            return None
        payload = dict(target)
        payload["runtime_binding"] = self._runtime.binding_for(target_id)
        return payload

    def summary(self, *, limit: int | None = None) -> dict[str, Any]:
        targets = self._targets if limit is None else self._targets[:limit]
        completeness = self._runtime.completeness_report()
        complete_assimilation = _complete_assimilation_compact()
        priority_counts: dict[str, int] = {}
        for target in self._targets:
            priority_counts[target["priority"]] = priority_counts.get(target["priority"], 0) + 1
        online = sum(1 for target in self._targets if target["source_kind"] == "online")
        video = sum(1 for target in self._targets if target["source_kind"] == "video")
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "assimilation-target-catalog",
            "authority": "NexusBrain",
            "runtime_state": completeness["runtime_state"],
            "target_count": len(self._targets),
            "online_target_count": online,
            "video_target_count": video,
            "started_count": sum(1 for t in self._targets if t["lifecycle_state"] == "started-research-candidate"),
            "promoted_count": sum(1 for t in self._targets if t["production_promotion_allowed"]),
            "implemented_count": completeness["implemented_target_count"],
            "canon_excluded_count": len(completeness["canon_excluded_target_ids"]),
            "canon_excluded_target_ids": completeness["canon_excluded_target_ids"],
            "unimplemented_count": len(completeness["unimplemented_target_ids"]),
            "unimplemented_target_ids": completeness["unimplemented_target_ids"],
            "cluster_counts": completeness["cluster_counts"],
            "complete_assimilation": complete_assimilation,
            "priority_counts": priority_counts,
            "promotion_boundary": "all-targets-research-only-until-gates-pass-no-auto-promotion",
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/canon/assimilation-target-catalog"},
                "inspect_target": {"method": "GET", "endpoint_template": "/ops/brain/assimilation-target-catalog/{target_id}"},
            },
            "targets": [self.get(target["target_id"]) for target in targets],
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary(limit=12)
        summary["control_panel_label"] = "Assimilation Target Catalog"
        return summary
