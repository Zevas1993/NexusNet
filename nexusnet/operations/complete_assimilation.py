from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .corpus_runtime import CorpusAssimilationRuntime
from .ledger_runtime import AssimilationLedgerRuntime


_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONSOLIDATED_PATH = _REPO_ROOT / "docs" / "assimilation" / "NEXUSNET_ALL_ASSIMILATION_TARGETS_CONSOLIDATED_2026-05-31.md"
_REGISTER_ROW = re.compile(
    r"^\|\s*(?P<source_id>\d+)\s*\|\s*(?P<category>[^|]+?)\s*\|\s*`(?P<path>[^`]+)`\s*\|\s*(?P<title>[^|]+?)\s*\|\s*(?P<status>[^|]*?)\s*\|\s*(?P<urls>\d+)\s*\|\s*`(?P<sha>[0-9a-f]+)`\s*\|"
)


class CompleteAssimilationRuntime:
    """One evidence gate spanning the 195-source corpus, 144 specs, and 111-row ledger."""

    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.numbered = CorpusAssimilationRuntime(artifacts_dir=artifacts_dir)
        self.ledger = AssimilationLedgerRuntime()
        self.sources = self._load_sources(_CONSOLIDATED_PATH)

    def completeness_report(self) -> dict[str, Any]:
        numbered = self.numbered.completeness_report()
        ledger = self.ledger.completeness_report()
        missing_paths: list[str] = []
        unbound_source_ids: list[int] = []
        routed_sources: list[dict[str, Any]] = []
        for source in self.sources:
            payload = deepcopy(source)
            local_path = _REPO_ROOT / source["source_path"]
            if not local_path.is_file():
                missing_paths.append(source["source_path"])
            target_id = self._numbered_target_id(source)
            if target_id is not None:
                binding = numbered["bindings"].get(target_id)
                if binding is None:
                    unbound_source_ids.append(source["source_id"])
                payload.update(
                    {
                        "route": "numbered-runtime-target",
                        "target_id": target_id,
                        "runtime_binding": deepcopy(binding),
                    }
                )
            else:
                payload.update(
                    {
                        "route": "governance-or-evidence-source",
                        "target_id": None,
                        "runtime_binding": {
                            "state": "source-indexed",
                            "purpose": "Canon, ledger, source verification, decision, run log, or packet evidence",
                        },
                    }
                )
            routed_sources.append(payload)
        overall_complete = (
            len(routed_sources) == 195
            and not missing_paths
            and not unbound_source_ids
            and numbered["runtime_state"] == "complete-runtime-bindings"
            and ledger["runtime_state"] == "complete-ledger-runtime-evidence"
        )
        return {
            "surface_id": "complete-assimilation-runtime",
            "authority": "NexusBrain",
            "consolidated_source_count": len(routed_sources),
            "numbered_target_count": numbered["target_count"],
            "ledger_entry_count": ledger["entry_count"],
            "native_cluster_count": len(numbered["cluster_counts"]),
            "code_appropriate_numbered_target_count": numbered["code_appropriate_target_count"],
            "implemented_numbered_target_count": numbered["implemented_target_count"],
            "implemented_ledger_candidate_count": ledger["implemented_candidate_count"],
            "missing_source_paths": sorted(set(missing_paths)),
            "unbound_numbered_source_ids": sorted(unbound_source_ids),
            "unimplemented_numbered_target_ids": numbered["unimplemented_target_ids"],
            "unimplemented_ledger_entry_ids": ledger["unimplemented_candidate_entry_ids"],
            "canon_excluded_numbered_target_ids": numbered["canon_excluded_target_ids"],
            "overall_runtime_state": (
                "complete-assimilation-runtime-evidence"
                if overall_complete
                else "incomplete-assimilation-runtime-evidence"
            ),
            "numbered_runtime": numbered,
            "ledger_runtime": ledger,
            "sources": routed_sources,
        }

    @staticmethod
    def _load_sources(path: Path) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        in_register = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line == "## Normalized Source Register":
                in_register = True
                continue
            if in_register and line == "## Full Source Corpus":
                break
            if not in_register:
                continue
            match = _REGISTER_ROW.match(line)
            if match is None:
                continue
            item = match.groupdict()
            sources.append(
                {
                    "source_id": int(item["source_id"]),
                    "category": item["category"].strip(),
                    "source_path": item["path"].replace("\\", "/"),
                    "title": item["title"].strip(),
                    "snapshot_status": item["status"].strip() or None,
                    "url_count": int(item["urls"]),
                    "snapshot_sha256_prefix": item["sha"],
                }
            )
        expected_ids = list(range(1, len(sources) + 1))
        actual_ids = [item["source_id"] for item in sources]
        if actual_ids != expected_ids:
            raise ValueError("consolidated source register is not contiguous")
        return sources

    @staticmethod
    def _numbered_target_id(source: dict[str, Any]) -> str | None:
        if source["category"] not in {"online-spec", "video-spec"}:
            return None
        filename = source["source_path"].rsplit("/", 1)[-1]
        if not re.match(r"^\d+-.*\.md$", filename):
            return None
        return filename[:-3]
