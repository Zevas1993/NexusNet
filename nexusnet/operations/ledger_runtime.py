from __future__ import annotations

import importlib
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[2]
_LEDGER_PATH = _REPO_ROOT / "docs" / "NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md"
_CANDIDATE_STATUSES = {"candidate", "code_backed_candidate"}
_LIVE_STATUSES = {"live_control_plane", "live_substrate_implementation"}

_CANDIDATE_BINDINGS: dict[str, tuple[str, ...]] = {
    "PB-2026-05-01-015": ("nexusnet.agents.sandbox_factory:SandboxAgentFactory.start",),
    "PB-2026-05-04-093": ("nexusnet.teachers.registry:TeacherRegistry.resolve_for_task",),
    "PB-2026-04-30-001": ("nexusnet.browser.context_memory:BrowserContextMemory.query",),
    "PB-2026-04-30-002": ("nexusnet.agents.pipelines.service:AgenticPipelineRuntime.start",),
    "PB-2026-04-30-003": ("nexusnet.policy.kernel:PolicyKernel.scan",),
    "PB-2026-04-30-004": (
        "nexusnet.recipes.service:RecipeCatalogService.list_items",
        "nexusnet.operations.spine:OperationalSpineService.register_worktree",
    ),
    "PB-2026-04-30-005": ("nexusnet.agents.harnesses.registry:HarnessProviderRegistry.recommend",),
    "PB-2026-04-30-006": ("nexusnet.runtime.edge_router.service:EdgeWorkloadRouter.route",),
    "PB-2026-04-30-007": (
        "nexusnet.adapters.forge:AdapterForgeRegistry.register",
        "nexusnet.adapters.dataset_forge:DatasetForge.build",
        "nexusnet.adapters.decision_gate:FineTuneDecisionGate.decide",
    ),
    "PB-2026-05-05-080": ("nexusnet.knowledge.compiler:KnowledgeArtifactCompiler.compile",),
    "PB-2026-06-03-094": ("nexusnet.agents.harnesses.contract:HarnessContractLedger.preflight",),
    "PB-2026-06-03-095": ("nexusnet.knowledge.memory_model:MemoryModelLane.query",),
    "PB-2026-06-03-096": ("nexusnet.adapters.passport:AdapterRegistry.shadow_attach",),
    "PB-2026-06-03-097": ("nexusnet.agents.harnesses.secure_runtime:SecureRuntimeContract.evaluate",),
    "PB-2026-06-03-099": ("nexusnet.runtime.model_attach_harness:ModelAttachInferenceHarness.open_route",),
    "PB-2026-06-03-100": ("nexusnet.runtime.hardware_fit:ModelFitRecommender.recommend",),
}


class AssimilationLedgerRuntime:
    """Runtime evidence overlay for the append-only post-book assimilation ledger."""

    def __init__(self, *, ledger_path: Path | str = _LEDGER_PATH) -> None:
        self.ledger_path = Path(ledger_path)
        self._entries = self._parse_entries(self.ledger_path.read_text(encoding="utf-8"))

    def completeness_report(self) -> dict[str, Any]:
        entries: dict[str, dict[str, Any]] = {}
        missing_paths: set[str] = set()
        live_without_code: list[str] = []
        unimplemented_candidates: list[str] = []
        implemented_candidates = 0
        for entry in self._entries:
            payload = deepcopy(entry)
            status = entry["ledger_status"]
            if status in _CANDIDATE_STATUSES:
                refs = _CANDIDATE_BINDINGS.get(entry["entry_id"], ())
                probe = self._probe(refs)
                binding = {
                    "state": "runtime-implemented" if refs and probe["passed"] else "unimplemented",
                    "implementation_refs": list(refs),
                    "probe": probe,
                }
                if binding["state"] == "runtime-implemented":
                    implemented_candidates += 1
                else:
                    unimplemented_candidates.append(entry["entry_id"])
                payload["runtime_binding"] = binding
            elif status in _LIVE_STATUSES:
                code_paths = entry["evidence_code_paths"]
                missing = [path for path in code_paths if not (_REPO_ROOT / path).is_file()]
                missing_paths.update(missing)
                if not code_paths:
                    live_without_code.append(entry["entry_id"])
                payload["runtime_binding"] = {
                    "state": "ledger-live-code-evidence" if code_paths and not missing else "live-evidence-missing",
                    "implementation_paths": code_paths,
                    "missing_paths": missing,
                }
            elif status == "research_only":
                payload["runtime_binding"] = {"state": "canon-research-only"}
            else:
                payload["runtime_binding"] = {"state": "canon-clarification"}
            entries[entry["entry_id"]] = payload

        status_counts = {
            status: sum(1 for item in self._entries if item["ledger_status"] == status)
            for status in sorted({item["ledger_status"] for item in self._entries})
        }
        code_appropriate = sum(1 for item in self._entries if item["ledger_status"] in _CANDIDATE_STATUSES | _LIVE_STATUSES)
        runtime_state = (
            "complete-ledger-runtime-evidence"
            if not unimplemented_candidates and not live_without_code and not missing_paths
            else "incomplete-ledger-runtime-evidence"
        )
        return {
            "surface_id": "assimilation-ledger-runtime",
            "ledger_path": self.ledger_path.relative_to(_REPO_ROOT).as_posix(),
            "entry_count": len(self._entries),
            "status_counts": status_counts,
            "code_appropriate_entry_count": code_appropriate,
            "implemented_candidate_count": implemented_candidates,
            "unimplemented_candidate_entry_ids": sorted(unimplemented_candidates),
            "live_entry_missing_code_refs": sorted(live_without_code),
            "missing_evidence_paths": sorted(missing_paths),
            "runtime_state": runtime_state,
            "entries": entries,
        }

    @staticmethod
    def _parse_entries(text: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for line in text.splitlines():
            if not line.startswith("| PB-"):
                continue
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            if len(columns) != 7:
                raise ValueError(f"invalid assimilation ledger row: {line[:120]}")
            entry_id, date, status, addition, original_status, evidence_refs, current_gate = columns
            code_paths = sorted(set(re.findall(r"`([^`]+\.py)`", evidence_refs)))
            entries.append(
                {
                    "entry_id": entry_id,
                    "date": date,
                    "ledger_status": status,
                    "addition": addition,
                    "original_book_status": original_status,
                    "evidence_refs": evidence_refs,
                    "evidence_code_paths": code_paths,
                    "current_gate": current_gate,
                }
            )
        return entries

    @staticmethod
    def _probe(refs: tuple[str, ...]) -> dict[str, Any]:
        resolved: list[str] = []
        errors: list[str] = []
        for ref in refs:
            try:
                module_name, symbol_path = ref.split(":", 1)
                value: Any = importlib.import_module(module_name)
                for part in symbol_path.split("."):
                    value = getattr(value, part)
                if not callable(value):
                    raise TypeError("resolved object is not callable")
                resolved.append(ref)
            except (ImportError, AttributeError, TypeError, ValueError) as exc:
                errors.append(f"{ref}: {type(exc).__name__}: {exc}")
        return {"passed": bool(refs) and len(resolved) == len(refs) and not errors, "resolved_refs": resolved, "errors": errors}
