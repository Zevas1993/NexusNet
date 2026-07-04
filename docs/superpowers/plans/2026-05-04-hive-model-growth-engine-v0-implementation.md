# Hive Model Growth Engine v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first replayable, dry-run Hive Model Growth Engine that can birth a shadow child Expert from machine-readable artifact contracts without real weight mutation or teacher ejection.

**Architecture:** Add a new `nexusnet.growth` package with Pydantic contracts, a repo-local append-only artifact store, and a dry-run engine that writes a complete growth cycle directory. The engine will produce cycle, source, curriculum, teacher council, dataset, student genome, training plan, eval scorecard, reviewer decision, and rollback artifacts with stable refs and hashable JSON/YAML outputs.

**Tech Stack:** Python, Pydantic v2, JSON/JSONL/YAML artifacts, pytest, existing NexusNet project-local artifact patterns.

---

### Task 1: Failing Tests For Dry-Run Growth Lifecycle

**Files:**
- Create: `tests/test_hive_model_growth_engine.py`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import json

from nexusnet.growth import GrowthCycleRequest, HiveModelGrowthEngine


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_growth_engine_dry_run_writes_replayable_cycle_contracts(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)

    result = engine.start_dry_run(
        GrowthCycleRequest(
            cycle_id="cycle:cyc_demo_001",
            target_node_id="node:expert_coder",
            target_node_type="Expert",
            target_capabilities=["multi_file_patch", "test_repair", "terminal_recovery"],
            student_kind="child_expert",
            birth_reason="Repeated failures on multi-file repair tasks.",
            teacher_pairing_refs=[
                "teacher:qwen3-coder-next",
                "teacher:devstral-2",
                "node:expert_critique",
            ],
            source_refs=["source:licensed_synthetic_code_cases"],
        )
    )

    assert result["surface_id"] == "hive-model-growth-engine"
    assert result["cycle_id"] == "cycle:cyc_demo_001"
    assert result["state"] == "shadow_specialist"
    assert result["actual_weight_mutation_allowed"] is False
    assert result["teacher_ejection_eligible"] is False

    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_demo_001"
    assert (cycle_dir / "cycle.json").is_file()
    assert (cycle_dir / "events.jsonl").is_file()
    assert (cycle_dir / "datasets" / "dataset_manifest.json").is_file()
    assert (cycle_dir / "datasets" / "teacher_free_hidden.manifest.json").is_file()
    assert (cycle_dir / "students" / "model_genome.yaml").is_file()
    assert (cycle_dir / "training-runs" / "train_demo_001" / "training_run.json").is_file()
    assert (cycle_dir / "evals" / "eval_demo_001" / "scorecard.json").is_file()
    assert (cycle_dir / "reviewer-monitor" / "decision.json").is_file()
    assert (cycle_dir / "rollbacks" / "rewind_proof.json").is_file()

    cycle = _read_json(cycle_dir / "cycle.json")
    assert cycle["schema_version"] == "growth_cycle.v0.1"
    assert cycle["header"]["artifact_type"] == "growth_cycle"
    assert cycle["header"]["hash"].startswith("sha256:")
    assert cycle["state_refs"]["dataset_manifest_ref"] == "dataset:ds_demo_001"
    assert cycle["governance"]["human_approval_required"] is True

    hidden = _read_json(cycle_dir / "datasets" / "teacher_free_hidden.manifest.json")
    assert hidden["sealed"] is True
    assert hidden["visible_to_training"] is False
    assert hidden["visible_to_teacher_council"] is False
    assert hidden["leakage_scan"]["status"] == "passed"

    training = _read_json(cycle_dir / "training-runs" / "train_demo_001" / "training_run.json")
    assert training["support_state"] == "dry_run_supported"
    assert training["actual_weight_mutation_allowed"] is False
    assert "qlora" in training["declared_methods"]

    reviewer = _read_json(cycle_dir / "reviewer-monitor" / "decision.json")
    assert reviewer["decision"] == "shadow_specialist"
    assert reviewer["parent_comparison"]["passed"] is True
    assert reviewer["teacher_comparison"]["passed"] is False
    assert reviewer["teacher_ejection_eligible"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: FAIL because `nexusnet.growth` does not exist.

### Task 2: Growth Contracts

**Files:**
- Create: `nexusnet/growth/__init__.py`
- Create: `nexusnet/growth/contracts.py`

- [ ] **Step 1: Implement Pydantic contracts**

Define `GrowthCycleRequest`, artifact enum literals, and structured models for cycle records, dataset manifests, training runs, eval scorecards, reviewer decisions, and rollback snapshots. All contracts use `ConfigDict(extra="forbid")` to prevent loose fields.

- [ ] **Step 2: Run targeted tests**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: FAIL because `HiveModelGrowthEngine` is not implemented yet.

### Task 3: Artifact Store

**Files:**
- Create: `nexusnet/growth/artifacts.py`

- [ ] **Step 1: Implement repo-local artifact writer**

Implement `GrowthArtifactStore` with JSON, JSONL, YAML writing, artifact hash calculation, stable path sanitization, cycle directory creation, and registry index append.

- [ ] **Step 2: Run targeted tests**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: FAIL because the engine has not produced the lifecycle files yet.

### Task 4: Dry-Run Engine

**Files:**
- Create: `nexusnet/growth/engine.py`
- Modify: `nexusnet/growth/__init__.py`

- [ ] **Step 1: Implement `HiveModelGrowthEngine.start_dry_run()`**

Create the complete cycle directory with required artifacts:

```text
cycle.json
events.jsonl
material-scout/scout_manifest.json
curriculum/curriculum.yaml
teacher-council/council_manifest.json
datasets/dataset_manifest.json
datasets/train.jsonl
datasets/validation.jsonl
datasets/heldout.jsonl
datasets/adversarial.jsonl
datasets/teacher_free_hidden.manifest.json
students/student_birth_record.json
students/model_genome.yaml
training-runs/train_demo_001/training_run.json
training-runs/train_demo_001/loss_trace.jsonl
evals/eval_demo_001/scorecard.json
evals/eval_demo_001/comparison_matrix.json
evals/eval_demo_001/case_results.jsonl
reviewer-monitor/decision.json
rollbacks/rollback_snapshot.json
rollbacks/rewind_proof.json
```

- [ ] **Step 2: Run targeted tests**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: PASS.

### Task 5: Summary And Scorecard

**Files:**
- Modify: `tests/test_hive_model_growth_engine.py`
- Modify: `nexusnet/growth/engine.py`

- [ ] **Step 1: Add failing tests for summary and scorecard**

Assert that `summary()` reports cycle counts and latest lifecycle state, and `scorecard()` reports required controls, dry-run boundary, and operator action names.

- [ ] **Step 2: Implement summary and scorecard**

Add methods that read persisted `cycle.json` files and return control-panel-ready payloads without requiring API integration.

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: PASS.

### Task 6: Optional API And UI Wiring

**Files:**
- Potentially modify: `nexus/services.py`
- Potentially modify: `nexus/api/app.py`
- Potentially modify: `nexusnet/visuals/layout.py`
- Potentially modify: `ui/control-panel/app.js`
- Potentially modify: `tests/test_hive_model_growth_engine.py`

- [ ] **Step 1: Run GitNexus impact checks before modifying existing symbols**

Use `gitnexus_impact` for every existing function or method touched. If any target returns HIGH or CRITICAL risk, warn the user before editing.

- [ ] **Step 2: Add API/control-panel tests first**

Add blackbox tests for `/ops/brain/growth-engine`, `/ops/brain/growth-engine/cycles`, and `/ops/brain/canon/growth-engine`.

- [ ] **Step 3: Implement API and visualizer wiring**

Wire the engine into services and expose scorecard/state to the control panel only after tests fail for missing endpoints.

- [ ] **Step 4: Run targeted tests**

Run: `pytest tests/test_hive_model_growth_engine.py -q`

Expected: PASS.

### Task 7: Verification

**Files:**
- All files touched by this plan.

- [ ] **Step 1: Run targeted tests**

Run: `pytest tests/test_hive_model_growth_engine.py tests/test_dataset_forge.py tests/test_adapter_training_planner.py -q`

Expected: PASS.

- [ ] **Step 2: Run formatting/checksum sanity**

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 3: Review dirty tree**

Run: `git status --short`

Expected: only intended new growth files plus prior unrelated dirty files remain.
