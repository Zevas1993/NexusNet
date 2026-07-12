# Universal Evolution Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first end-to-end NexusNet evolution slice: NexusBrain-owned, versioned evolvable-unit contracts; sanitized append-only Everything State; evidence-ranked Growth Pressure; honest compatibility with the existing self-improvement engine; and runtime-visible API, release, and Control Panel status.

**Architecture:** Add a focused `nexusnet.evolution` package that owns contracts, persistence, registry, pressure ranking, foundation verification, and read-only projections. Existing self-improvement code remains the compute-lane implementation and is adapted into the registry without changing its public behavior. `NexusServices` owns one evolution service under NexusBrain authority; API and release surfaces project sanitized summaries and never perform protected mutation.

**Tech Stack:** Python 3.10+, Pydantic 2.7+, FastAPI, standard-library JSONL/SHA-256 persistence, pytest, vanilla JavaScript Control Panel, GitNexus.

## Global Constraints

- `NexusBrain` remains the permanent primary controller and identity root.
- Everything can influence everything only through typed, attributable contracts; influence never means unrestricted mutation.
- This slice is observational and registry-forming. It does not authorize production code, weight, route, permission, canonical-memory, or release mutation.
- Raw prompts, outputs, files, secrets, absolute local paths, and local user identifiers must not enter Everything State.
- Event history is append-only, hash-chained, replayable, and fail-closed on corruption.
- Unknown unit kinds require schema, authority, eval, privacy, and rollback definitions.
- Current `IMPROVABLE_ASPECTS` coverage remains a legacy compatibility claim, not proof that all NexusNet components are covered.
- Quality and safety claims remain proof-bound. No endpoint may imply candidate, shadow, prototype, or publication approval.
- Do not loosen the strict quality floor: no meaningful correctness, safety, privacy, instruction-adherence, or protected-domain regression; noncritical tolerance may never exceed `0.5%` under the design specification's conditions.
- Preserve unrelated dirty-worktree changes. Execute in an isolated worktree created through `superpowers:using-git-worktrees` unless the user explicitly chooses safe inline execution in the shared checkout.
- Before editing any existing function, class, or method, rerun upstream GitNexus impact analysis. `SelfImprovementEngine` was HIGH risk at plan time (137 transitive/test impacts), so do not edit it in this slice.
- Before every commit, run focused tests, `git diff --check`, and `gitnexus_detect_changes(scope="staged", repo="NexusNet")`.

---

## File Structure

- Create `nexusnet/evolution/__init__.py`: stable public exports for the evolution foundation.
- Create `nexusnet/evolution/contracts.py`: schema versions, unit/genome/pressure/foundation/snapshot models, enums, and reference sanitization.
- Create `nexusnet/evolution/store.py`: append-only hash-chained event storage, integrity validation, and deterministic replay.
- Create `nexusnet/evolution/registry.py`: evolvable-unit/genome registry and the compatibility adapter for current self-improvement lanes.
- Create `nexusnet/evolution/pressure.py`: Growth Pressure recording and deterministic evidence-aware prioritization.
- Create `nexusnet/evolution/foundation.py`: honest prerequisite verification with `verified`, `missing`, and `unverified` states.
- Create `nexusnet/evolution/service.py`: NexusBrain-owned facade and sanitized Everything State/status projections.
- Create `tests/test_universal_evolution_contracts.py`: contract, privacy, unknown-kind, and serialization tests.
- Create `tests/test_universal_evolution_store.py`: append, hash-chain, corruption, restart, and replay tests.
- Create `tests/test_universal_evolution_service.py`: registry bridge, coverage honesty, pressure ranking, and prerequisite tests.
- Create `tests/test_universal_evolution_api.py`: black-box API and release-status projection tests.
- Modify `nexus/services.py`: construct and expose the single evolution service.
- Modify `nexus/api/app.py`: add read-only evolution routes, preserve the legacy coverage route, and project evolution into wrapper status.
- Modify `ui/control-panel/app.js`: render a compact sanitized Universal Evolution card from wrapper status.
- Modify `tests/test_self_improvement_coverage_endpoint.py`: prove legacy compatibility plus explicit universal-coverage claim boundary.
- Modify `tests/test_release_wrapper_runtime.py`: prove restart-safe, session-sanitized evolution status.

### Task 1: Versioned Evolution Contracts and Privacy Boundary

**Files:**
- Create: `nexusnet/evolution/__init__.py`
- Create: `nexusnet/evolution/contracts.py`
- Test: `tests/test_universal_evolution_contracts.py`

**Interfaces:**
- Consumes: Pydantic `BaseModel`, `ConfigDict`, `Field`, and `model_validator`.
- Produces: `EvolvableUnit`, `GenomeRef`, `GrowthPressure`, `FoundationCheck`, `EverythingStateSnapshot`, `sanitize_reference(value: str) -> str`, `KNOWN_UNIT_KINDS`, and `EVOLUTION_SCHEMA_VERSION`.

- [ ] **Step 1: Write failing contract tests**

```python
# tests/test_universal_evolution_contracts.py
from __future__ import annotations

import pytest
from pydantic import ValidationError

from nexusnet.evolution.contracts import (
    EVOLUTION_SCHEMA_VERSION,
    EvolvableUnit,
    GenomeRef,
    GrowthPressure,
    sanitize_reference,
)


def _unit(**overrides):
    payload = {
        "unit_id": "unit:runtime:vulkan-pilot",
        "unit_kind": "runtime",
        "owner_brain_ref": "brain:NexusBrain",
        "authority_class": "mother-brain-governed",
        "privacy_class": "sanitized-metadata",
        "license_state": "reviewed",
        "trust_state": "quarantined",
        "federation_policy": "local-only",
        "lifecycle_state": "observed",
        "eval_suite_refs": ["eval:runtime-portability-v1"],
        "invariant_refs": ["policy:north-star-v1"],
        "checkpoint_refs": ["checkpoint:runtime-baseline-v1"],
        "rollback_refs": ["checkpoint:runtime-baseline-v1"],
    }
    payload.update(overrides)
    return EvolvableUnit(**payload)


def test_known_unit_round_trips_with_versioned_contract():
    unit = _unit()
    payload = unit.model_dump(mode="json")
    assert payload["schema_version"] == EVOLUTION_SCHEMA_VERSION
    assert payload["owner_brain_ref"] == "brain:NexusBrain"
    assert EvolvableUnit.model_validate(payload) == unit


def test_unknown_kind_requires_schema_eval_privacy_authority_and_rollback():
    with pytest.raises(ValidationError, match="unknown unit kind"):
        _unit(unit_kind="invented-neural-organ")
    unit = _unit(
        unit_kind="invented-neural-organ",
        registration_schema_ref="schema:invented-neural-organ-v1",
    )
    assert unit.unit_kind == "invented-neural-organ"


@pytest.mark.parametrize(
    "unsafe",
    [
        "C:/Users/ChrisBoyd/private.txt",
        "F:\\NexusNet\\secret.bin",
        "sk-secret-token",
        "Bearer abcdef",
        "-----BEGIN PRIVATE KEY-----",
        "evidence:line-one\nline-two",
    ],
)
def test_reference_sanitizer_rejects_private_or_secret_material(unsafe: str):
    with pytest.raises(ValueError, match="unsafe reference"):
        sanitize_reference(unsafe)


def test_genome_and_pressure_use_refs_not_raw_content():
    genome = GenomeRef(
        genome_id="genome:runtime:v1",
        family="runtime",
        content_ref="sha256:" + "a" * 64,
        invariant_refs=["policy:north-star-v1"],
    )
    pressure = GrowthPressure(
        pressure_id="pressure:runtime:latency-1",
        target_unit_refs=["unit:runtime:vulkan-pilot"],
        source_evidence_refs=["evidence:benchmark:run-1"],
        problem_class="latency",
        severity=0.8,
        recurrence=3,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.9,
        expected_value=0.85,
        research_budget_request=0.2,
        status="open",
    )
    assert genome.family == "runtime"
    assert pressure.recurrence == 3
```

- [ ] **Step 2: Run the tests and confirm the missing package failure**

Run: `python -m pytest tests/test_universal_evolution_contracts.py -q`

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'nexusnet.evolution'`.

- [ ] **Step 3: Implement the contracts and sanitizer**

Create `nexusnet/evolution/contracts.py` with frozen Pydantic models, the complete fields from sections 5 and 7 of the design, numeric fields constrained to `[0.0, 1.0]`, nonnegative recurrence, and these rules:

```python
EVOLUTION_SCHEMA_VERSION = "nexusnet-evolution-v1"

KNOWN_UNIT_KINDS = frozenset({
    "model", "expert", "router", "O", "AO", "memory-plane", "retriever",
    "harness", "prompt", "execution-contract", "workflow", "tool", "skill",
    "runtime", "inference-backend", "kernel", "compiler", "quantization-method",
    "cache-method", "scheduler", "evaluator", "policy", "federation-method",
    "improvement-service",
})

UNSAFE_REFERENCE_PATTERNS = (
    re.compile(r"^[A-Za-z]:[\\/]"),
    re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]+|bearer\s+\S+|begin private key)\b"),
    re.compile(r"[\r\n\x00]"),
)


def sanitize_reference(value: str) -> str:
    normalized = value.strip()
    if not normalized or any(pattern.search(normalized) for pattern in UNSAFE_REFERENCE_PATTERNS):
        raise ValueError("unsafe reference: raw, local, secret, or multiline material is forbidden")
    if len(normalized) > 512:
        raise ValueError("unsafe reference: maximum length is 512 characters")
    return normalized
```

Define `GenomeRef.family` as `Literal["model", "harness", "runtime", "organism"]`. Define `FoundationCheck.status` as `Literal["verified", "missing", "unverified"]`. Define lifecycle state as the exact state set from design section 8. Include all `EvolvableUnit` list fields with `default_factory=list`, plus `registration_schema_ref: str | None`, `rollback_refs: list[str]`, and `improvement_strategy_refs: list[str]`. Apply `sanitize_reference` to every `*_ref`, `*_refs`, identifier, and reference-like string through field validators.

Add a model-level validator:

```python
@model_validator(mode="after")
def validate_unknown_kind_contract(self) -> "EvolvableUnit":
    if self.unit_kind not in KNOWN_UNIT_KINDS:
        required = {
            "registration_schema_ref": self.registration_schema_ref,
            "eval_suite_refs": self.eval_suite_refs,
            "invariant_refs": self.invariant_refs,
            "rollback_refs": self.rollback_refs,
            "authority_class": self.authority_class,
            "privacy_class": self.privacy_class,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"unknown unit kind requires governed registration fields: {', '.join(missing)}")
    return self
```

Create `nexusnet/evolution/__init__.py` exporting only the public contracts initially.

- [ ] **Step 4: Run contract tests**

Run: `python -m pytest tests/test_universal_evolution_contracts.py -q`

Expected: PASS, `9 passed` (the parametrized privacy test contributes six cases).

- [ ] **Step 5: Commit the contract boundary**

Run:

```powershell
git add nexusnet/evolution/__init__.py nexusnet/evolution/contracts.py tests/test_universal_evolution_contracts.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Add universal evolution contracts"
```

Expected: no whitespace errors; GitNexus reports only the new evolution package/tests; commit succeeds.

### Task 2: Append-Only, Hash-Chained Everything State Events

**Files:**
- Create: `nexusnet/evolution/store.py`
- Test: `tests/test_universal_evolution_store.py`
- Modify: `nexusnet/evolution/__init__.py`

**Interfaces:**
- Consumes: `sanitize_reference` and Pydantic-serialized dictionaries.
- Produces: `EvolutionEventStore(root: Path)`, `append(event_type: str, payload: dict[str, Any]) -> dict[str, Any]`, `replay() -> list[dict[str, Any]]`, and `EvolutionIntegrityError`.

- [ ] **Step 1: Write failing persistence tests**

```python
# tests/test_universal_evolution_store.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from nexusnet.evolution.store import EvolutionEventStore, EvolutionIntegrityError


def test_events_restart_replay_with_hash_chain(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    first = store.append("unit.registered", {"unit_id": "unit:runtime:vulkan"})
    second = store.append("pressure.recorded", {"pressure_id": "pressure:latency:1"})
    restarted = EvolutionEventStore(tmp_path)
    replayed = restarted.replay()
    assert [event["sequence"] for event in replayed] == [1, 2]
    assert replayed[0]["previous_event_sha256"] is None
    assert replayed[1]["previous_event_sha256"] == first["event_sha256"]
    assert replayed[1]["event_sha256"] == second["event_sha256"]


def test_replay_fails_closed_when_event_is_modified(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    store.append("unit.registered", {"unit_id": "unit:runtime:vulkan"})
    path = tmp_path / "evolution" / "events.jsonl"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["payload"]["unit_id"] = "unit:runtime:tampered"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(EvolutionIntegrityError, match="hash mismatch"):
        EvolutionEventStore(tmp_path).replay()


def test_store_rejects_nested_private_material(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    with pytest.raises(ValueError, match="unsafe reference"):
        store.append("unit.registered", {"implementation_refs": ["C:/private/model.bin"]})
```

- [ ] **Step 2: Run and confirm missing store failure**

Run: `python -m pytest tests/test_universal_evolution_store.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'nexusnet.evolution.store'`.

- [ ] **Step 3: Implement durable event storage**

Implement `nexusnet/evolution/store.py` with canonical JSON (`sort_keys=True`, separators `(",", ":")`, UTF-8), recursive sanitization of values whose keys end in `_ref` or `_refs`, and event records shaped exactly as:

```python
{
    "schema_version": "nexusnet-evolution-event-v1",
    "sequence": sequence,
    "event_type": event_type,
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "previous_event_sha256": previous_hash,
    "payload_sha256": sha256(canonical_payload).hexdigest(),
    "payload": sanitized_payload,
    "event_sha256": sha256(canonical_record_without_event_hash).hexdigest(),
}
```

Use `self.path = root / "evolution" / "events.jsonl"`, create the parent directory, append one line with `open("a", encoding="utf-8", newline="\n")`, then `flush()` and `os.fsync()`. `append()` must call `replay()` first so corruption prevents new writes. `replay()` must verify contiguous sequence, previous hash, payload hash, and event hash; raise `EvolutionIntegrityError` at the first invalid record.

- [ ] **Step 4: Run persistence tests**

Run: `python -m pytest tests/test_universal_evolution_store.py -q`

Expected: PASS, `3 passed`.

- [ ] **Step 5: Export and commit the event store**

Add `EvolutionEventStore` and `EvolutionIntegrityError` to `nexusnet/evolution/__init__.py`, then run:

```powershell
git add nexusnet/evolution/__init__.py nexusnet/evolution/store.py tests/test_universal_evolution_store.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Add replayable Everything State event store"
```

Expected: focused new-symbol impact only; commit succeeds.

### Task 3: Evolvable Registry and Honest Legacy-Lane Adapter

**Files:**
- Create: `nexusnet/evolution/registry.py`
- Test: `tests/test_universal_evolution_service.py`
- Modify: `nexusnet/evolution/__init__.py`

**Interfaces:**
- Consumes: `EvolutionEventStore`, `EvolvableUnit`, `GenomeRef`, and an object exposing `.lanes: dict[str, Callable]` plus `.coverage() -> dict[str, Any]`.
- Produces: `EvolvableUnitRegistry`, `register_unit(unit)`, `register_genome(genome)`, `list_units()`, `list_genomes()`, `coverage()`, and `adapt_self_improvement_engine(engine)`.

- [ ] **Step 1: Add failing registry and compatibility tests**

Append to `tests/test_universal_evolution_service.py`:

```python
from pathlib import Path

from nexusnet.evolution.contracts import EvolvableUnit
from nexusnet.evolution.registry import EvolvableUnitRegistry
from nexusnet.evolution.store import EvolutionEventStore
from nexusnet.hive.self_improvement_engine import IMPROVABLE_ASPECTS, default_engine


def test_legacy_lanes_become_registry_units_without_claiming_universal_completion(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.adapt_self_improvement_engine(default_engine())
    coverage = registry.coverage()
    assert coverage["legacy_aspect_total"] == len(IMPROVABLE_ASPECTS)
    assert coverage["legacy_aspect_covered"] == len(IMPROVABLE_ASPECTS)
    assert coverage["legacy_taxonomy_fully_covered"] is True
    assert coverage["universal_coverage_complete"] is False
    assert coverage["claim_boundary"] == "legacy-lane-coverage-is-not-universal-organism-coverage"


def test_registered_uncovered_unit_is_reported_honestly(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.register_unit(EvolvableUnit(
        unit_id="unit:runtime:new-backend",
        unit_kind="runtime",
        owner_brain_ref="brain:NexusBrain",
        authority_class="mother-brain-governed",
        privacy_class="sanitized-metadata",
        license_state="reviewed",
        trust_state="quarantined",
        federation_policy="local-only",
        lifecycle_state="observed",
        eval_suite_refs=["eval:runtime-v1"],
        invariant_refs=["policy:north-star-v1"],
        checkpoint_refs=["checkpoint:baseline-v1"],
        rollback_refs=["checkpoint:baseline-v1"],
    ))
    coverage = registry.coverage()
    assert coverage["uncovered_unit_refs"] == ["unit:runtime:new-backend"]


def test_registry_replays_units_after_restart(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    first = EvolvableUnitRegistry(store)
    first.adapt_self_improvement_engine(default_engine())
    restarted = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    assert len(restarted.list_units()) == len(IMPROVABLE_ASPECTS)
```

- [ ] **Step 2: Verify the registry tests fail**

Run: `python -m pytest tests/test_universal_evolution_service.py -q`

Expected: FAIL with missing `nexusnet.evolution.registry`.

- [ ] **Step 3: Implement registry replay and adapter**

Implement `EvolvableUnitRegistry` with dictionaries keyed by `unit_id` and `genome_id`. Constructor replays `unit.registered` and `genome.registered`. Registration is idempotent only when the serialized record is identical; conflicting reuse raises `ValueError("conflicting evolution identity")`.

For each existing lane, the adapter registers:

```python
EvolvableUnit(
    unit_id=f"unit:self-improvement:{aspect}",
    unit_kind="improvement-service",
    owner_brain_ref="brain:NexusBrain",
    capability_refs=[f"capability:self-improvement:{aspect}"],
    implementation_refs=[f"implementation:self-improvement-lane:{aspect}"],
    authority_class="mother-brain-governed",
    privacy_class="sanitized-metadata",
    license_state="repository-governed",
    trust_state="existing-compatibility-lane",
    eval_suite_refs=["eval:self-improvement-coverage-v1"],
    invariant_refs=["policy:north-star-v1", "policy:governed-autonomy-v1"],
    checkpoint_refs=["checkpoint:production-before-self-improvement-v1"],
    rollback_refs=["checkpoint:production-before-self-improvement-v1"],
    improvement_strategy_refs=[f"strategy:legacy-lane:{aspect}"],
    federation_policy="sanitized-evidence-only",
    lifecycle_state="active",
)
```

`coverage()` counts a unit as covered only when `improvement_strategy_refs`, `eval_suite_refs`, `invariant_refs`, and `rollback_refs` are all nonempty. Set `universal_coverage_complete` to true only when at least one non-legacy organism unit is registered and every registered unit is covered; do not derive it from the static tuple alone.

- [ ] **Step 4: Run registry and existing compute-lane tests**

Run:

```powershell
python -m pytest tests/test_universal_evolution_service.py tests/test_hive_self_improvement_engine.py -q
```

Expected: new registry tests pass and all existing self-improvement engine tests remain unchanged. If Torch is absent, the existing file may skip; record that fact rather than reporting it as a pass.

- [ ] **Step 5: Commit the compatibility adapter**

```powershell
git add nexusnet/evolution/__init__.py nexusnet/evolution/registry.py tests/test_universal_evolution_service.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Bridge self improvement into evolvable registry"
```

Expected: no edit to `nexusnet/hive/self_improvement_engine.py`; commit succeeds.

### Task 4: Growth Pressure and Foundation Verification

**Files:**
- Create: `nexusnet/evolution/pressure.py`
- Create: `nexusnet/evolution/foundation.py`
- Modify: `tests/test_universal_evolution_service.py`
- Modify: `nexusnet/evolution/__init__.py`

**Interfaces:**
- Consumes: `EvolutionEventStore`, `GrowthPressure`, and prerequisite evidence mappings.
- Produces: `GrowthPressureMap.record()`, `.ranked()`, `.summary()`, `FoundationVerifier.verify() -> list[FoundationCheck]`.

- [ ] **Step 1: Add failing pressure and prerequisite tests**

Append tests proving:

```python
from nexusnet.evolution.contracts import GrowthPressure
from nexusnet.evolution.foundation import FoundationVerifier
from nexusnet.evolution.pressure import GrowthPressureMap


def test_pressure_ranking_respects_value_priority_and_health_limits(tmp_path: Path):
    pressure_map = GrowthPressureMap(EvolutionEventStore(tmp_path))
    pressure_map.record(GrowthPressure(
        pressure_id="pressure:latency:1", target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:1"], problem_class="latency",
        severity=0.8, recurrence=4, quality_risk=0.1, safety_risk=0.0,
        opportunity_score=0.9, expected_value=0.9, research_budget_request=0.3,
        affected_workloads=["workload:interactive"], status="open",
    ))
    pressure_map.record(GrowthPressure(
        pressure_id="pressure:safety:1", target_unit_refs=["unit:model:a"],
        source_evidence_refs=["evidence:eval:2"], problem_class="safety",
        severity=1.0, recurrence=1, quality_risk=0.8, safety_risk=1.0,
        opportunity_score=1.0, expected_value=1.0, research_budget_request=1.0,
        affected_workloads=["workload:protected"], status="open",
    ))
    ranked = pressure_map.ranked(
        workload_priority={"workload:interactive": 1.0, "workload:protected": 1.0},
        system_health_limit=0.5,
    )
    assert ranked[0]["pressure_id"] == "pressure:latency:1"
    assert ranked[1]["blocked_reason"] == "safety-or-quality-risk-exceeds-system-health-limit"


def test_foundation_verifier_labels_unknowns_instead_of_inventing_proof():
    checks = FoundationVerifier({
        "mother_brain_authority": "evidence:brain:identity",
        "governance": "evidence:governance:service",
    }).verify()
    by_name = {check.prerequisite: check for check in checks}
    assert by_name["mother_brain_authority"].status == "verified"
    assert by_name["neural_bus"].status == "unverified"
    assert by_name["hive_blackboard"].status == "unverified"
```

- [ ] **Step 2: Run and verify missing module failures**

Run: `python -m pytest tests/test_universal_evolution_service.py -q`

Expected: FAIL importing `nexusnet.evolution.foundation` or `.pressure`.

- [ ] **Step 3: Implement deterministic pressure scoring**

Persist `pressure.recorded` events and replay them. For each open pressure compute:

```python
recurrence_score = min(1.0, pressure.recurrence / 10.0)
workload_score = max((workload_priority.get(ref, 0.5) for ref in pressure.affected_workloads), default=0.5)
priority_score = round(
    0.25 * pressure.severity
    + 0.15 * recurrence_score
    + 0.20 * pressure.opportunity_score
    + 0.20 * pressure.expected_value
    + 0.20 * workload_score,
    6,
)
blocked = max(pressure.quality_risk, pressure.safety_risk) > system_health_limit
```

Sort unblocked before blocked, then descending `priority_score`, then `pressure_id`. A blocked item remains visible and cannot receive an executable research budget.

- [ ] **Step 4: Implement honest prerequisite checks**

`FoundationVerifier` must enumerate exactly: `canon`, `mother_brain_authority`, `isolation`, `neural_bus`, `hive_blackboard`, `evidence`, `checkpoint`, `replay`, `governance`, and `rollback`. Nonempty sanitized evidence refs are `verified`; explicit `None` is `missing`; absent keys are `unverified`. Return a `FoundationCheck` with a claim boundary explaining that presence of a reference is not semantic proof of the subsystem.

- [ ] **Step 5: Run the focused tests and commit**

```powershell
python -m pytest tests/test_universal_evolution_service.py tests/test_universal_evolution_store.py -q
git add nexusnet/evolution/__init__.py nexusnet/evolution/pressure.py nexusnet/evolution/foundation.py tests/test_universal_evolution_service.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Add growth pressure and foundation verification"
```

Expected: all focused tests pass; commit contains no existing production-symbol edits.

### Task 5: NexusBrain-Owned Evolution Service and Everything State Projection

**Files:**
- Create: `nexusnet/evolution/service.py`
- Modify: `nexusnet/evolution/__init__.py`
- Modify: `tests/test_universal_evolution_service.py`

**Interfaces:**
- Consumes: `artifacts_dir: Path`, `owner_brain_ref: str`, `prerequisite_evidence: dict[str, str | None]`, registry, pressure map, and `default_engine()` passed by the composition root.
- Produces: `UniversalEvolutionService`, `.everything_state()`, `.evolvable_units()`, `.growth_pressure()`, `.status()`, `.register_unit()`, and `.record_pressure()`.

- [ ] **Step 1: Write a failing restart-and-status test**

```python
from nexusnet.evolution.service import UniversalEvolutionService
from nexusnet.hive.self_improvement_engine import default_engine


def test_service_projects_sanitized_restart_replayable_everything_state(tmp_path: Path):
    service = UniversalEvolutionService(
        artifacts_dir=tmp_path,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={"mother_brain_authority": "evidence:brain:identity"},
        legacy_engine=default_engine(),
    )
    first = service.everything_state()
    restarted = UniversalEvolutionService(
        artifacts_dir=tmp_path,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={"mother_brain_authority": "evidence:brain:identity"},
        legacy_engine=default_engine(),
    )
    second = restarted.everything_state()
    assert first["content_sha256"] == second["content_sha256"]
    assert second["authority"] == "NexusBrain"
    assert second["coverage"]["universal_coverage_complete"] is False
    assert "ChrisBoyd" not in str(second)
```

- [ ] **Step 2: Confirm failure before implementation**

Run: `python -m pytest tests/test_universal_evolution_service.py -q`

Expected: FAIL importing `UniversalEvolutionService`.

- [ ] **Step 3: Implement the facade**

Construct one store, registry, pressure map, and verifier. Adapt the legacy engine idempotently. `everything_state()` must return only serialized units, genomes, open pressures, prerequisite checks, coverage, event count, last event hash, `authority: "NexusBrain"`, and a content hash computed over the canonical payload excluding `content_sha256`. Include:

```python
"claim_boundary": (
    "registry-and-evidence-state-only; no candidate, experiment, promotion, "
    "native-model-birth, or frontier-superiority claim"
)
```

`status()` must be a compact projection with counts, coverage, top five pressures, missing/unverified prerequisites, last event hash, and endpoint refs. It must not include raw event payloads.

- [ ] **Step 4: Run the complete evolution unit suite**

Run: `python -m pytest tests/test_universal_evolution_contracts.py tests/test_universal_evolution_store.py tests/test_universal_evolution_service.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the service facade**

```powershell
git add nexusnet/evolution/__init__.py nexusnet/evolution/service.py tests/test_universal_evolution_service.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Add NexusBrain evolution service"
```

Expected: additive evolution-package scope only.

### Task 6: Service Composition and Read-Only API Surfaces

**Files:**
- Modify: `nexus/services.py` at `NexusServices` and `build_services`
- Modify: `nexus/api/app.py` at `create_app`, the canon self-improvement coverage route, and wrapper status route
- Create: `tests/test_universal_evolution_api.py`
- Modify: `tests/test_self_improvement_coverage_endpoint.py`

**Interfaces:**
- Consumes: `UniversalEvolutionService` and `default_engine()`.
- Produces: `services.brain_evolution` and GET routes `/ops/brain/evolution/everything-state`, `/ops/brain/evolution/evolvable-units`, `/ops/brain/evolution/growth-pressure`, `/ops/brain/evolution/status`.

- [ ] **Step 1: Rerun mandatory impact gates before existing-symbol edits**

Run GitNexus upstream impact for `NexusServices`, `build_services`, and `create_app`, plus API impact for `/ops/brain/canon/self-improvement-coverage` and `/ops/wrapper/status-card`.

Expected: record direct callers, affected flows, and risk. Stop and warn the user before editing if any result is HIGH or CRITICAL. Do not edit `SelfImprovementEngine` or `default_engine`.

- [ ] **Step 2: Write failing black-box API tests**

```python
# tests/test_universal_evolution_api.py
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_evolution_endpoints_are_nexusbrain_owned_and_read_only(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    state = client.get("/ops/brain/evolution/everything-state")
    units = client.get("/ops/brain/evolution/evolvable-units")
    pressure = client.get("/ops/brain/evolution/growth-pressure")
    status = client.get("/ops/brain/evolution/status")
    assert [response.status_code for response in (state, units, pressure, status)] == [200, 200, 200, 200]
    assert state.json()["authority"] == "NexusBrain"
    assert units.json()["coverage"]["legacy_taxonomy_fully_covered"] is True
    assert units.json()["coverage"]["universal_coverage_complete"] is False
    assert pressure.json()["items"] == []
    assert status.json()["mutation_boundary"] == "read-only-no-protected-state-mutation"


def test_wrapper_status_projects_sanitized_evolution_without_session_identifier(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    card = client.get("/ops/wrapper/status-card", params={"session_id": "private-user-123"}).json()
    assert card["evolution"]["authority"] == "NexusBrain"
    assert card["evolution"]["coverage"]["universal_coverage_complete"] is False
    assert "private-user-123" not in str(card["evolution"])
```

Extend the legacy endpoint test with:

```python
assert payload["legacy_taxonomy_fully_covered"] is True
assert payload["universal_coverage_complete"] is False
assert payload["claim_boundary"] == "legacy-lane-coverage-is-not-universal-organism-coverage"
```

- [ ] **Step 3: Run tests and confirm missing service/route failure**

Run: `python -m pytest tests/test_universal_evolution_api.py tests/test_self_improvement_coverage_endpoint.py -q`

Expected: FAIL because `brain_evolution` and the new routes do not exist.

- [ ] **Step 4: Wire the service once under NexusServices**

Add `brain_evolution: UniversalEvolutionService` to the dataclass. Construct it once in `build_services` using `paths.artifacts_dir`, `brain:NexusBrain`, `default_engine()`, and only evidence refs that existing runtime construction can actually substantiate. Leave Neural Bus and HiveBlackboard absent if no current runtime evidence adapter exists. Pass `brain_evolution=brain_evolution` in the final `NexusServices(...)` construction.

- [ ] **Step 5: Add the read-only endpoints and compatibility projection**

Route bodies must be direct projections:

```python
@application.get("/ops/brain/evolution/everything-state")
def ops_brain_evolution_everything_state():
    return services.brain_evolution.everything_state()

@application.get("/ops/brain/evolution/evolvable-units")
def ops_brain_evolution_evolvable_units():
    return services.brain_evolution.evolvable_units()

@application.get("/ops/brain/evolution/growth-pressure")
def ops_brain_evolution_growth_pressure():
    return services.brain_evolution.growth_pressure()

@application.get("/ops/brain/evolution/status")
def ops_brain_evolution_status():
    return services.brain_evolution.status()
```

Preserve all existing legacy coverage keys while adding the registry coverage fields. In `ops_wrapper_status_card`, copy the returned card and add `card["evolution"] = services.brain_evolution.status()`; do not modify `ReleaseWrapperRuntime.status_card` in this slice.

- [ ] **Step 6: Run API compatibility tests**

Run:

```powershell
python -m pytest tests/test_universal_evolution_api.py tests/test_self_improvement_coverage_endpoint.py tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q
```

Expected: all focused tests pass; previous response keys remain intact; evolution status contains no raw session identifier.

- [ ] **Step 7: Commit service and API wiring**

```powershell
git add nexus/services.py nexus/api/app.py tests/test_universal_evolution_api.py tests/test_self_improvement_coverage_endpoint.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Expose universal evolution runtime state"
```

Expected: GitNexus reports only service composition and the intended API flows. If broad unrelated symbols appear, unstage and narrow the patch before committing.

### Task 7: Release Harness and Control Panel Evolution Projection

**Files:**
- Modify: `ui/control-panel/app.js` near release-wrapper state/rendering
- Modify: `tests/test_release_wrapper_runtime.py`

**Interfaces:**
- Consumes: `statusCard.evolution` from Task 6.
- Produces: a sanitized Universal Evolution card showing authority, registered/covered/uncovered counts, top growth pressure, prerequisite gaps, event hash, and explicit claim boundary.

- [ ] **Step 1: Run UI-symbol impact analysis before editing**

Use GitNexus context/impact on `renderReleaseWrapperStatusFallback` and the primary release-wrapper rendering function discovered at execution time. Record direct callers and affected UI/API flows. Stop and warn on HIGH or CRITICAL risk.

- [ ] **Step 2: Add a failing control-panel source assertion**

Append to the existing release-wrapper control-panel test:

```python
control_panel_js = (Path(__file__).parents[1] / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
assert "Universal Evolution" in control_panel_js
assert "legacy-lane-coverage-is-not-universal-organism-coverage" in control_panel_js
assert "universal_coverage_complete" in control_panel_js
assert "evolution-prerequisite-gaps" in control_panel_js
```

- [ ] **Step 3: Run and verify the red assertion**

Run: `python -m pytest tests/test_release_wrapper_runtime.py::test_release_readiness_runner_drives_governed_evidence_path -q`

Expected: FAIL because `Universal Evolution` is absent.

- [ ] **Step 4: Render a compact read-only card**

Read `const evolution = state.releaseWrapperStatus?.evolution || {};` in the existing release rendering path. Render escaped values only. The card must include CSS class `evolution-prerequisite-gaps`, display `NexusBrain` authority, `registered_unit_count`, `covered_unit_count`, `uncovered_unit_count`, top pressure count/ID, missing/unverified prerequisites, and the fixed visible sentence `legacy-lane-coverage-is-not-universal-organism-coverage`. Do not add mutation buttons or claim that universal coverage is complete.

- [ ] **Step 5: Run UI and API projection tests**

Run:

```powershell
python -m pytest tests/test_universal_evolution_api.py tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart tests/test_release_wrapper_runtime.py::test_release_readiness_runner_drives_governed_evidence_path -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit the visible projection**

```powershell
git add ui/control-panel/app.js tests/test_release_wrapper_runtime.py
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Show universal evolution status in control panel"
```

Expected: only the intended control-panel rendering/test symbols are affected.

### Task 8: End-to-End Verification and Program-A/B Evidence Record

**Files:**
- Create: `docs/evidence/universal-evolution-foundation.md`
- Test: all focused files from Tasks 1–7

**Interfaces:**
- Consumes: completed foundation implementation and current test output.
- Produces: an evidence record that distinguishes verified behavior, skips, unverified prerequisites, and Programs C–I.

- [ ] **Step 1: Run the full focused verification matrix**

```powershell
python -m pytest tests/test_universal_evolution_contracts.py tests/test_universal_evolution_store.py tests/test_universal_evolution_service.py tests/test_universal_evolution_api.py tests/test_self_improvement_coverage_endpoint.py tests/test_hive_self_improvement_engine.py tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q
```

Expected: all available tests pass. Record exact pass/skip/fail counts; a Torch-related skip is a skip, not a pass.

- [ ] **Step 2: Run restart and privacy smoke checks**

Run the API restart test twice against the same temporary project and inspect `artifacts/evolution/events.jsonl` only for schema version, sequence, hashes, event types, and sanitized refs.

Expected: identical Everything State content hash across restart; no absolute user path, prompt/output body, bearer token, private key marker, or session identifier.

- [ ] **Step 3: Run repository quality gates**

```powershell
git diff --check
python -m compileall -q nexusnet/evolution
npx gitnexus detect-changes --scope all --repo NexusNet
```

Expected: no whitespace or compile errors. GitNexus may report the pre-existing dirty tree; separate this slice's symbols and flows explicitly from unrelated user changes.

- [ ] **Step 4: Write the evidence record with exact observed results**

Create `docs/evidence/universal-evolution-foundation.md` containing:

- commit IDs for Tasks 1–7;
- exact test commands and pass/skip/fail counts;
- event-log restart/hash-chain evidence;
- privacy scan result;
- verified, missing, and unverified Program-A prerequisites;
- legacy taxonomy coverage versus universal registry coverage;
- GitNexus impact/risk results;
- explicit statement that Programs C–I, novel inference synthesis, Native MoE birth, federation, and Hugging Face publication are not implemented by this slice.

- [ ] **Step 5: Commit the evidence record**

```powershell
git add docs/evidence/universal-evolution-foundation.md
git diff --cached --check
npx gitnexus detect-changes --scope staged --repo NexusNet
git commit -m "Record universal evolution foundation evidence"
```

Expected: documentation-only staged impact and successful commit.

## Completion Gate

This plan is complete only when all of the following are evidenced:

- versioned contracts accept known types and fail closed for ungoverned unknown types;
- unsafe/private references are rejected recursively;
- Everything State events survive restart and detect tampering;
- every current legacy self-improvement lane is represented without editing `SelfImprovementEngine`;
- the system explicitly reports that legacy completeness is not universal completeness;
- Growth Pressure is persisted, ranked deterministically, and blocked by safety/quality health limits;
- foundation prerequisites can remain honestly `missing` or `unverified`;
- one NexusBrain-owned evolution service is reachable through runtime APIs;
- wrapper and Control Panel show sanitized evolution status without mutation controls;
- focused tests, compile checks, `git diff --check`, and GitNexus scope review pass;
- the evidence record makes no claim that candidate synthesis, frontier inference, Native MoE birth, federation, or Hugging Face publication exists yet.

## Ordered Follow-On Plans

After this foundation is verified, write and approve separate plans in this order:

1. Program C — candidate, experiment, negative-knowledge, ablation, and Pareto graph.
2. Program D — inference/runtime assimilation pilot with reproduced baselines and one NexusNet-synthesized candidate.
3. Program E — harness/model/runtime co-evolution and subtraction ablations.
4. Program F — rights-safe Native MoE growth, teacher-free evaluation, and birth dossiers.
5. Program G — sanitized fractal federation and reproduction-before-promotion.
6. Program H — private Hugging Face validation and separately authorized publication.
7. Program I — continuous frontier monitoring and successor-cycle reopening.

Each follow-on plan must inherit the North-Star Constitutional Intent, mother-brain authority, evidence gates, privacy, provenance, rollback, and honest claim boundaries from the approved design specification.
