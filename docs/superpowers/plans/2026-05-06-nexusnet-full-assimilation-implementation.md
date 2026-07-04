# NexusNet Full Assimilation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full 2026-05-06 assimilation packet as a governed developmental cortex with attached runtime, memory, authority, tool, eval, evidence, and Control Panel lanes.

**Architecture:** Build one non-mutating `nexusnet.developmental` spine first, then connect existing NexusNet registries through stable evidence contracts. Every candidate from the assimilation docs remains refs-only until it has code-backed consumers, tests, policy gates, artifact trust, and operator-visible scorecards.

**Tech Stack:** Python 3, Pydantic, pytest, existing NexusNet registries, existing Control Panel JavaScript, existing artifact stores under `runtime/artifacts`.

---

## Source Inputs

- `docs/assimilation/online/2026-05-06/README.md`
- `docs/assimilation/online/2026-05-06/FINAL_MISSING_PIECE_SYNTHESIS.md`
- `docs/assimilation/videos/2026-05-06/README.md`
- `docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md`
- Existing implementation surfaces:
  - `nexusnet/growth/engine.py`
  - `nexusnet/growth/production_spine.py`
  - `nexusnet/dreaming/engine.py`
  - `nexusnet/core/self_review.py`
  - `nexusnet/knowledge/compiler.py`
  - `nexusnet/memory/quality_ledger.py`
  - `nexusnet/memory/engram_index.py`
  - `nexusnet/policy/kernel.py`
  - `nexusnet/security/artifact_trust.py`
  - `nexusnet/protocols/trust.py`
  - `nexusnet/evals/registry.py`
  - `nexusnet/evals/verifier_search.py`
  - `nexusnet/runtime/inference_economy_router.py`
  - `nexusnet/runtime/cache_ledger.py`
  - `nexusnet/vision/computer_use.py`
  - `nexusnet/visuals/layout.py`
  - `ui/control-panel/app.js`

## Implementation Rules

- No production self-mutation in this plan.
- No consciousness, sentience, whole-brain-emulation, or uploading claims.
- No video transcript or workstation path commits.
- Every new lane emits evidence records, not active behavior changes.
- Every promotion path requires policy, eval, provenance, artifact trust, rollback, and operator approval.
- Every code edit that touches existing symbols must follow `AGENTS.md`: run GitNexus impact analysis first and report blast radius.

## File Structure

Create these new packages:

- `nexusnet/developmental/__init__.py`: public exports for the developmental cortex package.
- `nexusnet/developmental/contracts.py`: Pydantic contracts shared by all developmental lanes.
- `nexusnet/developmental/body_schema.py`: live self-model over registries, policy, runtime, memory, tools, evals, and degraded states.
- `nexusnet/developmental/reference_frames.py`: local reference-frame store for project, task, artifact, tool, model, user-goal, memory, runtime, and policy frames.
- `nexusnet/developmental/simulator.py`: deterministic dreaming/simulation request builder and result recorder.
- `nexusnet/developmental/causal_lab.py`: sandboxed intervention records and causal confidence ledger.
- `nexusnet/developmental/growth_archive.py`: diversity-preserving archive for improvement candidates.
- `nexusnet/developmental/promotion_tribunal.py`: promotion decision aggregator over policy, eval, artifact trust, self-review, memory quality, rollback, and operator approval.
- `nexusnet/developmental/kernel.py`: orchestration layer that binds the previous modules.

Create these support packages:

- `nexusnet/authority/contracts.py`: effect, capability, observed-effect, rollback, and authority-decision contracts.
- `nexusnet/authority/spine.py`: local authority-integrity spine over policy and artifact trust.
- `nexusnet/evidence/contracts.py`: content-addressed evidence and assurance-case contracts.
- `nexusnet/evidence/store.py`: append-only local evidence store with hash chaining and projection helpers.
- `nexusnet/evals/federation.py`: normalized eval event schema for local and external benchmark adapters.
- `nexusnet/tools/action_harness.py`: policy-gated tool/browser/desktop action harness that starts read-only.
- `nexusnet/runtime/decision_ledger.py`: aggregated runtime decision ledger over route, cache, quantization, cost, model passport, eval, and fallback evidence.

Create tests:

- `tests/test_developmental_body_schema.py`
- `tests/test_reference_frame_store.py`
- `tests/test_developmental_simulation_and_causal_lab.py`
- `tests/test_growth_archive_and_promotion_tribunal.py`
- `tests/test_developmental_cortex_kernel.py`
- `tests/test_authority_integrity_spine.py`
- `tests/test_evidence_store.py`
- `tests/test_eval_federation.py`
- `tests/test_tool_action_harness.py`
- `tests/test_runtime_decision_ledger.py`
- Extend `tests/test_nexusnet_visualizer.py`

Modify integration surfaces:

- `nexusnet/visuals/layout.py`
- `ui/control-panel/app.js`
- `nexusnet/developmental/__init__.py`
- `nexusnet/runtime/__init__.py`
- `nexusnet/evals/__init__.py`

## Wave 0: Source Ledger And Boundaries

### Task 1: Assimilation Source Ledger

**Files:**
- Create: `nexusnet/developmental/contracts.py`
- Create: `tests/test_developmental_body_schema.py`

- [ ] **Step 1: Write the source-ledger test**

```python
from nexusnet.developmental.contracts import AssimilationSourceLedger


def test_assimilation_source_ledger_counts_full_chat_packet():
    ledger = AssimilationSourceLedger.full_2026_05_06_packet()

    assert ledger.online_spec_count == 134
    assert ledger.video_spec_count == 10
    assert ledger.total_spec_count == 144
    assert ledger.status == "refs_only_until_code_backed"
    assert "consciousness_upload_claims_blocked" in ledger.boundaries
    assert "production_self_mutation_blocked" in ledger.boundaries
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `pytest tests/test_developmental_body_schema.py::test_assimilation_source_ledger_counts_full_chat_packet -q`

Expected: `ImportError` for `nexusnet.developmental` or missing `AssimilationSourceLedger`.

- [ ] **Step 3: Add the ledger contract**

Add this to `nexusnet/developmental/contracts.py`:

```python
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssimilationSourceLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    packet_id: str
    online_spec_count: int
    video_spec_count: int
    total_spec_count: int
    status: Literal["refs_only_until_code_backed"] = "refs_only_until_code_backed"
    source_docs: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)

    @classmethod
    def full_2026_05_06_packet(cls) -> "AssimilationSourceLedger":
        return cls(
            packet_id="assimilation-2026-05-06-full-chat",
            online_spec_count=134,
            video_spec_count=10,
            total_spec_count=144,
            source_docs=[
                "docs/assimilation/online/2026-05-06/README.md",
                "docs/assimilation/online/2026-05-06/FINAL_MISSING_PIECE_SYNTHESIS.md",
                "docs/assimilation/videos/2026-05-06/README.md",
                "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
            ],
            boundaries=[
                "refs_only_until_code_backed",
                "production_self_mutation_blocked",
                "consciousness_upload_claims_blocked",
                "operator_approval_required_for_active_promotion",
                "artifact_trust_required_for_promoted_artifacts",
            ],
        )
```

- [ ] **Step 4: Create package export**

Create `nexusnet/developmental/__init__.py`:

```python
from .contracts import AssimilationSourceLedger

__all__ = ["AssimilationSourceLedger"]
```

- [ ] **Step 5: Run the test and verify it passes**

Run: `pytest tests/test_developmental_body_schema.py::test_assimilation_source_ledger_counts_full_chat_packet -q`

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add nexusnet/developmental tests/test_developmental_body_schema.py
git commit -m "feat: add assimilation source ledger"
```

## Wave 1: Developmental Cortex Spine

### Task 2: Nexus Body Schema

**Files:**
- Modify: `nexusnet/developmental/contracts.py`
- Create: `nexusnet/developmental/body_schema.py`
- Modify: `tests/test_developmental_body_schema.py`

- [ ] **Step 1: Run GitNexus impact before touching existing registry consumers**

Run: `gitnexus_impact` for each existing symbol the worker decides to call directly, starting with `PolicyKernel`, `ProtocolTrustRegistry`, `ArtifactTrustRegistry`, `EvalRegistry`, `VerifierSearchRegistry`, `InferenceEconomyRouter`, `EffectiveContextCacheLedger`, `KnowledgeArtifactCompiler`, `MemoryQualityLedger`, and `MultimodalComputerUseController`.

Expected: LOW or MEDIUM risk before proceeding. If HIGH or CRITICAL appears, stop and report the blast radius.

- [ ] **Step 2: Write the body-schema test**

Append to `tests/test_developmental_body_schema.py`:

```python
from nexusnet.developmental.body_schema import NexusBodySchemaBuilder


def test_body_schema_snapshot_marks_degraded_and_blocked_surfaces():
    builder = NexusBodySchemaBuilder()

    snapshot = builder.snapshot(
        runtime_state={"runtime_state": "live-bound", "provider_count": 3},
        memory_state={"runtime_state": "degraded", "blocked_count": 1},
        authority_state={"runtime_state": "degraded", "blocked_count": 2},
        eval_state={"runtime_state": "static-canon", "suite_count": 0},
    )

    assert snapshot["surface_id"] == "nexus-body-schema"
    assert snapshot["authority"] == "NexusBrain"
    assert snapshot["runtime_state"] == "degraded"
    assert snapshot["capability_counts"]["runtime"] == 3
    assert "memory" in snapshot["degraded_surfaces"]
    assert "authority" in snapshot["degraded_surfaces"]
    assert snapshot["production_mutation_allowed"] is False
```

- [ ] **Step 3: Run the test and verify it fails**

Run: `pytest tests/test_developmental_body_schema.py::test_body_schema_snapshot_marks_degraded_and_blocked_surfaces -q`

Expected: failure because `NexusBodySchemaBuilder` does not exist.

- [ ] **Step 4: Add body schema contracts**

Append to `nexusnet/developmental/contracts.py`:

```python
class NexusBodySchemaSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    surface_id: str = "nexus-body-schema"
    authority: str = "NexusBrain"
    runtime_state: Literal["static-canon", "live-bound", "degraded"] = "static-canon"
    capability_counts: dict[str, int] = Field(default_factory=dict)
    degraded_surfaces: list[str] = Field(default_factory=list)
    blocked_surfaces: list[str] = Field(default_factory=list)
    production_mutation_allowed: bool = False
    source_ledger: AssimilationSourceLedger = Field(default_factory=AssimilationSourceLedger.full_2026_05_06_packet)
```

- [ ] **Step 5: Implement the body schema builder**

Create `nexusnet/developmental/body_schema.py`:

```python
from __future__ import annotations

from typing import Any

from .contracts import NexusBodySchemaSnapshot


class NexusBodySchemaBuilder:
    def snapshot(
        self,
        *,
        runtime_state: dict[str, Any] | None = None,
        memory_state: dict[str, Any] | None = None,
        authority_state: dict[str, Any] | None = None,
        eval_state: dict[str, Any] | None = None,
        tool_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        states = {
            "runtime": runtime_state or {},
            "memory": memory_state or {},
            "authority": authority_state or {},
            "eval": eval_state or {},
            "tool": tool_state or {},
        }
        degraded = [
            name
            for name, state in states.items()
            if state.get("runtime_state") == "degraded" or int(state.get("blocked_count") or 0) > 0
        ]
        blocked = [
            name
            for name, state in states.items()
            if int(state.get("blocked_count") or 0) > 0 or str(state.get("status") or "").startswith("blocked")
        ]
        counts = {
            "runtime": int((runtime_state or {}).get("provider_count") or (runtime_state or {}).get("route_count") or 0),
            "memory": int((memory_state or {}).get("claim_count") or (memory_state or {}).get("record_count") or 0),
            "authority": int((authority_state or {}).get("grant_count") or (authority_state or {}).get("adapter_count") or 0),
            "eval": int((eval_state or {}).get("suite_count") or (eval_state or {}).get("search_count") or 0),
            "tool": int((tool_state or {}).get("plan_count") or 0),
        }
        runtime_label = "degraded" if degraded or blocked else (
            "live-bound" if any(counts.values()) else "static-canon"
        )
        return NexusBodySchemaSnapshot(
            runtime_state=runtime_label,
            capability_counts=counts,
            degraded_surfaces=sorted(set(degraded)),
            blocked_surfaces=sorted(set(blocked)),
        ).model_dump(mode="json")
```

- [ ] **Step 6: Export the builder**

Update `nexusnet/developmental/__init__.py`:

```python
from .body_schema import NexusBodySchemaBuilder
from .contracts import AssimilationSourceLedger, NexusBodySchemaSnapshot

__all__ = ["AssimilationSourceLedger", "NexusBodySchemaBuilder", "NexusBodySchemaSnapshot"]
```

- [ ] **Step 7: Run the body-schema tests**

Run: `pytest tests/test_developmental_body_schema.py -q`

Expected: all tests in the file pass.

- [ ] **Step 8: Commit**

```bash
git add nexusnet/developmental tests/test_developmental_body_schema.py
git commit -m "feat: add Nexus body schema"
```

### Task 3: Reference Frame Store

**Files:**
- Modify: `nexusnet/developmental/contracts.py`
- Create: `nexusnet/developmental/reference_frames.py`
- Create: `tests/test_reference_frame_store.py`

- [ ] **Step 1: Write the reference-frame tests**

Create `tests/test_reference_frame_store.py`:

```python
from nexusnet.developmental.reference_frames import ReferenceFrameStore


def test_reference_frame_store_records_local_models(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="frame:project:nexusnet",
        frame_type="project",
        subject_ref="repo:NexusNet",
        facts=[{"claim": "Developmental cortex is refs-only until code-backed.", "source_ref": "docs/assimilation"}],
        evidence_refs=["docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md"],
        uncertainty=0.2,
    )

    assert frame["frame_id"] == "frame:project:nexusnet"
    assert frame["runtime_state"] == "live-bound"
    assert frame["mutation_allowed"] is False
    assert frame["artifact_path"]


def test_reference_frame_store_rejects_mutation_claims(tmp_path):
    store = ReferenceFrameStore(artifacts_dir=tmp_path)

    frame = store.record(
        frame_id="frame:unsafe",
        frame_type="tool",
        subject_ref="tool:browser",
        facts=[{"claim": "Browser tool may mutate production without review.", "source_ref": "bad"}],
        evidence_refs=[],
        uncertainty=0.7,
    )

    assert frame["runtime_state"] == "degraded"
    assert "reference_frame_requires_evidence_refs" in frame["findings"]
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_reference_frame_store.py -q`

Expected: import failure for `ReferenceFrameStore`.

- [ ] **Step 3: Add reference-frame contract**

Append to `nexusnet/developmental/contracts.py`:

```python
FrameType = Literal["project", "task", "artifact", "tool", "model", "user_goal", "memory", "runtime", "policy"]


class ReferenceFrameRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_id: str
    frame_type: FrameType
    subject_ref: str
    facts: list[dict[str, str]] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    uncertainty: float = 0.0
    findings: list[str] = Field(default_factory=list)
    runtime_state: Literal["live-bound", "degraded"] = "live-bound"
    mutation_allowed: bool = False
    artifact_path: str | None = None
```

- [ ] **Step 4: Implement the store**

Create `nexusnet/developmental/reference_frames.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import ReferenceFrameRecord


class ReferenceFrameStore:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.frames_dir = self.artifacts_dir / "developmental" / "reference-frames" if self.artifacts_dir else None
        if self.frames_dir is not None:
            self.frames_dir.mkdir(parents=True, exist_ok=True)
        self._frames: list[dict[str, Any]] = []

    def record(
        self,
        *,
        frame_id: str,
        frame_type: str,
        subject_ref: str,
        facts: list[dict[str, str]],
        evidence_refs: list[str],
        uncertainty: float = 0.0,
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("reference_frame_requires_evidence_refs")
        if any("mutate production without review" in str(fact.get("claim", "")).lower() for fact in facts):
            findings.append("reference_frame_blocks_unreviewed_mutation_claim")
        record = ReferenceFrameRecord(
            frame_id=frame_id,
            frame_type=frame_type,
            subject_ref=subject_ref,
            facts=facts,
            evidence_refs=evidence_refs,
            uncertainty=uncertainty,
            findings=findings,
            runtime_state="degraded" if findings else "live-bound",
            mutation_allowed=False,
        ).model_dump(mode="json")
        record["created_at"] = utcnow().isoformat()
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        frames = self._list_frames(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "reference-frame-store",
            "runtime_state": "degraded" if any(frame.get("findings") for frame in frames) else ("live-bound" if frames else "static-canon"),
            "frame_count": len(frames),
            "latest_frame": frames[0] if frames else None,
            "frames": frames,
            "mutation_boundary": "reference-frames-model-context-without-production-mutation",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._frames.insert(0, record)
        if self.frames_dir is None:
            return
        safe = record["frame_id"].replace(":", "_").replace("/", "_")
        path = self.frames_dir / f"{safe}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    def _list_frames(self, *, limit: int) -> list[dict[str, Any]]:
        frames = list(self._frames)
        if self.frames_dir is not None:
            seen = {frame.get("frame_id") for frame in frames}
            for path in self.frames_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("frame_id") not in seen:
                    frames.append(payload)
        frames.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return frames[:limit]
```

- [ ] **Step 5: Export the store**

Update `nexusnet/developmental/__init__.py` so it exports `ReferenceFrameStore`.

- [ ] **Step 6: Run the tests**

Run: `pytest tests/test_reference_frame_store.py -q`

Expected: `2 passed`.

- [ ] **Step 7: Commit**

```bash
git add nexusnet/developmental tests/test_reference_frame_store.py
git commit -m "feat: add developmental reference frames"
```

### Task 4: Deterministic Simulation And Causal Lab

**Files:**
- Modify: `nexusnet/developmental/contracts.py`
- Create: `nexusnet/developmental/simulator.py`
- Create: `nexusnet/developmental/causal_lab.py`
- Create: `tests/test_developmental_simulation_and_causal_lab.py`

- [ ] **Step 1: Write simulation and causal tests**

Create `tests/test_developmental_simulation_and_causal_lab.py`:

```python
from nexusnet.developmental.causal_lab import CausalInterventionLab
from nexusnet.developmental.simulator import DreamingSimulator


def test_dreaming_simulator_records_deterministic_shadow_request(tmp_path):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)

    result = simulator.record_simulation(
        simulation_id="sim:route-cache-off",
        seed_trace_ref="trace:abc",
        scenario={"route": "reasoning", "cache": "off"},
        expected_outcomes=["lower_cache_hit_rate", "higher_latency"],
        evidence_refs=["trace:abc", "cache-ledger:baseline"],
    )

    assert result["status"] == "shadow-recorded"
    assert result["learned_world_model_claim"] is False
    assert result["production_action_allowed"] is False


def test_causal_lab_blocks_interventions_without_evidence(tmp_path):
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    result = lab.record_intervention(
        intervention_id="causal:missing-evidence",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": 0.12},
        evidence_refs=[],
    )

    assert result["status"] == "blocked"
    assert result["causal_confidence"] == "unknown"
    assert "causal_intervention_requires_evidence_refs" in result["findings"]
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_developmental_simulation_and_causal_lab.py -q`

Expected: import failures for `DreamingSimulator` and `CausalInterventionLab`.

- [ ] **Step 3: Add contracts**

Append to `nexusnet/developmental/contracts.py`:

```python
class SimulationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    simulation_id: str
    seed_trace_ref: str
    scenario: dict[str, object] = Field(default_factory=dict)
    expected_outcomes: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    status: Literal["shadow-recorded", "blocked"] = "shadow-recorded"
    learned_world_model_claim: bool = False
    production_action_allowed: bool = False
    findings: list[str] = Field(default_factory=list)
    artifact_path: str | None = None


class CausalInterventionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intervention_id: str
    variable: str
    control_value: str
    treatment_value: str
    observed_delta: dict[str, float] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    status: Literal["recorded", "blocked"] = "recorded"
    causal_confidence: Literal["confirmed", "refuted", "unknown"] = "unknown"
    findings: list[str] = Field(default_factory=list)
    production_action_allowed: bool = False
    artifact_path: str | None = None
```

- [ ] **Step 4: Implement shared JSON persistence helper inside both modules**

Use this pattern in both `simulator.py` and `causal_lab.py`:

```python
def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")[:160] or "record"
```

- [ ] **Step 5: Implement `DreamingSimulator`**

Create `nexusnet/developmental/simulator.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import SimulationRecord


class DreamingSimulator:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "simulations" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record_simulation(
        self,
        *,
        simulation_id: str,
        seed_trace_ref: str,
        scenario: dict[str, object],
        expected_outcomes: list[str],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = [] if evidence_refs else ["simulation_requires_evidence_refs"]
        record = SimulationRecord(
            simulation_id=simulation_id,
            seed_trace_ref=seed_trace_ref,
            scenario=scenario,
            expected_outcomes=expected_outcomes,
            evidence_refs=evidence_refs,
            status="blocked" if findings else "shadow-recorded",
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "dreaming-simulator",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("status") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "simulation_count": len(self._records),
            "latest_simulation": self._records[0] if self._records else None,
            "world_model_boundary": "deterministic-shadow-simulation-no-learned-world-model-claim",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{_safe_id(record['simulation_id'])}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")[:160] or "simulation"
```

- [ ] **Step 6: Implement `CausalInterventionLab`**

Create `nexusnet/developmental/causal_lab.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import CausalInterventionRecord


class CausalInterventionLab:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "causal-lab" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record_intervention(
        self,
        *,
        intervention_id: str,
        variable: str,
        control_value: str,
        treatment_value: str,
        observed_delta: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = [] if evidence_refs else ["causal_intervention_requires_evidence_refs"]
        confidence = "confirmed" if evidence_refs and any(abs(value) >= 0.05 for value in observed_delta.values()) else "unknown"
        record = CausalInterventionRecord(
            intervention_id=intervention_id,
            variable=variable,
            control_value=control_value,
            treatment_value=treatment_value,
            observed_delta=observed_delta,
            evidence_refs=evidence_refs,
            status="blocked" if findings else "recorded",
            causal_confidence=confidence,
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "causal-intervention-lab",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("status") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "intervention_count": len(self._records),
            "latest_intervention": self._records[0] if self._records else None,
            "boundary": "sandboxed-intervention-records-only-no-production-action",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{_safe_id(record['intervention_id'])}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")[:160] or "intervention"
```

- [ ] **Step 7: Export simulator and causal lab**

Update `nexusnet/developmental/__init__.py` so it exports `DreamingSimulator` and `CausalInterventionLab`.

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_developmental_simulation_and_causal_lab.py -q`

Expected: `2 passed`.

- [ ] **Step 9: Commit**

```bash
git add nexusnet/developmental tests/test_developmental_simulation_and_causal_lab.py
git commit -m "feat: add developmental simulation and causal lab"
```

### Task 5: Growth Archive And Promotion Tribunal

**Files:**
- Modify: `nexusnet/developmental/contracts.py`
- Create: `nexusnet/developmental/growth_archive.py`
- Create: `nexusnet/developmental/promotion_tribunal.py`
- Create: `tests/test_growth_archive_and_promotion_tribunal.py`

- [ ] **Step 1: Write archive and tribunal tests**

Create `tests/test_growth_archive_and_promotion_tribunal.py`:

```python
from nexusnet.developmental.growth_archive import GrowthArchive
from nexusnet.developmental.promotion_tribunal import PromotionTribunal


def test_growth_archive_preserves_diverse_shadow_candidates(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)

    first = archive.record_candidate(
        candidate_id="growth:route-cache",
        candidate_type="runtime",
        diversity_key="runtime-cache",
        scores={"quality": 0.78, "safety": 0.95},
        evidence_refs=["eval:shadow-route"],
    )
    second = archive.record_candidate(
        candidate_id="growth:memory-frame",
        candidate_type="memory",
        diversity_key="reference-frame",
        scores={"quality": 0.74, "safety": 0.98},
        evidence_refs=["memory:quality"],
    )

    summary = archive.summary()
    assert first["promotion_state"] == "archived-shadow"
    assert second["promotion_state"] == "archived-shadow"
    assert summary["diversity_key_count"] == 2
    assert summary["production_mutation_allowed"] is False


def test_promotion_tribunal_requires_all_gates_for_active_request():
    tribunal = PromotionTribunal()

    decision = tribunal.decide(
        case_id="case:growth:route-cache",
        candidate_ref="growth:route-cache",
        requested_state="active",
        policy_scan={"summary": {"active_hard_fail_count": 0}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": False, "promotion_blockers": ["signature_missing"]},
        self_review={"status": "accepted-shadow"},
        memory_quality={"status": "verified"},
        rollback={"rollback_restorable": True},
        operator_approved=True,
    )

    assert decision["decision"] == "rejected"
    assert "artifact_trust_not_clear" in decision["blockers"]
    assert decision["active_promotion_allowed"] is False
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_growth_archive_and_promotion_tribunal.py -q`

Expected: import failures.

- [ ] **Step 3: Add contracts**

Append to `nexusnet/developmental/contracts.py`:

```python
CandidateKind = Literal["runtime", "memory", "policy", "tool", "prompt", "adapter", "model", "research"]


class GrowthArchiveCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    candidate_type: CandidateKind
    diversity_key: str
    scores: dict[str, float] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    promotion_state: Literal["archived-shadow", "blocked"] = "archived-shadow"
    production_mutation_allowed: bool = False
    findings: list[str] = Field(default_factory=list)
    artifact_path: str | None = None


class PromotionTribunalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    candidate_ref: str
    requested_state: Literal["archived", "shadow", "canary", "active"]
    decision: Literal["accepted-shadow", "accepted-canary-request", "accepted-active-request", "rejected"]
    blockers: list[str] = Field(default_factory=list)
    active_promotion_allowed: bool = False
    production_mutation_allowed: bool = False
```

- [ ] **Step 4: Implement `GrowthArchive`**

Create `nexusnet/developmental/growth_archive.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import GrowthArchiveCandidate


class GrowthArchive:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "growth-archive" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record_candidate(
        self,
        *,
        candidate_id: str,
        candidate_type: str,
        diversity_key: str,
        scores: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = [] if evidence_refs else ["growth_candidate_requires_evidence_refs"]
        record = GrowthArchiveCandidate(
            candidate_id=candidate_id,
            candidate_type=candidate_type,
            diversity_key=diversity_key,
            scores=scores,
            evidence_refs=evidence_refs,
            promotion_state="blocked" if findings else "archived-shadow",
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "growth-archive",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("promotion_state") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "candidate_count": len(self._records),
            "diversity_key_count": len({item.get("diversity_key") for item in self._records}),
            "latest_candidate": self._records[0] if self._records else None,
            "production_mutation_allowed": False,
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['candidate_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 5: Implement `PromotionTribunal`**

Create `nexusnet/developmental/promotion_tribunal.py`:

```python
from __future__ import annotations

from typing import Any

from .contracts import PromotionTribunalDecision


class PromotionTribunal:
    def decide(
        self,
        *,
        case_id: str,
        candidate_ref: str,
        requested_state: str,
        policy_scan: dict[str, Any],
        eval_gate: dict[str, Any],
        artifact_trust: dict[str, Any],
        self_review: dict[str, Any],
        memory_quality: dict[str, Any],
        rollback: dict[str, Any],
        operator_approved: bool,
    ) -> dict[str, Any]:
        blockers = []
        if _policy_hard_fail_count(policy_scan) > 0:
            blockers.append("policy_scan_not_clear")
        if eval_gate.get("promotion_allowed") is not True:
            blockers.append("eval_gate_not_clear")
        if artifact_trust.get("promotion_allowed") is not True:
            blockers.append("artifact_trust_not_clear")
        if self_review.get("status") not in {"accepted-shadow", "passed", "review-passed"}:
            blockers.append("self_review_not_clear")
        if memory_quality.get("status") not in {"verified", "claim-grounded", "not_required"}:
            blockers.append("memory_quality_not_clear")
        if rollback.get("rollback_restorable") is not True:
            blockers.append("rollback_not_restorable")
        if not operator_approved and requested_state in {"canary", "active"}:
            blockers.append("operator_approval_required")
        active_allowed = requested_state == "active" and not blockers and operator_approved
        decision = "rejected"
        if not blockers and requested_state == "shadow":
            decision = "accepted-shadow"
        elif not blockers and requested_state == "canary":
            decision = "accepted-canary-request"
        elif active_allowed:
            decision = "accepted-active-request"
        return PromotionTribunalDecision(
            case_id=case_id,
            candidate_ref=candidate_ref,
            requested_state=requested_state,
            decision=decision,
            blockers=sorted(set(blockers)),
            active_promotion_allowed=active_allowed,
        ).model_dump(mode="json")


def _policy_hard_fail_count(policy_scan: dict[str, Any]) -> int:
    summary = policy_scan.get("summary") or {}
    if isinstance(summary, dict):
        return int(summary.get("active_hard_fail_count") or 0)
    return 0
```

- [ ] **Step 6: Export archive and tribunal**

Update `nexusnet/developmental/__init__.py` so it exports `GrowthArchive` and `PromotionTribunal`.

- [ ] **Step 7: Run tests**

Run: `pytest tests/test_growth_archive_and_promotion_tribunal.py -q`

Expected: `2 passed`.

- [ ] **Step 8: Commit**

```bash
git add nexusnet/developmental tests/test_growth_archive_and_promotion_tribunal.py
git commit -m "feat: add growth archive and promotion tribunal"
```

### Task 6: Developmental Cortex Kernel

**Files:**
- Modify: `nexusnet/developmental/contracts.py`
- Create: `nexusnet/developmental/kernel.py`
- Create: `tests/test_developmental_cortex_kernel.py`

- [ ] **Step 1: Write the kernel orchestration test**

Create `tests/test_developmental_cortex_kernel.py`:

```python
from nexusnet.developmental.kernel import DevelopmentalCortexKernel


def test_developmental_cortex_kernel_returns_non_mutating_growth_packet(tmp_path):
    kernel = DevelopmentalCortexKernel(artifacts_dir=tmp_path)

    result = kernel.assess(
        request_id="dev:req:001",
        task_ref="task:improve-routing",
        trace_refs=["trace:route-1"],
        evidence_refs=["eval:route-shadow", "cache-ledger:baseline"],
        runtime_state={"runtime_state": "live-bound", "provider_count": 2},
        memory_state={"runtime_state": "live-bound", "claim_count": 1},
        authority_state={"runtime_state": "live-bound", "grant_count": 0},
        eval_state={"runtime_state": "live-bound", "suite_count": 1},
    )

    assert result["surface_id"] == "developmental-cortex-kernel"
    assert result["status"] == "shadow-ready"
    assert result["production_mutation_allowed"] is False
    assert result["body_schema_snapshot"]["surface_id"] == "nexus-body-schema"
    assert result["reference_frame"]["frame_id"].startswith("frame:task:")
    assert result["simulation"]["status"] == "shadow-recorded"
    assert result["growth_candidate"]["promotion_state"] == "archived-shadow"
    assert result["promotion_case"]["decision"] == "accepted-shadow"
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `pytest tests/test_developmental_cortex_kernel.py -q`

Expected: import failure for `DevelopmentalCortexKernel`.

- [ ] **Step 3: Add kernel output contract**

Append to `nexusnet/developmental/contracts.py`:

```python
class DevelopmentalCortexResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    surface_id: str = "developmental-cortex-kernel"
    authority: str = "NexusBrain"
    request_id: str
    task_ref: str
    status: Literal["shadow-ready", "blocked"] = "shadow-ready"
    body_schema_snapshot: dict[str, object]
    reference_frame: dict[str, object]
    simulation: dict[str, object]
    causal_intervention: dict[str, object]
    growth_candidate: dict[str, object]
    promotion_case: dict[str, object]
    production_mutation_allowed: bool = False
```

- [ ] **Step 4: Implement the kernel**

Create `nexusnet/developmental/kernel.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from .body_schema import NexusBodySchemaBuilder
from .causal_lab import CausalInterventionLab
from .contracts import DevelopmentalCortexResult
from .growth_archive import GrowthArchive
from .promotion_tribunal import PromotionTribunal
from .reference_frames import ReferenceFrameStore
from .simulator import DreamingSimulator


class DevelopmentalCortexKernel:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = artifacts_dir
        self.body_schema = NexusBodySchemaBuilder()
        self.reference_frames = ReferenceFrameStore(artifacts_dir=artifacts_dir)
        self.simulator = DreamingSimulator(artifacts_dir=artifacts_dir)
        self.causal_lab = CausalInterventionLab(artifacts_dir=artifacts_dir)
        self.growth_archive = GrowthArchive(artifacts_dir=artifacts_dir)
        self.tribunal = PromotionTribunal()

    def assess(
        self,
        *,
        request_id: str,
        task_ref: str,
        trace_refs: list[str],
        evidence_refs: list[str],
        runtime_state: dict[str, Any],
        memory_state: dict[str, Any],
        authority_state: dict[str, Any],
        eval_state: dict[str, Any],
    ) -> dict[str, Any]:
        body = self.body_schema.snapshot(
            runtime_state=runtime_state,
            memory_state=memory_state,
            authority_state=authority_state,
            eval_state=eval_state,
        )
        frame = self.reference_frames.record(
            frame_id=f"frame:task:{request_id.replace(':', '_')}",
            frame_type="task",
            subject_ref=task_ref,
            facts=[
                {
                    "claim": "Developmental cortex assessment is shadow-only and evidence-gated.",
                    "source_ref": "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
                }
            ],
            evidence_refs=evidence_refs,
            uncertainty=0.15,
        )
        simulation = self.simulator.record_simulation(
            simulation_id=f"sim:{request_id.replace(':', '_')}",
            seed_trace_ref=trace_refs[0] if trace_refs else task_ref,
            scenario={"task_ref": task_ref, "trace_refs": trace_refs},
            expected_outcomes=["promotion_case_created", "growth_candidate_archived"],
            evidence_refs=evidence_refs,
        )
        causal = self.causal_lab.record_intervention(
            intervention_id=f"causal:{request_id.replace(':', '_')}",
            variable="evidence_gate",
            control_value="without_developmental_kernel",
            treatment_value="with_developmental_kernel",
            observed_delta={"reviewability": 0.1 if evidence_refs else 0.0},
            evidence_refs=evidence_refs,
        )
        candidate = self.growth_archive.record_candidate(
            candidate_id=f"growth:{request_id.replace(':', '_')}",
            candidate_type="research",
            diversity_key="developmental-cortex",
            scores={"quality": 0.7, "safety": 0.95},
            evidence_refs=evidence_refs,
        )
        promotion = self.tribunal.decide(
            case_id=f"case:{request_id.replace(':', '_')}",
            candidate_ref=candidate["candidate_id"],
            requested_state="shadow",
            policy_scan={"summary": {"active_hard_fail_count": 0}},
            eval_gate={"promotion_allowed": bool(evidence_refs)},
            artifact_trust={"promotion_allowed": bool(evidence_refs), "promotion_blockers": []},
            self_review={"status": "accepted-shadow"},
            memory_quality={"status": "verified"},
            rollback={"rollback_restorable": True},
            operator_approved=False,
        )
        blocked = any(
            item.get("runtime_state") == "degraded" or item.get("status") == "blocked"
            for item in [body, frame, simulation, causal]
        ) or promotion["decision"] == "rejected"
        return DevelopmentalCortexResult(
            request_id=request_id,
            task_ref=task_ref,
            status="blocked" if blocked else "shadow-ready",
            body_schema_snapshot=body,
            reference_frame=frame,
            simulation=simulation,
            causal_intervention=causal,
            growth_candidate=candidate,
            promotion_case=promotion,
        ).model_dump(mode="json")
```

- [ ] **Step 5: Export the kernel**

Update `nexusnet/developmental/__init__.py` so it exports `DevelopmentalCortexKernel`.

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_developmental_cortex_kernel.py -q`

Expected: `1 passed`.

- [ ] **Step 7: Run all developmental tests**

Run: `pytest tests/test_developmental_body_schema.py tests/test_reference_frame_store.py tests/test_developmental_simulation_and_causal_lab.py tests/test_growth_archive_and_promotion_tribunal.py tests/test_developmental_cortex_kernel.py -q`

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add nexusnet/developmental tests/test_developmental_*.py tests/test_growth_archive_and_promotion_tribunal.py tests/test_reference_frame_store.py
git commit -m "feat: add developmental cortex kernel"
```

## Wave 2: Authority Integrity Spine

### Task 7: Effect, Capability, Observed-Effect, And Rollback Records

**Files:**
- Create: `nexusnet/authority/contracts.py`
- Create: `nexusnet/authority/spine.py`
- Create: `nexusnet/authority/__init__.py`
- Create: `tests/test_authority_integrity_spine.py`

- [ ] **Step 1: Write authority spine tests**

Create `tests/test_authority_integrity_spine.py`:

```python
from nexusnet.authority.spine import AuthorityIntegritySpine


def test_authority_spine_blocks_write_effect_without_sandbox_and_approval(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id="action:file-write",
        actor_ref="agent:researcher",
        effect_type="filesystem_write",
        capability_refs=[],
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:file-write-request"],
    )

    assert decision["status"] == "blocked"
    assert "write_effect_requires_sandbox" in decision["blockers"]
    assert "write_effect_requires_operator_approval" in decision["blockers"]
    assert decision["production_action_allowed"] is False


def test_authority_spine_records_readonly_receipt(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id="action:file-read",
        actor_ref="agent:researcher",
        effect_type="filesystem_read",
        capability_refs=["cap:repo-read"],
        sandbox_state="project-readonly",
        operator_approved=False,
        evidence_refs=["trace:file-read-request"],
    )

    assert decision["status"] == "allowed-shadow"
    assert decision["observed_effect_receipt"]["declared_effect_type"] == "filesystem_read"
    assert decision["rollback_record"]["rollback_required"] is False
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_authority_integrity_spine.py -q`

Expected: import failure.

- [ ] **Step 3: Add authority contracts**

Create `nexusnet/authority/contracts.py`:

```python
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EffectType = Literal["filesystem_read", "filesystem_write", "network", "browser", "desktop", "shell", "model_update", "memory_update"]


class AuthorityDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    actor_ref: str
    effect_type: EffectType
    status: Literal["allowed-shadow", "blocked"]
    blockers: list[str] = Field(default_factory=list)
    capability_refs: list[str] = Field(default_factory=list)
    sandbox_state: str
    operator_approved: bool
    evidence_refs: list[str] = Field(default_factory=list)
    observed_effect_receipt: dict[str, object]
    rollback_record: dict[str, object]
    production_action_allowed: bool = False
    artifact_path: str | None = None
```

- [ ] **Step 4: Implement authority spine**

Create `nexusnet/authority/spine.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import AuthorityDecisionRecord


WRITE_EFFECTS = {"filesystem_write", "shell", "desktop", "browser", "model_update", "memory_update"}


class AuthorityIntegritySpine:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "authority" / "decisions" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def evaluate(
        self,
        *,
        action_id: str,
        actor_ref: str,
        effect_type: str,
        capability_refs: list[str],
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        blockers = []
        if not evidence_refs:
            blockers.append("authority_decision_requires_evidence_refs")
        if effect_type in WRITE_EFFECTS and sandbox_state in {"", "none", "unknown"}:
            blockers.append("write_effect_requires_sandbox")
        if effect_type in WRITE_EFFECTS and not operator_approved:
            blockers.append("write_effect_requires_operator_approval")
        receipt = {
            "receipt_id": f"effect::{action_id}",
            "declared_effect_type": effect_type,
            "observed_effect_type": effect_type,
            "created_at": utcnow().isoformat(),
        }
        rollback = {
            "rollback_id": f"rollback::{action_id}",
            "rollback_required": effect_type in WRITE_EFFECTS,
            "rollback_available": False,
        }
        record = AuthorityDecisionRecord(
            action_id=action_id,
            actor_ref=actor_ref,
            effect_type=effect_type,
            status="blocked" if blockers else "allowed-shadow",
            blockers=sorted(set(blockers)),
            capability_refs=capability_refs,
            sandbox_state=sandbox_state,
            operator_approved=operator_approved,
            evidence_refs=evidence_refs,
            observed_effect_receipt=receipt,
            rollback_record=rollback,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "authority-integrity-spine",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in self._records) else ("live-bound" if self._records else "static-canon"),
            "decision_count": len(self._records),
            "blocked_count": sum(1 for record in self._records if record.get("status") == "blocked"),
            "latest_decision": self._records[0] if self._records else None,
            "production_action_boundary": "write-effects-require-sandbox-operator-approval-and-evidence",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['action_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 5: Export authority spine**

Create `nexusnet/authority/__init__.py`:

```python
from .contracts import AuthorityDecisionRecord
from .spine import AuthorityIntegritySpine

__all__ = ["AuthorityDecisionRecord", "AuthorityIntegritySpine"]
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_authority_integrity_spine.py -q`

Expected: `2 passed`.

- [ ] **Step 7: Commit**

```bash
git add nexusnet/authority tests/test_authority_integrity_spine.py
git commit -m "feat: add authority integrity spine"
```

## Wave 3: Evidence Store And Assurance Projections

### Task 8: Content-Addressed Evidence Store

**Files:**
- Create: `nexusnet/evidence/contracts.py`
- Create: `nexusnet/evidence/store.py`
- Create: `nexusnet/evidence/__init__.py`
- Create: `tests/test_evidence_store.py`

- [ ] **Step 1: Write evidence store tests**

Create `tests/test_evidence_store.py`:

```python
from nexusnet.evidence.store import EvidenceStore


def test_evidence_store_hash_chains_records(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)

    first = store.append(kind="eval", subject_ref="suite:route", payload={"score": 0.91}, source_refs=["eval:route"])
    second = store.append(kind="policy", subject_ref="policy:tool", payload={"blocked": False}, source_refs=["policy:scan"])

    assert first["content_hash"].startswith("sha256:")
    assert second["previous_hash"] == first["content_hash"]
    assert second["content_hash"] != first["content_hash"]


def test_evidence_store_projection_counts_by_kind(tmp_path):
    store = EvidenceStore(artifacts_dir=tmp_path)
    store.append(kind="eval", subject_ref="suite:route", payload={"score": 0.91}, source_refs=["eval:route"])
    store.append(kind="eval", subject_ref="suite:cache", payload={"score": 0.83}, source_refs=["eval:cache"])

    projection = store.projection()

    assert projection["record_count"] == 2
    assert projection["kind_counts"]["eval"] == 2
    assert projection["runtime_state"] == "live-bound"
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_evidence_store.py -q`

Expected: import failure.

- [ ] **Step 3: Add evidence contract and store**

Create `nexusnet/evidence/contracts.py`:

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    kind: str
    subject_ref: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source_refs: list[str] = Field(default_factory=list)
    previous_hash: str = ""
    content_hash: str
    artifact_path: str | None = None
```

Create `nexusnet/evidence/store.py`:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import EvidenceRecord


class EvidenceStore:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "evidence" / "records" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def append(self, *, kind: str, subject_ref: str, payload: dict[str, Any], source_refs: list[str]) -> dict[str, Any]:
        previous_hash = self._records[0]["content_hash"] if self._records else ""
        base = {
            "record_id": f"evidence::{kind}::{len(self._records) + 1}",
            "kind": kind,
            "subject_ref": subject_ref,
            "payload": payload,
            "source_refs": source_refs,
            "previous_hash": previous_hash,
            "created_at": utcnow().isoformat(),
        }
        digest = hashlib.sha256(json.dumps(base, sort_keys=True).encode("utf-8")).hexdigest()
        record = EvidenceRecord(**base, content_hash=f"sha256:{digest}").model_dump(mode="json")
        self._records.insert(0, record)
        if self.root is not None:
            path = self.root / f"{digest[:16]}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return record

    def projection(self) -> dict[str, Any]:
        kind_counts: dict[str, int] = {}
        for record in self._records:
            kind = str(record.get("kind") or "unknown")
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        return {
            "surface_id": "content-addressed-evidence-store",
            "authority": "NexusBrain",
            "runtime_state": "live-bound" if self._records else "static-canon",
            "record_count": len(self._records),
            "kind_counts": kind_counts,
            "latest_hash": self._records[0]["content_hash"] if self._records else "",
        }
```

- [ ] **Step 4: Export evidence store**

Create `nexusnet/evidence/__init__.py`:

```python
from .contracts import EvidenceRecord
from .store import EvidenceStore

__all__ = ["EvidenceRecord", "EvidenceStore"]
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_evidence_store.py -q`

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add nexusnet/evidence tests/test_evidence_store.py
git commit -m "feat: add content addressed evidence store"
```

## Wave 4: Eval Federation

### Task 9: Normalized Eval Event Schema

**Files:**
- Create: `nexusnet/evals/federation.py`
- Modify: `nexusnet/evals/__init__.py`
- Create: `tests/test_eval_federation.py`

- [ ] **Step 1: Write eval federation tests**

Create `tests/test_eval_federation.py`:

```python
from nexusnet.evals.federation import EvalFederationRegistry


def test_eval_federation_records_external_adapter_shape(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:browsergym:001",
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:browser-readonly",
        scores={"success": 0.8, "safety": 1.0},
        evidence_refs=["trace:browsergym-fixture"],
        held_out=True,
    )

    assert event["status"] == "recorded"
    assert event["promotion_allowed"] is True
    assert event["adapter"] == "browsergym"


def test_eval_federation_blocks_non_held_out_eval(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:swebench:001",
        adapter="swebench",
        target_surface="coding",
        candidate_ref="patch:demo",
        scores={"success": 1.0, "safety": 1.0},
        evidence_refs=["trace:swebench-fixture"],
        held_out=False,
    )

    assert event["status"] == "blocked"
    assert event["promotion_allowed"] is False
    assert "eval_event_requires_held_out_set" in event["findings"]
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_eval_federation.py -q`

Expected: import failure.

- [ ] **Step 3: Implement eval federation**

Create `nexusnet/evals/federation.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvalFederationRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "evals" / "federation" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._events: list[dict[str, Any]] = []

    def record_event(
        self,
        *,
        event_id: str,
        adapter: str,
        target_surface: str,
        candidate_ref: str,
        scores: dict[str, float],
        evidence_refs: list[str],
        held_out: bool,
    ) -> dict[str, Any]:
        findings = []
        if not held_out:
            findings.append("eval_event_requires_held_out_set")
        if not evidence_refs:
            findings.append("eval_event_requires_evidence_refs")
        if scores.get("safety", 0.0) < 0.8:
            findings.append("eval_event_safety_below_gate")
        event = {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "event_id": event_id,
            "adapter": adapter,
            "target_surface": target_surface,
            "candidate_ref": candidate_ref,
            "scores": scores,
            "evidence_refs": evidence_refs,
            "held_out": held_out,
            "status": "blocked" if findings else "recorded",
            "promotion_allowed": not findings,
            "findings": findings,
        }
        self._persist(event)
        return event

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(event.get("status") == "blocked" for event in self._events) else ("live-bound" if self._events else "static-canon"),
            "event_count": len(self._events),
            "adapters": sorted({event.get("adapter") for event in self._events}),
            "latest_event": self._events[0] if self._events else None,
        }

    def _persist(self, event: dict[str, Any]) -> None:
        self._events.insert(0, event)
        if self.root is None:
            return
        path = self.root / f"{event['event_id'].replace(':', '_').replace('/', '_')}.json"
        event["artifact_path"] = str(path)
        path.write_text(json.dumps(event, indent=2, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 4: Export eval federation**

Update the imports at the top of `nexusnet/evals/__init__.py` to include:

```python
from .federation import EvalFederationRegistry
```

Add `"EvalFederationRegistry"` to the existing `__all__` list between `"EvalRegistry"` and `"EvalSuiteRequest"`.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_eval_federation.py -q`

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add nexusnet/evals tests/test_eval_federation.py
git commit -m "feat: add eval federation registry"
```

## Wave 5: Tool And Computer-Use Harness

### Task 10: Read-Only Tool Action Harness

**Files:**
- Create: `nexusnet/tools/action_harness.py`
- Create: `tests/test_tool_action_harness.py`

- [ ] **Step 1: Write tool harness tests**

Create `tests/test_tool_action_harness.py`:

```python
from nexusnet.tools.action_harness import ToolActionHarness


def test_tool_action_harness_allows_readonly_observation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is False


def test_tool_action_harness_requires_confirmation_for_mutation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:desktop:click",
        tool_ref="desktop",
        action_type="click",
        requested_effect="desktop",
        contains_private_data=True,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:click"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_tool_action_harness.py -q`

Expected: import failure.

- [ ] **Step 3: Implement action harness**

Create `nexusnet/tools/action_harness.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MUTATING_ACTIONS = {"click", "type", "write", "submit", "delete", "shell", "install"}


class ToolActionHarness:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "tools" / "action-harness" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._plans: list[dict[str, Any]] = []

    def plan_action(
        self,
        *,
        action_id: str,
        tool_ref: str,
        action_type: str,
        requested_effect: str,
        contains_private_data: bool,
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        mutating = action_type in MUTATING_ACTIONS
        findings = []
        if not evidence_refs:
            findings.append("tool_action_requires_evidence_refs")
        if mutating and sandbox_state in {"", "none", "unknown"}:
            findings.append("mutating_tool_action_requires_sandbox")
        if mutating and not operator_approved:
            findings.append("mutating_tool_action_requires_operator_confirmation")
        if contains_private_data and not operator_approved:
            findings.append("private_tool_context_requires_operator_confirmation")
        plan = {
            "surface_id": "tool-action-harness",
            "authority": "NexusBrain",
            "action_id": action_id,
            "tool_ref": tool_ref,
            "action_type": action_type,
            "requested_effect": requested_effect,
            "contains_private_data": contains_private_data,
            "sandbox_state": sandbox_state,
            "operator_approved": operator_approved,
            "evidence_refs": evidence_refs,
            "status": "blocked" if findings else "planned-shadow",
            "execution_allowed": False,
            "operator_confirmation_required": mutating or contains_private_data,
            "findings": findings,
            "trace_contract": "plan-only-replayable-no-direct-tool-execution",
        }
        self._persist(plan)
        return plan

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "tool-action-harness",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(plan.get("status") == "blocked" for plan in self._plans) else ("live-bound" if self._plans else "static-canon"),
            "plan_count": len(self._plans),
            "latest_plan": self._plans[0] if self._plans else None,
        }

    def _persist(self, plan: dict[str, Any]) -> None:
        self._plans.insert(0, plan)
        if self.root is None:
            return
        path = self.root / f"{plan['action_id'].replace(':', '_').replace('/', '_')}.json"
        plan["artifact_path"] = str(path)
        path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_tool_action_harness.py -q`

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add nexusnet/tools/action_harness.py tests/test_tool_action_harness.py
git commit -m "feat: add read only tool action harness"
```

## Wave 6: Runtime Decision Ledger

### Task 11: Runtime Decision Ledger

**Files:**
- Create: `nexusnet/runtime/decision_ledger.py`
- Modify: `nexusnet/runtime/__init__.py`
- Create: `tests/test_runtime_decision_ledger.py`

- [ ] **Step 1: Write runtime decision ledger tests**

Create `tests/test_runtime_decision_ledger.py`:

```python
from nexusnet.runtime.decision_ledger import RuntimeDecisionLedger


def test_runtime_decision_ledger_combines_route_cache_quantization_and_eval(tmp_path):
    ledger = RuntimeDecisionLedger(artifacts_dir=tmp_path)

    record = ledger.record(
        decision_id="runtime:decision:001",
        route_decision={"status": "routed-shadow", "provider": {"provider_id": "local"}, "estimated_cost_usd": 0.0},
        cache_state={"status": "measured", "promotion_allowed": True},
        quantization_state={"status": "recommended", "promotion_blockers": []},
        eval_state={"promotion_allowed": True},
        evidence_refs=["route:001", "cache:001", "eval:001"],
    )

    assert record["status"] == "ready-shadow"
    assert record["promotion_allowed"] is True
    assert record["estimated_cost_usd"] == 0.0


def test_runtime_decision_ledger_blocks_missing_eval(tmp_path):
    ledger = RuntimeDecisionLedger(artifacts_dir=tmp_path)

    record = ledger.record(
        decision_id="runtime:decision:002",
        route_decision={"status": "routed-shadow"},
        cache_state={"status": "measured", "promotion_allowed": True},
        quantization_state={"status": "recommended", "promotion_blockers": []},
        eval_state={"promotion_allowed": False},
        evidence_refs=["route:002"],
    )

    assert record["status"] == "blocked"
    assert "runtime_decision_eval_gate_not_clear" in record["findings"]
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_runtime_decision_ledger.py -q`

Expected: import failure.

- [ ] **Step 3: Implement runtime decision ledger**

Create `nexusnet/runtime/decision_ledger.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RuntimeDecisionLedger:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "runtime" / "decision-ledger" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record(
        self,
        *,
        decision_id: str,
        route_decision: dict[str, Any],
        cache_state: dict[str, Any],
        quantization_state: dict[str, Any],
        eval_state: dict[str, Any],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("runtime_decision_requires_evidence_refs")
        if str(route_decision.get("status") or "").startswith("blocked"):
            findings.append("runtime_decision_route_blocked")
        if cache_state.get("promotion_allowed") is not True:
            findings.append("runtime_decision_cache_gate_not_clear")
        if quantization_state.get("promotion_blockers"):
            findings.append("runtime_decision_quantization_blocked")
        if eval_state.get("promotion_allowed") is not True:
            findings.append("runtime_decision_eval_gate_not_clear")
        record = {
            "surface_id": "runtime-decision-ledger",
            "authority": "NexusBrain",
            "decision_id": decision_id,
            "route_decision": route_decision,
            "cache_state": cache_state,
            "quantization_state": quantization_state,
            "eval_state": eval_state,
            "evidence_refs": evidence_refs,
            "estimated_cost_usd": float(route_decision.get("estimated_cost_usd") or 0.0),
            "status": "blocked" if findings else "ready-shadow",
            "promotion_allowed": not findings,
            "findings": findings,
        }
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "runtime-decision-ledger",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in self._records) else ("live-bound" if self._records else "static-canon"),
            "decision_count": len(self._records),
            "latest_decision": self._records[0] if self._records else None,
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['decision_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 4: Export runtime decision ledger**

Update `nexusnet/runtime/__init__.py`.

Add `"RuntimeDecisionLedger"` to the existing `__all__` list after `"ModelPassportRequest"`.

Add this branch to `__getattr__` before the final `raise AttributeError(name)`:

```python
    if name == "RuntimeDecisionLedger":
        from .decision_ledger import RuntimeDecisionLedger

        return RuntimeDecisionLedger
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_runtime_decision_ledger.py -q`

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add nexusnet/runtime/decision_ledger.py nexusnet/runtime/__init__.py tests/test_runtime_decision_ledger.py
git commit -m "feat: add runtime decision ledger"
```

## Wave 7: Control Panel And Visualizer Integration

### Task 12: Developmental Scorecard In Visual Layout

**Files:**
- Modify: `nexusnet/visuals/layout.py`
- Modify: `ui/control-panel/app.js`
- Modify: `tests/test_nexusnet_visualizer.py`

- [ ] **Step 1: Run GitNexus impact for `NexusNetVisualizationBuilder` or the exact layout symbol being modified**

Run: `gitnexus_impact` on the selected symbol in `nexusnet/visuals/layout.py`.

Expected: LOW or MEDIUM risk before editing. If HIGH or CRITICAL appears, report the affected processes and split the UI integration into smaller tasks.

- [ ] **Step 2: Write visualizer payload test**

Add this test to `tests/test_nexusnet_visualizer.py`:

```python
def test_control_panel_exposes_developmental_cortex_scorecard(client):
    response = client.get("/ops/brain/control-panel")

    assert response.status_code == 200
    payload = response.json()
    scorecard = payload["developmental_cortex_scorecard"]
    assert scorecard["surface_id"] == "developmental-cortex-kernel"
    assert scorecard["production_mutation_allowed"] is False
    assert "body_schema" in scorecard["subsurfaces"]
    assert "promotion_tribunal" in scorecard["subsurfaces"]
```

- [ ] **Step 3: Run the test and verify it fails**

Run: `pytest tests/test_nexusnet_visualizer.py::test_control_panel_exposes_developmental_cortex_scorecard -q`

Expected: failure because `developmental_cortex_scorecard` is absent.

- [ ] **Step 4: Add visual layout payload**

In `nexusnet/visuals/layout.py`, instantiate the new scorecard near the other scorecards:

```python
from nexusnet.developmental.kernel import DevelopmentalCortexKernel
```

Then add a payload:

```python
developmental_cortex = {
    "surface_id": "developmental-cortex-kernel",
    "authority": "NexusBrain",
    "runtime_state": "static-canon",
    "production_mutation_allowed": False,
    "subsurfaces": {
        "body_schema": "nexus-body-schema",
        "reference_frames": "reference-frame-store",
        "dreaming_simulator": "dreaming-simulator",
        "causal_lab": "causal-intervention-lab",
        "growth_archive": "growth-archive",
        "promotion_tribunal": "promotion-tribunal",
    },
    "operator_actions": {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/canon/developmental-cortex"},
    },
}
```

Add it to the returned Control Panel payload as:

```python
"developmental_cortex_scorecard": developmental_cortex,
```

- [ ] **Step 5: Add Control Panel renderer**

In `ui/control-panel/app.js`, add state binding near other scorecards:

```javascript
state.developmentalCortex = state.controlPanel.developmental_cortex_scorecard || null;
```

Add a renderer:

```javascript
function renderDevelopmentalCortexScorecard() {
  const scorecard = state.developmentalCortex || {};
  fill(dom.developmentalCortexScorecard, `
    <div class="scorecard-head">
      <strong>Developmental Cortex</strong>
      <span class="state-pill ${scorecard.runtime_state === "degraded" ? "blocked" : "live-bound"}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
    </div>
    <div class="completion-scope">Production mutation: ${scorecard.production_mutation_allowed ? "allowed" : "blocked"}</div>
    ${scorecardLaneGrid(Object.entries(scorecard.subsurfaces || {}).map(([lane_id, label]) => ({
      lane_id,
      label,
      state: "mapped"
    })))}
  `);
}
```

Add the DOM binding only if `ui/control-panel/index.html` already has a suitable empty card. If no card exists, add a single un-nested card with id `developmentalCortexScorecard` beside existing scorecard cards.

- [ ] **Step 6: Run focused tests**

Run: `pytest tests/test_nexusnet_visualizer.py::test_control_panel_exposes_developmental_cortex_scorecard -q`

Expected: pass.

- [ ] **Step 7: Run visualizer regression slice**

Run: `pytest tests/test_nexusnet_visualizer.py -q`

Expected: all tests in that file pass.

- [ ] **Step 8: Commit**

```bash
git add nexusnet/visuals/layout.py ui/control-panel/app.js ui/control-panel/index.html tests/test_nexusnet_visualizer.py
git commit -m "feat: surface developmental cortex in control panel"
```

## Wave 8: Full Assimilation Closeout

### Task 13: Full Assimilation Implementation Dossier

**Files:**
- Create: `docs/assimilation/FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md`

- [ ] **Step 1: Create the dossier after code waves pass**

Create `docs/assimilation/FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md` with this structure:

```markdown
# Full Assimilation Implementation Dossier - 2026-05-06

Status: implementation dossier for the 144-spec assimilation packet.

## Scope

- Online specs: 134
- Video specs: 10
- Final synthesis target: governed developmental cortex

## Implemented Surfaces

| Surface | Code | Tests | Boundary |
| --- | --- | --- | --- |
| Developmental cortex | `nexusnet/developmental/kernel.py` | `tests/test_developmental_cortex_kernel.py` | shadow-only |
| Body schema | `nexusnet/developmental/body_schema.py` | `tests/test_developmental_body_schema.py` | no production mutation |
| Reference frames | `nexusnet/developmental/reference_frames.py` | `tests/test_reference_frame_store.py` | context model only |
| Simulation and causal lab | `nexusnet/developmental/simulator.py`, `nexusnet/developmental/causal_lab.py` | `tests/test_developmental_simulation_and_causal_lab.py` | no learned-world-model claim |
| Growth archive and tribunal | `nexusnet/developmental/growth_archive.py`, `nexusnet/developmental/promotion_tribunal.py` | `tests/test_growth_archive_and_promotion_tribunal.py` | gated promotion only |
| Authority spine | `nexusnet/authority/spine.py` | `tests/test_authority_integrity_spine.py` | write effects blocked without sandbox and approval |
| Evidence store | `nexusnet/evidence/store.py` | `tests/test_evidence_store.py` | hash-chained local evidence |
| Eval federation | `nexusnet/evals/federation.py` | `tests/test_eval_federation.py` | held-out eval required |
| Tool action harness | `nexusnet/tools/action_harness.py` | `tests/test_tool_action_harness.py` | plan-only, no direct execution |
| Runtime decision ledger | `nexusnet/runtime/decision_ledger.py` | `tests/test_runtime_decision_ledger.py` | route/cache/quant/eval gates required |

## Claims Still Blocked

- Consciousness, sentience, or upload claims
- Production self-mutation
- Active promotion without operator approval
- Learned world-model behavior without model-backed evals
- External benchmark certification without runnable adapters
- OS-level sandbox enforcement without platform-specific proof

## Verification

Record exact command output from the final verification task here.
```

- [ ] **Step 2: Run release hygiene scan**

Run:

```powershell
$patterns = @('T'+'BD', 'T'+'ODO', 'FIX'+'ME', 'PLACE'+'HOLDER', 'C:'+'\', 'F:'+'\', 'Users'+'\'+'ChrisBoyd')
$hits = foreach ($pattern in $patterns) {
    Select-String -Path docs\assimilation\FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md -Pattern ([regex]::Escape($pattern))
}
if ($hits) { $hits; exit 2 } else { 'RELEASE_HYGIENE_OK' }
```

Expected: `RELEASE_HYGIENE_OK`.

- [ ] **Step 3: Run ASCII scan**

Run:

```powershell
$text = Get-Content -Raw docs\assimilation\FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md
$nonAscii = [regex]::Matches($text, '[^\x00-\x7F]')
if ($nonAscii.Count -eq 0) { 'ASCII_OK' } else { $nonAscii | Select-Object -First 20 }
```

Expected: `ASCII_OK`.

- [ ] **Step 4: Commit**

```bash
git add docs/assimilation/FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md
git commit -m "docs: add full assimilation implementation dossier"
```

### Task 14: Final Verification Gate

**Files:**
- No code files created.

- [ ] **Step 1: Run focused test suite**

Run:

```bash
pytest tests/test_developmental_body_schema.py tests/test_reference_frame_store.py tests/test_developmental_simulation_and_causal_lab.py tests/test_growth_archive_and_promotion_tribunal.py tests/test_developmental_cortex_kernel.py tests/test_authority_integrity_spine.py tests/test_evidence_store.py tests/test_eval_federation.py tests/test_tool_action_harness.py tests/test_runtime_decision_ledger.py tests/test_nexusnet_visualizer.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run package import smoke**

Run:

```powershell
@'
from nexusnet.developmental import DevelopmentalCortexKernel
from nexusnet.authority import AuthorityIntegritySpine
from nexusnet.evidence import EvidenceStore
from nexusnet.evals.federation import EvalFederationRegistry
from nexusnet.runtime.decision_ledger import RuntimeDecisionLedger
print("IMPORT_SMOKE_OK")
'@ | python -
```

Expected: `IMPORT_SMOKE_OK`.

- [ ] **Step 3: Run shareability scan for new artifacts**

Run:

```powershell
$patterns = @('C:'+'\', 'F:'+'\', 'Users'+'\'+'ChrisBoyd', 'LOCAL_VIDEO'+'_WATCH_OUTPUT')
$paths = @(
    'nexusnet/developmental',
    'nexusnet/authority',
    'nexusnet/evidence',
    'nexusnet/evals/federation.py',
    'nexusnet/tools/action_harness.py',
    'nexusnet/runtime/decision_ledger.py',
    'tests',
    'docs/assimilation/FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md'
)
$files = foreach ($path in $paths) {
    if (Test-Path $path -PathType Container) {
        Get-ChildItem -Path $path -Recurse -File
    } elseif (Test-Path $path -PathType Leaf) {
        Get-Item $path
    }
}
$hits = foreach ($pattern in $patterns) {
    $files | Select-String -Pattern ([regex]::Escape($pattern))
}
if ($hits) { $hits; exit 2 } else { 'SHAREABILITY_SCAN_OK' }
```

Expected: `SHAREABILITY_SCAN_OK`.

- [ ] **Step 4: Run GitNexus change detection before commit or PR**

Run: `gitnexus_detect_changes()` with `scope="all"` for repo `NexusNet`.

Expected: changed symbols match this plan: developmental cortex, authority spine, evidence store, eval federation, tool action harness, runtime decision ledger, visual layout, and tests.

- [ ] **Step 5: Commit verification updates**

If verification requires only dossier updates, run:

```bash
git add docs/assimilation/FULL_IMPLEMENTATION_DOSSIER_2026-05-06.md
git commit -m "docs: record full assimilation verification"
```

## Coverage Map

| Assimilation domain | Implementation wave |
| --- | --- |
| Final missing piece, ranks 123-134 | Waves 1 and 2 |
| Synthetic truth, source status, KAC, memory quality | Waves 1, 3, and existing KAC/memory modules |
| Darwin Godel, AlphaEvolve, verifier search | Waves 1, 4, and existing verifier search |
| Runtime ladder, KV cache, quantization, model routing | Wave 6 and existing runtime modules |
| Browser, desktop, TARS, Jarvis-style operator surfaces | Wave 5 and existing computer-use/operator modules |
| MCP, protocol trust, object capability, effect authority | Wave 2 and existing protocol/policy modules |
| Event sourcing, evidence DAG, assurance cases | Wave 3 |
| Benchmarks and eval federation | Wave 4 |
| Control Panel visibility | Wave 7 |

## Residual Work After This Plan

- External benchmark adapters can be added one at a time after `EvalFederationRegistry` is stable.
- OS-level sandbox enforcement can be added per platform after `AuthorityIntegritySpine` records decisions.
- Learned world-model and GFlowNet implementations can be added after the deterministic simulator, causal lab, and growth archive have real replay/eval data.
- Capability tokens, FGA, SCITT, C2PA, trusted time, and WASM compartments can be attached to the authority and evidence contracts without changing the developmental cortex interface.
