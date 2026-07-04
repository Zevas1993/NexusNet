# Video Assimilation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn all ten 2026-05-06 video assimilation specs into live NexusNet control-plane surfaces with source-status gates, eval receipts, action permissions, and Control Panel visibility.

**Architecture:** Implement this as additive NexusNet surfaces rather than direct imports from external projects. Governance and source-truth gates land first, then retrieval/self-improvement/eval/operator/runtime/telemetry lanes bind into existing APIs and Control Panel scorecards. Every new lane remains refs-only or shadow-only until tests prove provenance, policy, rollback, and operator-approval behavior.

**Tech Stack:** Python 3.13, FastAPI, Pydantic, pytest, existing NexusNet service registry, existing static Control Panel HTML/CSS/JS.

---

## Scope And Decomposition

The ten specs cover independent subsystems, so execute this as ten small implementation tasks. Do not mix tasks in one patch unless the later task only wires together already-tested surfaces.

Spec coverage:

- `01-frontier-small-model-training-spec.md`: Task 6.
- `02-jarvis-operator-shell-spec.md`: Tasks 5 and 9.
- `03-space-agent-self-updating-surface-spec.md`: Task 4.
- `04-agentic-rag-planner-spec.md`: Task 3.
- `05-gitnexus-codegraph-gate-spec.md`: Task 8.
- `06-synthetic-truth-guard-spec.md`: Task 2.
- `07-black-box-interpretability-plane-spec.md`: Task 7.
- `08-darwin-godel-machine-lineage-spec.md`: Task 4.
- `09-alphaevolve-verifier-search-spec.md`: Task 4.
- `10-tars-computer-use-operator-spec.md`: Task 5.

GitNexus rule:

- Before modifying an existing function, class, or method, run GitNexus impact for that symbol and record the risk in the task notes.
- If impact is HIGH or CRITICAL, pause implementation and ask for a review checkpoint.
- Before any commit, run `gitnexus_detect_changes` or the GitNexus MCP `detect_changes` equivalent for this repo.

Dirty-tree rule:

- Stage only files touched by the current task.
- Do not stage unrelated existing dirty files.

## File Structure

Create or modify these files.

Core governance and target ledger:

- Modify: `nexusnet/operations/assimilation_targets.py`
- Create: `nexusnet/operations/codegraph_gate.py`
- Modify: `nexusnet/operations/__init__.py`
- Modify: `nexusnet/policy/kernel.py`
- Modify: `nexusnet/memory/quality_ledger.py`

Retrieval, self-improvement, and eval search:

- Create: `nexusnet/retrieval/planner.py`
- Modify: `nexusnet/retrieval/__init__.py`
- Create: `nexusnet/core/self_improvement/lineage.py`
- Modify: `nexusnet/core/self_improvement/__init__.py`
- Create: `nexusnet/evals/verifier_search.py`
- Modify: `nexusnet/evals/__init__.py`

Operator, browser, runtime, and telemetry:

- Create: `nexusnet/browser/profile_policy.py`
- Modify: `nexusnet/browser/__init__.py`
- Create: `nexusnet/vision/operator_events.py`
- Modify: `nexusnet/vision/__init__.py`
- Create: `nexusnet/runtime/model_passport.py`
- Modify: `nexusnet/runtime/__init__.py`
- Create: `nexusnet/telemetry/concept_plane.py`
- Modify: `nexusnet/telemetry/__init__.py`

API and service registry:

- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`

Control Panel:

- Modify: `ui/control-panel/index.html`
- Modify: `ui/control-panel/app.js`
- Modify: `ui/control-panel/styles.css`

Tests:

- Create: `tests/test_video_assimilation_targets.py`
- Create: `tests/test_synthetic_truth_guard.py`
- Create: `tests/test_retrieval_planner.py`
- Create: `tests/test_assimilation_lineage_verifier_search.py`
- Create: `tests/test_operator_permission_events.py`
- Create: `tests/test_edge_model_certification.py`
- Create: `tests/test_concept_telemetry_plane.py`
- Create: `tests/test_codegraph_gate.py`
- Create: `tests/test_video_assimilation_control_panel.py`

Documentation:

- Create: `docs/autonomous/TASK_SCOPE_2026_VIDEO_ASSIMILATION_IMPLEMENTATION.md`
- Create: `docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md`

---

### Task 0: Baseline Gate And Worktree Hygiene

**Files:**
- Read: `docs/assimilation/videos/2026-05-06/README.md`
- Read: `AGENTS.md`
- Create: `docs/autonomous/TASK_SCOPE_2026_VIDEO_ASSIMILATION_IMPLEMENTATION.md`
- Create: `docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md`

- [ ] **Step 1: Verify current repo state**

Run:

```powershell
git status --short
git branch --show-current
```

Expected: a dirty tree is allowed. Note unrelated dirty files in the run log and do not stage them.

- [ ] **Step 2: Confirm the assimilation packet exists**

Run:

```powershell
Get-ChildItem -LiteralPath 'docs/assimilation/videos/2026-05-06' -Filter '*.md' | Sort-Object Name | Select-Object -ExpandProperty Name
```

Expected: `01-...` through `10-...`, `README.md`, and `NEXT_WATCH_AND_SOURCE_CANDIDATES.md`.

- [ ] **Step 3: Create the scope document**

Create `docs/autonomous/TASK_SCOPE_2026_VIDEO_ASSIMILATION_IMPLEMENTATION.md` with:

```markdown
# Video Assimilation Implementation Scope - 2026-05-06

Scope: implement live NexusNet control-plane surfaces for the ten video assimilation specs under `docs/assimilation/videos/2026-05-06`.

Boundaries:

- External projects are source references only; no copied Mark XXXIX, DGM, AlphaEvolve, TARS, Space Agent, or other external implementation code.
- Self-improvement, verifier search, generated modules, browser actions, desktop actions, and model certification remain shadow or refs-only until policy, eval, rollback, and operator approval gates pass.
- Private browser, screen, file, memory, and workstation context remains local and permissioned.
- Codegraph evidence is required before code-affecting work.
- Every new surface needs API visibility, Control Panel visibility, and targeted tests.

Primary implementation sequence:

1. Video assimilation target ledger.
2. Synthetic truth guard.
3. Retrieval planner.
4. Self-improvement lineage and verifier search.
5. Operator permission/event stream.
6. Edge model passport and certification.
7. Concept telemetry plane.
8. Codegraph gate.
9. API and Control Panel integration.
10. End-to-end verification.
```

- [ ] **Step 4: Create the run log**

Create `docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md` with:

```markdown
# Video Assimilation Run Log

## 2026-05-06

Started implementation from `docs/superpowers/plans/2026-05-06-video-assimilation-implementation.md`.

Dirty tree note: unrelated existing changes must remain untouched and unstaged unless this lane explicitly modifies the file.
```

- [ ] **Step 5: Run the initial doc safety scan**

Run:

```powershell
$patterns = @("[A-Za-z]:\\\\", "uri-scheme-file", "placeholder-token", "deferred-detail")
foreach ($pattern in $patterns) {
  rg -n $pattern docs/assimilation docs/superpowers/plans docs/autonomous
}
```

Expected: no matches from files created in this task.

- [ ] **Step 6: Commit this task only**

Run:

```powershell
git add docs/autonomous/TASK_SCOPE_2026_VIDEO_ASSIMILATION_IMPLEMENTATION.md docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md
git commit -m "docs: add video assimilation implementation scope"
```

Expected: commit succeeds with only the two scope/log files staged.

---

### Task 1: Video Assimilation Target Ledger

**Files:**
- Modify: `nexusnet/operations/assimilation_targets.py`
- Create: `tests/test_video_assimilation_targets.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `AssimilationTargetRegistry` in `nexusnet/operations/assimilation_targets.py`.

Expected: risk is LOW or MEDIUM because this task extends scorecard payloads and tests existing API behavior.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_video_assimilation_targets.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.assimilation_targets import AssimilationTargetRegistry
from tests.test_nexus_phase1_foundation import make_project


EXPECTED_VIDEO_TARGET_IDS = {
    "frontier-small-model-training",
    "jarvis-operator-shell",
    "space-self-updating-surface",
    "agentic-rag-planner",
    "gitnexus-codegraph-gate",
    "synthetic-truth-guard",
    "black-box-interpretability-plane",
    "darwin-godel-machine-lineage",
    "alphaevolve-verifier-search",
    "tars-computer-use-operator",
}


def test_video_assimilation_scorecard_covers_all_specs():
    registry = AssimilationTargetRegistry()

    scorecard = registry.video_scorecard(session_id="video-assimilation")

    assert scorecard["status_label"] == "LOCKED CANON"
    assert scorecard["surface_id"] == "video-assimilation-targets"
    assert scorecard["target_count"] == 10
    assert {target["target_id"] for target in scorecard["targets"]} == EXPECTED_VIDEO_TARGET_IDS
    assert scorecard["coverage_summary"]["refs_only_count"] >= 4
    assert scorecard["coverage_summary"]["shadow_only_count"] >= 3
    assert scorecard["coverage_summary"]["clean_room_required_count"] >= 1
    jarvis = next(target for target in scorecard["targets"] if target["target_id"] == "jarvis-operator-shell")
    assert jarvis["source_status"] == "primary_verified"
    assert jarvis["clean_room_required"] is True
    assert "CC BY-NC 4.0" in jarvis["license_boundary"]


def test_video_assimilation_api_exposes_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/video-assimilation-targets")

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_count"] == 10
    assert payload["operator_actions"]["scorecard"]["endpoint"] == "/ops/brain/canon/video-assimilation-targets"
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_video_assimilation_targets.py -q
```

Expected: failure because `video_scorecard` and API endpoints do not exist.

- [ ] **Step 4: Add video source refs and target records**

Modify `nexusnet/operations/assimilation_targets.py` by adding these constants after `ASSIMILATION_TARGETS`:

```python
VIDEO_SOURCE_REFS: list[dict[str, str]] = [
    {
        "source_id": "video-spec-frontier-small-model-training",
        "label": "Frontier small model training video spec",
        "url": "docs/assimilation/videos/2026-05-06/01-frontier-small-model-training-spec.md",
        "assimilation_boundary": "Edge model lifecycle and certification only.",
    },
    {
        "source_id": "fatihmakes-mark-xxxix",
        "label": "Mark XXXIX repository",
        "url": "https://github.com/FatihMakes/Mark-XXXIX",
        "assimilation_boundary": "Clean-room UX and tool-surface pattern only; CC BY-NC 4.0 blocks code import.",
    },
    {
        "source_id": "space-agent-video-spec",
        "label": "Space Agent self-updating surface spec",
        "url": "docs/assimilation/videos/2026-05-06/03-space-agent-self-updating-surface-spec.md",
        "assimilation_boundary": "Sandboxed generated surface candidates only.",
    },
    {
        "source_id": "agentic-rag-video-spec",
        "label": "Agentic RAG planner spec",
        "url": "docs/assimilation/videos/2026-05-06/04-agentic-rag-planner-spec.md",
        "assimilation_boundary": "Planner and claim ledger only; retrieved snippets are not authority.",
    },
    {
        "source_id": "gitnexus-video-spec",
        "label": "GitNexus codegraph gate spec",
        "url": "docs/assimilation/videos/2026-05-06/05-gitnexus-codegraph-gate-spec.md",
        "assimilation_boundary": "Graph evidence and stale-index blockers only.",
    },
    {
        "source_id": "synthetic-truth-video-spec",
        "label": "Synthetic truth guard spec",
        "url": "docs/assimilation/videos/2026-05-06/06-synthetic-truth-guard-spec.md",
        "assimilation_boundary": "Source-status and abstention governance.",
    },
    {
        "source_id": "black-box-interpretability-video-spec",
        "label": "Black box interpretability plane spec",
        "url": "docs/assimilation/videos/2026-05-06/07-black-box-interpretability-plane-spec.md",
        "assimilation_boundary": "Behavioral concept telemetry and open-model research records.",
    },
    {
        "source_id": "sakana-dgm",
        "label": "Sakana Darwin Godel Machine",
        "url": "https://sakana.ai/dgm/",
        "assimilation_boundary": "Shadow-only lineage and eval gates; no production self-rewrite.",
    },
    {
        "source_id": "deepmind-alphaevolve",
        "label": "Google DeepMind AlphaEvolve",
        "url": "https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
        "assimilation_boundary": "Verifier-first candidate search where objective scoring exists.",
    },
    {
        "source_id": "bytedance-ui-tars",
        "label": "ByteDance UI-TARS Desktop",
        "url": "https://github.com/bytedance/UI-TARS-desktop",
        "assimilation_boundary": "Operator event stream and permission split; no unscoped desktop authority.",
    },
]

VIDEO_ASSIMILATION_TARGETS: list[dict[str, Any]] = [
    {
        "target_id": "frontier-small-model-training",
        "label": "Frontier Small Model Training",
        "source_ids": ["video-spec-frontier-small-model-training"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/01-frontier-small-model-training-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "shadow_certification",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["model_passport", "eval_registry", "quantization_catalog"],
        "required_controls": ["model_passport", "device_matrix", "certified_task_labels", "blocked_task_labels"],
    },
    {
        "target_id": "jarvis-operator-shell",
        "label": "Jarvis Mark XXXIX Operator Shell",
        "source_ids": ["fatihmakes-mark-xxxix"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/02-jarvis-operator-shell-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "clean_room_pattern_only",
        "clean_room_required": True,
        "license_boundary": "CC BY-NC 4.0 personal and non-commercial only",
        "nexus_surfaces": ["browser_profile_policy", "operator_events", "control_panel"],
        "required_controls": ["permission_envelope", "action_receipts", "profile_policy", "memory_consent"],
    },
    {
        "target_id": "space-self-updating-surface",
        "label": "Space Agent Self-Updating Surface",
        "source_ids": ["space-agent-video-spec"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/03-space-agent-self-updating-surface-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "shadow_only",
        "clean_room_required": True,
        "license_boundary": "source references only",
        "nexus_surfaces": ["self_improvement_lineage", "sandbox_factory"],
        "required_controls": ["generated_artifact_schema", "sandbox_default", "rollback_plan", "review_queue"],
    },
    {
        "target_id": "agentic-rag-planner",
        "label": "Agentic RAG Planner",
        "source_ids": ["agentic-rag-video-spec"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/04-agentic-rag-planner-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "candidate",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["retrieval_planner", "memory_quality_ledger"],
        "required_controls": ["retrieval_plan_schema", "claim_ledger", "critic_loop", "poisoning_controls"],
    },
    {
        "target_id": "gitnexus-codegraph-gate",
        "label": "GitNexus Codegraph Gate",
        "source_ids": ["gitnexus-video-spec"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/05-gitnexus-codegraph-gate-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "required_gate",
        "clean_room_required": False,
        "license_boundary": "tool evidence only",
        "nexus_surfaces": ["codegraph_gate", "agentic_pipelines"],
        "required_controls": ["impact_evidence", "stale_index_block", "detect_changes_evidence"],
    },
    {
        "target_id": "synthetic-truth-guard",
        "label": "Synthetic Truth Guard",
        "source_ids": ["synthetic-truth-video-spec"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/06-synthetic-truth-guard-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "critical_governance",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["memory_quality_ledger", "knowledge_artifacts", "policy_kernel"],
        "required_controls": ["source_status_enum", "abstention_reward", "contradiction_workflow", "canon_gate"],
    },
    {
        "target_id": "black-box-interpretability-plane",
        "label": "Black Box Interpretability Plane",
        "source_ids": ["black-box-interpretability-video-spec"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/07-black-box-interpretability-plane-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "research_only",
        "clean_room_required": False,
        "license_boundary": "open-model research records only",
        "nexus_surfaces": ["concept_telemetry", "engram_index"],
        "required_controls": ["behavioral_proxy_label", "sae_experiment_record", "closed_model_boundary"],
    },
    {
        "target_id": "darwin-godel-machine-lineage",
        "label": "Darwin Godel Machine Lineage",
        "source_ids": ["sakana-dgm"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/08-darwin-godel-machine-lineage-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_only",
        "clean_room_required": True,
        "license_boundary": "source references and paper/code review only",
        "nexus_surfaces": ["self_improvement_lineage", "eval_registry"],
        "required_controls": ["lineage_artifact", "anti_cheat_receipts", "transfer_tests", "reward_hacking_probe"],
    },
    {
        "target_id": "alphaevolve-verifier-search",
        "label": "AlphaEvolve Verifier Search",
        "source_ids": ["deepmind-alphaevolve"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/09-alphaevolve-verifier-search-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_optimizer",
        "clean_room_required": True,
        "license_boundary": "clean-room evaluator pattern only",
        "nexus_surfaces": ["verifier_search", "eval_registry"],
        "required_controls": ["objective_scorer", "candidate_database", "multi_objective_score", "human_review"],
    },
    {
        "target_id": "tars-computer-use-operator",
        "label": "TARS Computer-Use Operator",
        "source_ids": ["bytedance-ui-tars"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/10-tars-computer-use-operator-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "operator_plane_candidate",
        "clean_room_required": True,
        "license_boundary": "source references only; no unscoped authority",
        "nexus_surfaces": ["operator_events", "multimodal_computer_use", "protocol_trust"],
        "required_controls": ["operator_split", "event_stream", "mcp_mount_registry", "stop_control"],
    },
]
```

- [ ] **Step 5: Add scorecard methods**

Add these methods to `AssimilationTargetRegistry`:

```python
    def video_scorecard(self, session_id: str | None = None) -> dict[str, Any]:
        targets = deepcopy(VIDEO_ASSIMILATION_TARGETS)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "video-assimilation-targets",
            "session_id": session_id,
            "runtime_state": "live-bound",
            "target_count": len(targets),
            "targets": targets,
            "coverage_summary": {
                "target_count": len(targets),
                "covered_target_ids": [target["target_id"] for target in targets],
                "primary_verified_count": sum(1 for target in targets if target["source_status"] == "primary_verified"),
                "refs_only_count": sum(1 for target in targets if target["promotion_state"] in {"research_only", "clean_room_pattern_only", "candidate"}),
                "shadow_only_count": sum(1 for target in targets if "shadow" in target["promotion_state"]),
                "clean_room_required_count": sum(1 for target in targets if target["clean_room_required"]),
            },
            "source_refs": deepcopy(VIDEO_SOURCE_REFS),
            "promotion_boundary": "video targets are refs-only or shadow-only until code-backed tests and policy gates pass",
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/video-assimilation-targets"},
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/video-assimilation-targets"},
            },
        }

    def video_target(self, target_id: str) -> dict[str, Any] | None:
        for target in VIDEO_ASSIMILATION_TARGETS:
            if target["target_id"] == target_id:
                return {
                    "status_label": "LOCKED CANON",
                    "target": deepcopy(target),
                    "source_refs": [
                        deepcopy(source)
                        for source in VIDEO_SOURCE_REFS
                        if source["source_id"] in set(target.get("source_ids") or [])
                    ],
                    "control_plane_ref": "/ops/brain/canon/video-assimilation-targets",
                }
        return None
```

- [ ] **Step 6: Wire API endpoints**

Modify `nexus/api/app.py` near the existing assimilation target endpoints:

```python
    @application.get("/ops/brain/video-assimilation-targets")
    def ops_brain_video_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.video_scorecard(session_id=session_id)

    @application.get("/ops/brain/video-assimilation-targets/{target_id}")
    def ops_brain_video_assimilation_target(target_id: str):
        payload = services.brain_assimilation_targets.video_target(target_id)
        if payload is None:
            raise HTTPException(status_code=404, detail="video assimilation target not found")
        return payload

    @application.get("/ops/brain/canon/video-assimilation-targets")
    def ops_brain_canon_video_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.video_scorecard(session_id=session_id)
```

- [ ] **Step 7: Run tests**

Run:

```powershell
pytest tests/test_video_assimilation_targets.py tests/test_claude_code_assimilation_targets.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit this task only**

Run:

```powershell
git add nexusnet/operations/assimilation_targets.py nexus/api/app.py tests/test_video_assimilation_targets.py
git commit -m "feat: register video assimilation targets"
```

Expected: commit contains only the ledger, API, and tests for this task.

---

### Task 2: Synthetic Truth Guard

**Files:**
- Modify: `nexusnet/memory/quality_ledger.py`
- Modify: `nexusnet/policy/kernel.py`
- Create: `tests/test_synthetic_truth_guard.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `MemoryQualityLedger`, `SourceClaimRequest`, and `PolicyKernel`.

Expected: risk is MEDIUM because these objects are shared by memory-quality APIs and policy tests.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_synthetic_truth_guard.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.memory.quality_ledger import MemoryQualityLedger, SourceClaimRequest
from tests.test_nexus_phase1_foundation import make_project


def test_synthetic_truth_guard_blocks_transcript_only_promotion():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        SourceClaimRequest(
            claim_id="claim::video-only",
            answer_id="answer::assimilation",
            claim_text="The demo proves production-safe self-modification.",
            answerability_status="source_backed",
            source_status="transcript_only",
            source_refs=["video::demo-transcript"],
            confidence=0.91,
            promotion_state="canon_candidate",
        )
    )

    assert claim["status"] == "blocked"
    assert claim["source_status"] == "transcript_only"
    assert "claim_source_status_blocks_promotion" in {finding["rule_id"] for finding in claim["quality_findings"]}
    assert claim["abstention_reward"] == 0.0


def test_synthetic_truth_guard_rewards_explicit_unknown():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        {
            "claim_id": "claim::unknown",
            "answer_id": "answer::assimilation",
            "claim_text": "No primary source was verified for this claim.",
            "answerability_status": "explicit_unknown",
            "source_status": "unverified",
            "confidence": 0.0,
            "promotion_state": "blocked",
            "uncertainty_label": "not_verified",
        }
    )

    assert claim["status"] == "verified"
    assert claim["abstention_reward"] == 1.0
    assert claim["answerability_gate"] == "explicit-unknown"


def test_synthetic_truth_guard_api_exposes_source_status(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/memory-quality/claims",
        json={
            "claim_id": "claim::api-contradiction",
            "answer_id": "answer::api",
            "claim_text": "Conflicting source claim.",
            "answerability_status": "conflicting",
            "source_status": "contradicted",
            "source_refs": ["source::a"],
            "contradiction_refs": ["source::b"],
            "confidence": 0.5,
            "promotion_state": "canon_candidate",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["source_status"] == "contradicted"
    assert payload["promotion_state"] == "canon_candidate"
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_synthetic_truth_guard.py -q
```

Expected: failure because `source_status`, `promotion_state`, and abstention scoring are not present.

- [ ] **Step 4: Extend request schema**

In `nexusnet/memory/quality_ledger.py`, add these literals:

```python
SourceStatus = Literal[
    "primary_verified",
    "secondary_verified",
    "transcript_only",
    "operator_supplied",
    "inferred",
    "unverified",
    "contradicted",
    "rejected",
]
PromotionState = Literal["none", "refs_only", "review_required", "canon_candidate", "promoted", "blocked"]
```

Add fields to `SourceClaimRequest`:

```python
    source_status: SourceStatus = "unverified"
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty_label: str = ""
    reviewer: str = ""
    promotion_state: PromotionState = "none"
```

- [ ] **Step 5: Persist the new fields**

Inside `record_claim`, add these keys to the `claim` dict:

```python
            "source_status": normalized.source_status,
            "evidence_strength": normalized.evidence_strength,
            "uncertainty_label": normalized.uncertainty_label,
            "reviewer": normalized.reviewer,
            "promotion_state": normalized.promotion_state,
            "abstention_reward": _abstention_reward(normalized),
```

- [ ] **Step 6: Add source-status quality findings**

Append this logic to `_quality_findings`:

```python
    promotion_requested = request.promotion_state in {"canon_candidate", "promoted"}
    if promotion_requested and request.source_status in {"transcript_only", "operator_supplied", "inferred", "unverified", "contradicted", "rejected"}:
        findings.append(
            {
                "rule_id": "claim_source_status_blocks_promotion",
                "severity": "hard_fail",
                "message": "Claims need primary or secondary verification before canon promotion.",
            }
        )
    if request.source_status == "contradicted" and not request.contradiction_refs:
        findings.append(
            {
                "rule_id": "contradicted_claim_requires_contradiction_refs",
                "severity": "hard_fail",
                "message": "Contradicted claims must preserve contradiction references.",
            }
        )
```

Add helper:

```python
def _abstention_reward(request: SourceClaimRequest) -> float:
    if request.answerability_status == "explicit_unknown" and request.source_status in {"unverified", "rejected", "contradicted"}:
        return 1.0
    if request.uncertainty_label and request.promotion_state in {"none", "refs_only", "blocked"}:
        return 0.5
    return 0.0
```

- [ ] **Step 7: Add policy rule for unsupported canon promotion**

In `PolicyKernel.default()`, add a hard-fail rule:

```python
                PolicyRule(
                    rule_id="canon_claim_requires_verified_source_status",
                    title="Canon claims require verified source status",
                    severity="hard_fail",
                    target_types=["claim"],
                    description="Blocks canon claim promotion when source status is not primary or secondary verified.",
                    required_evidence=["source_status", "source_refs"],
                    promotion_gate="synthetic-truth-guard",
                ),
```

Add to `_evaluate_rule`:

```python
        if rule.rule_id == "canon_claim_requires_verified_source_status":
            if metadata.get("promotion_requested") and metadata.get("source_status") not in {"primary_verified", "secondary_verified"}:
                return "Canon claim promotion requested without verified source status."
```

Update `_policy_targets` in `quality_ledger.py` to include a claim target:

```python
        {
            "target_id": f"claim::{request.claim_id}",
            "target_type": "claim",
            "metadata": {
                "promotion_requested": request.promotion_state in {"canon_candidate", "promoted"},
                "source_status": request.source_status,
                "source_refs": request.source_refs,
            },
        },
```

- [ ] **Step 8: Run tests**

Run:

```powershell
pytest tests/test_synthetic_truth_guard.py tests/test_memory_quality_ledger.py tests/test_policy_kernel.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit this task only**

Run:

```powershell
git add nexusnet/memory/quality_ledger.py nexusnet/policy/kernel.py tests/test_synthetic_truth_guard.py
git commit -m "feat: add synthetic truth guard source status"
```

---

### Task 3: Agentic Retrieval Planner

**Files:**
- Create: `nexusnet/retrieval/planner.py`
- Modify: `nexusnet/retrieval/__init__.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_retrieval_planner.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `create_app` and `NexusServices`.

Expected: risk is MEDIUM because new service fields and API endpoints are added.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_retrieval_planner.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.retrieval.planner import RetrievalPlanner, RetrievalPlanRequest
from tests.test_nexus_phase1_foundation import make_project


def test_retrieval_planner_requires_evidence_threshold_and_modes():
    planner = RetrievalPlanner()

    plan = planner.plan(
        RetrievalPlanRequest(
            plan_id="retrieval-plan::complex",
            user_goal="Explain whether the Jarvis repo is safe to assimilate.",
            source_classes=["repo", "video_transcript", "primary_source"],
            query_decomposition=["verify license", "map high-authority actions", "extract safe NexusNet transfers"],
            retrieval_modes=["lexical", "semantic", "graph", "temporal", "rerank"],
            evidence_threshold=0.8,
            cost_budget_ms=2500,
        )
    )

    assert plan["status_label"] == "LOCKED CANON"
    assert plan["surface_id"] == "retrieval-planner"
    assert plan["status"] == "planned"
    assert plan["claim_ledger_contract"]["requires_source_status"] is True
    assert {"lexical", "semantic", "graph", "temporal", "rerank"} == set(plan["retrieval_modes"])
    assert "critic_loop" in plan["required_controls"]


def test_retrieval_planner_blocks_low_threshold_deep_retrieval():
    planner = RetrievalPlanner()

    plan = planner.plan(
        {
            "plan_id": "retrieval-plan::unsafe",
            "user_goal": "Make a canon claim from one weak source.",
            "source_classes": ["video_transcript"],
            "query_decomposition": [],
            "retrieval_modes": ["semantic"],
            "evidence_threshold": 0.25,
            "cost_budget_ms": 0,
        }
    )

    assert plan["status"] == "blocked"
    assert "retrieval_plan_requires_decomposition" in {finding["rule_id"] for finding in plan["planner_findings"]}
    assert "retrieval_plan_requires_evidence_threshold" in {finding["rule_id"] for finding in plan["planner_findings"]}


def test_retrieval_planner_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/retrieval/plans",
        json={
            "plan_id": "retrieval-plan::api",
            "user_goal": "Answer with source-backed claims only.",
            "source_classes": ["primary_source", "repo"],
            "query_decomposition": ["find primary source", "check contradiction"],
            "retrieval_modes": ["lexical", "rerank"],
            "evidence_threshold": 0.7,
            "cost_budget_ms": 1500,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "planned"
    summary = client.get("/ops/brain/retrieval/planner")
    assert summary.status_code == 200
    assert summary.json()["plan_count"] == 1
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_retrieval_planner.py -q
```

Expected: failure because `nexusnet.retrieval.planner` does not exist.

- [ ] **Step 4: Implement planner module**

Create `nexusnet/retrieval/planner.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


RetrievalMode = Literal["lexical", "semantic", "graph", "temporal", "rerank"]
SourceClass = Literal["primary_source", "secondary_source", "repo", "paper", "video_transcript", "memory", "operator_supplied"]


class RetrievalPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    user_goal: str
    source_classes: list[SourceClass] = Field(default_factory=list)
    query_decomposition: list[str] = Field(default_factory=list)
    retrieval_modes: list[RetrievalMode] = Field(default_factory=list)
    evidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    cost_budget_ms: int = Field(default=1500, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalPlanner:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "retrieval" / "planner" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_plans: list[dict[str, Any]] = []

    def plan(self, request: RetrievalPlanRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, RetrievalPlanRequest) else RetrievalPlanRequest.model_validate(request)
        findings = _planner_findings(normalized)
        blocked = bool(findings)
        payload = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "retrieval-planner",
            "plan_id": normalized.plan_id,
            "user_goal": normalized.user_goal,
            "status": "blocked" if blocked else "planned",
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "source_classes": normalized.source_classes,
            "query_decomposition": normalized.query_decomposition,
            "retrieval_modes": normalized.retrieval_modes or ["lexical", "semantic", "rerank"],
            "evidence_threshold": normalized.evidence_threshold,
            "cost_budget_ms": normalized.cost_budget_ms,
            "stop_condition": "enough_verified_sources_or_explicit_unknown",
            "claim_ledger_contract": {
                "requires_source_status": True,
                "requires_contradiction_refs": True,
                "unsupported_claim_state": "explicit_unknown",
            },
            "critic_loop": [
                "grade_document_relevance",
                "rewrite_query_when_evidence_misses_goal",
                "preserve_contradictions",
                "abstain_when_threshold_not_met",
            ],
            "poisoning_controls": ["private_source_block", "stale_source_warning", "memory_quality_downgrade"],
            "planner_findings": findings,
            "required_controls": _required_controls(),
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(payload)
        return payload

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        plans = self._list_plans(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "retrieval-planner",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(plan.get("status") == "blocked" for plan in plans) else ("live-bound" if plans else "static-canon"),
            "plan_count": len(plans),
            "blocked_count": sum(1 for plan in plans if plan.get("status") == "blocked"),
            "latest_plan": plans[0] if plans else None,
            "plans": plans,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def _persist(self, payload: dict[str, Any]) -> None:
        self._memory_plans.insert(0, payload)
        self._memory_plans = self._memory_plans[:50]
        if self.plans_dir is not None:
            path = self.plans_dir / f"{_safe_id(payload['plan_id'])}.json"
            payload["artifact_path"] = str(path)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _list_plans(self, *, limit: int) -> list[dict[str, Any]]:
        plans = list(self._memory_plans)
        seen = {plan.get("plan_id") for plan in plans}
        if self.plans_dir is not None:
            for path in self.plans_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("plan_id") not in seen:
                    plans.append(payload)
        plans.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return plans[:limit]


def _planner_findings(request: RetrievalPlanRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not request.query_decomposition:
        findings.append({"rule_id": "retrieval_plan_requires_decomposition", "severity": "hard_fail", "message": "Complex retrieval requires query decomposition."})
    if request.evidence_threshold < 0.65:
        findings.append({"rule_id": "retrieval_plan_requires_evidence_threshold", "severity": "hard_fail", "message": "Evidence threshold must be at least 0.65 for source-backed answers."})
    if not request.source_classes:
        findings.append({"rule_id": "retrieval_plan_requires_source_classes", "severity": "hard_fail", "message": "Retrieval plans must name source classes."})
    return findings


def _required_controls() -> list[str]:
    return ["retrieval_plan_schema", "hybrid_retrieval_modes", "claim_ledger", "critic_loop", "poisoning_controls", "cost_latency_budget"]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/retrieval/planner"},
        "plan": {"method": "POST", "endpoint": "/ops/brain/retrieval/plans"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/retrieval-planner"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "retrieval_plan"
```

- [ ] **Step 5: Export the planner**

Modify `nexusnet/retrieval/__init__.py`:

```python
from .planner import RetrievalPlanner, RetrievalPlanRequest

__all__ = ["RetrievalPlanner", "RetrievalPlanRequest"]
```

If `__all__` already contains names, merge these two names into the existing list.

- [ ] **Step 6: Wire service and API**

Modify `nexus/services.py`:

```python
from nexusnet.retrieval import RetrievalPlanner
```

Add `brain_retrieval_planner: Any` to `NexusServices`.

Inside `build_services`, instantiate:

```python
        brain_retrieval_planner=RetrievalPlanner(artifacts_dir=paths.artifacts_dir),
```

Modify `nexus/api/app.py`:

```python
from nexusnet.retrieval import RetrievalPlanRequest
```

Add endpoints near retrieval routes:

```python
    @application.get("/ops/brain/retrieval/planner")
    def ops_brain_retrieval_planner():
        return services.brain_retrieval_planner.summary()

    @application.post("/ops/brain/retrieval/plans")
    def ops_brain_retrieval_plans(payload: dict[str, Any] = Body(...)):
        return services.brain_retrieval_planner.plan(RetrievalPlanRequest.model_validate(payload))

    @application.get("/ops/brain/canon/retrieval-planner")
    def ops_brain_canon_retrieval_planner():
        return services.brain_retrieval_planner.summary()
```

- [ ] **Step 7: Run tests**

Run:

```powershell
pytest tests/test_retrieval_planner.py tests/test_assimilation_convergence.py tests/test_memory_quality_ledger.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit this task only**

Run:

```powershell
git add nexusnet/retrieval/planner.py nexusnet/retrieval/__init__.py nexus/services.py nexus/api/app.py tests/test_retrieval_planner.py
git commit -m "feat: add agentic retrieval planner"
```

---

### Task 4: Self-Improvement Lineage And Verifier Search

**Files:**
- Create: `nexusnet/core/self_improvement/lineage.py`
- Modify: `nexusnet/core/self_improvement/__init__.py`
- Create: `nexusnet/evals/verifier_search.py`
- Modify: `nexusnet/evals/__init__.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_assimilation_lineage_verifier_search.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `ImprovementQueue`, `EvalRegistry`, `NexusServices`, and `create_app`.

Expected: risk is MEDIUM. This task adds parallel surfaces and API endpoints without changing existing queue transitions.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_assimilation_lineage_verifier_search.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.core.self_improvement import SelfImprovementLineageRegistry, LineageCandidateRequest
from nexusnet.evals import VerifierSearchRegistry, VerifierSearchRequest
from tests.test_nexus_phase1_foundation import make_project


def test_lineage_candidate_stays_shadow_and_records_anti_cheat_receipts():
    registry = SelfImprovementLineageRegistry()

    candidate = registry.record_candidate(
        LineageCandidateRequest(
            candidate_id="candidate::dgm-shadow",
            parent_ids=["candidate::root"],
            mutation_prompt="Improve retrieval plan scoring.",
            touched_files=["nexusnet/retrieval/planner.py"],
            eval_suite_refs=["eval::nexus-held-out"],
            command_receipts=[{"command": "pytest tests/test_retrieval_planner.py -q", "exit_code": 0, "artifact_hash": "sha256:abc"}],
            scores={"pass_rate": 0.9, "safety": 0.95},
            transfer_results={"alternate_model": "passed"},
            safety_flags=[],
            reviewer_decision="shadow-passed",
        )
    )

    assert candidate["status"] == "shadow-passed"
    assert candidate["promotion_allowed"] is False
    assert candidate["anti_cheat_gate"]["real_receipts_present"] is True
    assert candidate["lineage"]["parent_ids"] == ["candidate::root"]


def test_lineage_blocks_fake_receipts_and_reward_hacking():
    registry = SelfImprovementLineageRegistry()

    candidate = registry.record_candidate(
        {
            "candidate_id": "candidate::unsafe",
            "parent_ids": [],
            "mutation_prompt": "Maximize benchmark by hiding failures.",
            "touched_files": ["nexusnet/evals/registry.py"],
            "eval_suite_refs": [],
            "command_receipts": [{"command": "pytest", "exit_code": 0}],
            "scores": {"pass_rate": 0.99, "safety": 0.4},
            "transfer_results": {},
            "safety_flags": ["reward_hacking_probe_failed"],
            "reviewer_decision": "safety-blocked",
        }
    )

    assert candidate["status"] == "safety-blocked"
    assert candidate["promotion_allowed"] is False
    assert "lineage_candidate_requires_hashable_command_receipts" in {finding["rule_id"] for finding in candidate["findings"]}
    assert "reward_hacking_probe_failed" in candidate["safety_flags"]


def test_verifier_search_records_multi_objective_candidate_database():
    registry = VerifierSearchRegistry()

    result = registry.record_search(
        VerifierSearchRequest(
            search_id="verifier-search::retrieval-policy",
            objective="Improve retrieval source faithfulness without increasing latency.",
            scorer_ref="scorer::source-faithfulness-v1",
            candidates=[
                {"candidate_id": "candidate::fast", "scores": {"quality": 0.72, "latency": 0.95, "safety": 0.9, "source_faithfulness": 0.6}},
                {"candidate_id": "candidate::faithful", "scores": {"quality": 0.86, "latency": 0.74, "safety": 0.94, "source_faithfulness": 0.91}},
            ],
            constraints={"minimum_source_faithfulness": 0.8, "minimum_safety": 0.85},
            evidence_refs=["eval::source-faithfulness-v1"],
        )
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["selected"]["candidate_id"] == "candidate::faithful"
    assert result["blocked_candidates"][0]["candidate_id"] == "candidate::fast"
    assert result["promotion_boundary"] == "verifier-search-results-remain-shadow-until-human-review"


def test_lineage_and_verifier_search_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    lineage = client.post(
        "/ops/brain/self-improvement/lineage/candidates",
        json={
            "candidate_id": "candidate::api",
            "parent_ids": ["candidate::root"],
            "mutation_prompt": "Create a retrieval planner.",
            "touched_files": ["nexusnet/retrieval/planner.py"],
            "eval_suite_refs": ["eval::api"],
            "command_receipts": [{"command": "pytest tests/test_retrieval_planner.py -q", "exit_code": 0, "artifact_hash": "sha256:def"}],
            "scores": {"pass_rate": 0.88, "safety": 0.94},
            "transfer_results": {"alternate_model": "passed"},
            "safety_flags": [],
            "reviewer_decision": "teacher-approved",
        },
    )
    assert lineage.status_code == 200
    assert lineage.json()["status"] == "teacher-approved"

    search = client.post(
        "/ops/brain/verifier-search/runs",
        json={
            "search_id": "verifier-search::api",
            "objective": "Choose the safest retrieval planner candidate.",
            "scorer_ref": "scorer::api",
            "candidates": [{"candidate_id": "candidate::api", "scores": {"quality": 0.9, "latency": 0.8, "safety": 0.93, "source_faithfulness": 0.9}}],
            "constraints": {"minimum_source_faithfulness": 0.8},
            "evidence_refs": ["eval::api"],
        },
    )
    assert search.status_code == 200
    assert search.json()["selected"]["candidate_id"] == "candidate::api"
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_assimilation_lineage_verifier_search.py -q
```

Expected: failure because the new modules do not exist.

- [ ] **Step 4: Implement lineage registry**

Create `nexusnet/core/self_improvement/lineage.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ReviewerDecision = Literal["proposed", "built-in-sandbox", "eval-failed", "safety-blocked", "shadow-passed", "teacher-approved", "operator-approved", "merged", "rolled-back"]


class LineageCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    parent_ids: list[str] = Field(default_factory=list)
    mutation_prompt: str
    touched_files: list[str] = Field(default_factory=list)
    eval_suite_refs: list[str] = Field(default_factory=list)
    command_receipts: list[dict[str, Any]] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)
    transfer_results: dict[str, Any] = Field(default_factory=dict)
    safety_flags: list[str] = Field(default_factory=list)
    reviewer_decision: ReviewerDecision = "proposed"
    rollback_plan: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SelfImprovementLineageRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "self-improvement" / "lineage" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def record_candidate(self, request: LineageCandidateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, LineageCandidateRequest) else LineageCandidateRequest.model_validate(request)
        findings = _findings(normalized)
        anti_cheat_gate = {
            "real_receipts_present": bool(normalized.command_receipts) and not any(finding["rule_id"] == "lineage_candidate_requires_hashable_command_receipts" for finding in findings),
            "receipt_count": len(normalized.command_receipts),
        }
        promotion_allowed = normalized.reviewer_decision in {"operator-approved", "merged"} and not findings and bool(normalized.rollback_plan)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "self-improvement-lineage",
            "candidate_id": normalized.candidate_id,
            "status": normalized.reviewer_decision,
            "runtime_state": "degraded" if findings or normalized.safety_flags else "live-bound",
            "created_at": utcnow().isoformat(),
            "lineage": {"parent_ids": normalized.parent_ids, "candidate_id": normalized.candidate_id},
            "mutation_prompt": normalized.mutation_prompt,
            "touched_files": normalized.touched_files,
            "eval_suite_refs": normalized.eval_suite_refs,
            "command_receipts": normalized.command_receipts,
            "scores": normalized.scores,
            "transfer_results": normalized.transfer_results,
            "safety_flags": normalized.safety_flags,
            "anti_cheat_gate": anti_cheat_gate,
            "findings": findings,
            "promotion_allowed": promotion_allowed,
            "promotion_boundary": "lineage-candidates-stay-shadow-until-eval-safety-transfer-rollback-and-operator-approval",
            "rollback_plan": normalized.rollback_plan,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "self-improvement-lineage",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("findings") or record.get("safety_flags") for record in records) else ("live-bound" if records else "static-canon"),
            "candidate_count": len(records),
            "latest_candidate": records[0] if records else None,
            "candidates": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{_safe_id(record['candidate_id'])}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("candidate_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("candidate_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _findings(request: LineageCandidateRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not request.eval_suite_refs:
        findings.append({"rule_id": "lineage_candidate_requires_eval_suite_refs", "severity": "hard_fail", "message": "Lineage candidates require eval suite references."})
    if not request.command_receipts or any(not receipt.get("artifact_hash") for receipt in request.command_receipts):
        findings.append({"rule_id": "lineage_candidate_requires_hashable_command_receipts", "severity": "hard_fail", "message": "Command receipts require artifact hashes."})
    if request.scores.get("safety", 1.0) < 0.85:
        findings.append({"rule_id": "lineage_candidate_blocks_low_safety_score", "severity": "hard_fail", "message": "Safety score below 0.85 blocks promotion."})
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/self-improvement/lineage"},
        "record_candidate": {"method": "POST", "endpoint": "/ops/brain/self-improvement/lineage/candidates"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "candidate"
```

- [ ] **Step 5: Implement verifier search registry**

Create `nexusnet/evals/verifier_search.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


class VerifierSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    search_id: str
    objective: str
    scorer_ref: str
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    constraints: dict[str, float] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerifierSearchRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "evals" / "verifier-search" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def record_search(self, request: VerifierSearchRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, VerifierSearchRequest) else VerifierSearchRequest.model_validate(request)
        scored = [_score_candidate(candidate, normalized.constraints) for candidate in normalized.candidates]
        allowed = [candidate for candidate in scored if not candidate["blockers"]]
        blocked = [candidate for candidate in scored if candidate["blockers"]]
        selected = sorted(allowed, key=lambda item: item["multi_objective_score"], reverse=True)[0] if allowed else None
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "verifier-search",
            "search_id": normalized.search_id,
            "objective": normalized.objective,
            "scorer_ref": normalized.scorer_ref,
            "status": "candidate-selected" if selected else "blocked",
            "runtime_state": "live-bound" if selected else "degraded",
            "created_at": utcnow().isoformat(),
            "selected": selected,
            "candidate_count": len(scored),
            "candidates": scored,
            "blocked_candidates": blocked,
            "constraints": normalized.constraints,
            "evidence_refs": normalized.evidence_refs,
            "promotion_boundary": "verifier-search-results-remain-shadow-until-human-review",
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "verifier-search",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in records) else ("live-bound" if records else "static-canon"),
            "search_count": len(records),
            "latest_search": records[0] if records else None,
            "searches": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{_safe_id(record['search_id'])}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("search_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("search_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _score_candidate(candidate: dict[str, Any], constraints: dict[str, float]) -> dict[str, Any]:
    scores = {str(key): float(value) for key, value in (candidate.get("scores") or {}).items()}
    blockers = []
    if scores.get("source_faithfulness", 0.0) < constraints.get("minimum_source_faithfulness", 0.0):
        blockers.append("source_faithfulness_below_constraint")
    if scores.get("safety", 1.0) < constraints.get("minimum_safety", 0.0):
        blockers.append("safety_below_constraint")
    multi_objective_score = round(
        (0.35 * scores.get("quality", 0.0))
        + (0.25 * scores.get("source_faithfulness", 0.0))
        + (0.25 * scores.get("safety", 0.0))
        + (0.15 * scores.get("latency", 0.0)),
        4,
    )
    return {**candidate, "scores": scores, "multi_objective_score": multi_objective_score, "blockers": blockers}


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/verifier-search"},
        "record_search": {"method": "POST", "endpoint": "/ops/brain/verifier-search/runs"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "verifier_search"
```

- [ ] **Step 6: Export modules**

Modify `nexusnet/core/self_improvement/__init__.py`:

```python
from .lineage import LineageCandidateRequest, SelfImprovementLineageRegistry
```

Add both names to `__all__`.

Modify `nexusnet/evals/__init__.py`:

```python
from .verifier_search import VerifierSearchRegistry, VerifierSearchRequest
```

Add both names to `__all__`.

- [ ] **Step 7: Wire service and API**

Add service fields in `nexus/services.py`:

```python
from nexusnet.core.self_improvement import SelfImprovementLineageRegistry
from nexusnet.evals import VerifierSearchRegistry
```

Add to `NexusServices`:

```python
    brain_self_improvement_lineage: Any
    brain_verifier_search: Any
```

Add to `build_services`:

```python
        brain_self_improvement_lineage=SelfImprovementLineageRegistry(artifacts_dir=paths.artifacts_dir),
        brain_verifier_search=VerifierSearchRegistry(artifacts_dir=paths.artifacts_dir),
```

Modify `nexus/api/app.py`:

```python
from nexusnet.core.self_improvement import LineageCandidateRequest
from nexusnet.evals import VerifierSearchRequest
```

Add endpoints:

```python
    @application.get("/ops/brain/self-improvement/lineage")
    def ops_brain_self_improvement_lineage():
        return services.brain_self_improvement_lineage.summary()

    @application.post("/ops/brain/self-improvement/lineage/candidates")
    def ops_brain_self_improvement_lineage_candidates(payload: dict[str, Any] = Body(...)):
        return services.brain_self_improvement_lineage.record_candidate(LineageCandidateRequest.model_validate(payload))

    @application.get("/ops/brain/verifier-search")
    def ops_brain_verifier_search():
        return services.brain_verifier_search.summary()

    @application.post("/ops/brain/verifier-search/runs")
    def ops_brain_verifier_search_runs(payload: dict[str, Any] = Body(...)):
        return services.brain_verifier_search.record_search(VerifierSearchRequest.model_validate(payload))
```

- [ ] **Step 8: Run tests**

Run:

```powershell
pytest tests/test_assimilation_lineage_verifier_search.py tests/test_self_improvement_layer.py tests/test_eval_registry.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit this task only**

Run:

```powershell
git add nexusnet/core/self_improvement/lineage.py nexusnet/core/self_improvement/__init__.py nexusnet/evals/verifier_search.py nexusnet/evals/__init__.py nexus/services.py nexus/api/app.py tests/test_assimilation_lineage_verifier_search.py
git commit -m "feat: add assimilation lineage and verifier search"
```

---

### Task 5: Operator Permission Events And Browser Profile Policy

**Files:**
- Create: `nexusnet/browser/profile_policy.py`
- Modify: `nexusnet/browser/__init__.py`
- Create: `nexusnet/vision/operator_events.py`
- Modify: `nexusnet/vision/__init__.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_operator_permission_events.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `MultimodalComputerUseController`, `BrowserContextMemory`, `NexusServices`, and `create_app`.

Expected: risk is MEDIUM because this adds operator event surfaces and new API endpoints.

- [ ] **Step 2: Write failing tests**

Create `tests/test_operator_permission_events.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.browser import BrowserProfilePolicy, BrowserProfilePolicyRequest
from nexusnet.vision import OperatorEventRegistry, OperatorEventRequest
from tests.test_nexus_phase1_foundation import make_project


def test_browser_profile_policy_blocks_real_profile_by_default():
    policy = BrowserProfilePolicy()

    decision = policy.evaluate(
        BrowserProfilePolicyRequest(
            request_id="browser-profile::default",
            profile_mode="real_user_profile",
            session_scoped_permission=False,
            contains_private_data=True,
            provenance_ref="",
        )
    )

    assert decision["status"] == "blocked"
    assert "real_browser_profile_requires_session_permission" in {finding["rule_id"] for finding in decision["findings"]}
    assert decision["recommended_profile_mode"] == "nexus_owned_ephemeral"


def test_operator_event_registry_blocks_cross_operator_escalation():
    registry = OperatorEventRegistry()

    event = registry.record(
        OperatorEventRequest(
            event_id="operator-event::browser-to-terminal",
            run_id="operator-run::1",
            operator_kind="browser_operator",
            action_kind="terminal_command",
            permission_scope="browser_only",
            target_confidence=0.92,
            evidence_refs=["screenshot::1"],
            stop_window_ms=1500,
        )
    )

    assert event["status"] == "blocked"
    assert "operator_event_blocks_permission_escalation" in {finding["rule_id"] for finding in event["findings"]}
    assert event["receipt"]["rollback_available"] is False


def test_operator_event_registry_records_safe_browser_action():
    registry = OperatorEventRegistry()

    event = registry.record(
        {
            "event_id": "operator-event::browser-click",
            "run_id": "operator-run::2",
            "operator_kind": "browser_operator",
            "action_kind": "browser_click",
            "permission_scope": "browser_only",
            "target_confidence": 0.91,
            "evidence_refs": ["screenshot::button"],
            "stop_window_ms": 1500,
            "rollback_ref": "browser-history-back",
        }
    )

    assert event["status"] == "recorded"
    assert event["receipt"]["rollback_available"] is True
    assert event["event_stream_contract"] == "observation-plan-action-result-correction"


def test_operator_events_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    profile = client.post(
        "/ops/brain/browser/profile-policy",
        json={
            "request_id": "browser-profile::api",
            "profile_mode": "nexus_owned_ephemeral",
            "session_scoped_permission": False,
            "contains_private_data": False,
            "provenance_ref": "operator::api",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["status"] == "allowed"

    event = client.post(
        "/ops/brain/operator-events",
        json={
            "event_id": "operator-event::api",
            "run_id": "operator-run::api",
            "operator_kind": "desktop_operator",
            "action_kind": "desktop_observe",
            "permission_scope": "desktop_observe_only",
            "target_confidence": 0.8,
            "evidence_refs": ["screenshot::api"],
            "stop_window_ms": 1000,
        },
    )
    assert event.status_code == 200
    assert event.json()["status"] == "recorded"
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_operator_permission_events.py -q
```

Expected: failure because the new modules do not exist.

- [ ] **Step 4: Implement browser profile policy**

Create `nexusnet/browser/profile_policy.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ProfileMode = Literal["nexus_owned_ephemeral", "nexus_owned_persistent", "real_user_profile"]


class BrowserProfilePolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_mode: ProfileMode = "nexus_owned_ephemeral"
    session_scoped_permission: bool = False
    contains_private_data: bool = False
    provenance_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserProfilePolicy:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "browser" / "profile-policy" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def evaluate(self, request: BrowserProfilePolicyRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, BrowserProfilePolicyRequest) else BrowserProfilePolicyRequest.model_validate(request)
        findings = _findings(normalized)
        decision = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "browser-profile-policy",
            "request_id": normalized.request_id,
            "profile_mode": normalized.profile_mode,
            "status": "blocked" if findings else "allowed",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "session_scoped_permission": normalized.session_scoped_permission,
            "contains_private_data": normalized.contains_private_data,
            "provenance_ref": normalized.provenance_ref,
            "recommended_profile_mode": "nexus_owned_ephemeral" if findings else normalized.profile_mode,
            "findings": findings,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(decision)
        return decision

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._memory_records[:limit]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "browser-profile-policy",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in records) else ("live-bound" if records else "static-canon"),
            "decision_count": len(records),
            "latest_decision": records[0] if records else None,
            "decisions": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, decision: dict[str, Any]) -> None:
        self._memory_records.insert(0, decision)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{decision['request_id'].replace(':', '_')}.json"
            decision["artifact_path"] = str(path)
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")


def _findings(request: BrowserProfilePolicyRequest) -> list[dict[str, str]]:
    findings = []
    if request.profile_mode == "real_user_profile" and not request.session_scoped_permission:
        findings.append({"rule_id": "real_browser_profile_requires_session_permission", "severity": "hard_fail", "message": "Real browser profiles require explicit session-scoped permission."})
    if request.contains_private_data and not request.provenance_ref:
        findings.append({"rule_id": "private_browser_profile_requires_provenance", "severity": "hard_fail", "message": "Private browser profile use requires a provenance or consent reference."})
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/browser/profile-policy"},
        "evaluate": {"method": "POST", "endpoint": "/ops/brain/browser/profile-policy"},
    }
```

- [ ] **Step 5: Implement operator event registry**

Create `nexusnet/vision/operator_events.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


OperatorKind = Literal["browser_operator", "desktop_operator", "terminal_operator", "file_operator", "mcp_tool_operator"]
ActionKind = Literal["browser_click", "browser_type", "desktop_observe", "desktop_click", "terminal_command", "file_read", "file_write", "mcp_tool_call"]
PermissionScope = Literal["browser_only", "desktop_observe_only", "desktop_control", "terminal_only", "file_read_only", "file_write", "mcp_tool_only"]


class OperatorEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    run_id: str
    operator_kind: OperatorKind
    action_kind: ActionKind
    permission_scope: PermissionScope
    target_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    stop_window_ms: int = Field(default=1000, ge=0)
    rollback_ref: str = ""
    result: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorEventRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "vision" / "operator-events" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_events: list[dict[str, Any]] = []

    def record(self, request: OperatorEventRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, OperatorEventRequest) else OperatorEventRequest.model_validate(request)
        findings = _findings(normalized)
        event = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "operator-events",
            "event_id": normalized.event_id,
            "run_id": normalized.run_id,
            "operator_kind": normalized.operator_kind,
            "action_kind": normalized.action_kind,
            "permission_scope": normalized.permission_scope,
            "status": "blocked" if findings else "recorded",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "target_confidence": normalized.target_confidence,
            "evidence_refs": normalized.evidence_refs,
            "stop_window_ms": normalized.stop_window_ms,
            "receipt": {
                "request": normalized.model_dump(mode="json"),
                "rollback_available": bool(normalized.rollback_ref),
                "rollback_ref": normalized.rollback_ref,
                "result": normalized.result,
            },
            "event_stream_contract": "observation-plan-action-result-correction",
            "findings": findings,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(event)
        return event

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        events = self._list_events(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "operator-events",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(event.get("status") == "blocked" for event in events) else ("live-bound" if events else "static-canon"),
            "event_count": len(events),
            "blocked_count": sum(1 for event in events if event.get("status") == "blocked"),
            "latest_event": events[0] if events else None,
            "events": events,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, event: dict[str, Any]) -> None:
        self._memory_events.insert(0, event)
        self._memory_events = self._memory_events[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{event['event_id'].replace(':', '_')}.json"
            event["artifact_path"] = str(path)
            path.write_text(json.dumps(event, indent=2), encoding="utf-8")

    def _list_events(self, *, limit: int) -> list[dict[str, Any]]:
        return self._memory_events[:limit]


def _findings(request: OperatorEventRequest) -> list[dict[str, str]]:
    findings = []
    allowed_pairs = {
        "browser_operator": {"browser_click", "browser_type"},
        "desktop_operator": {"desktop_observe", "desktop_click"},
        "terminal_operator": {"terminal_command"},
        "file_operator": {"file_read", "file_write"},
        "mcp_tool_operator": {"mcp_tool_call"},
    }
    if request.action_kind not in allowed_pairs[request.operator_kind]:
        findings.append({"rule_id": "operator_event_blocks_permission_escalation", "severity": "hard_fail", "message": "Operator action is outside the granted operator class."})
    if request.action_kind in {"browser_click", "browser_type", "desktop_click", "terminal_command", "file_write", "mcp_tool_call"} and request.target_confidence < 0.75:
        findings.append({"rule_id": "operator_event_requires_target_confidence", "severity": "hard_fail", "message": "High-authority actions require target confidence of at least 0.75."})
    if request.action_kind in {"browser_click", "browser_type", "desktop_click", "terminal_command", "file_write", "mcp_tool_call"} and not request.evidence_refs:
        findings.append({"rule_id": "operator_event_requires_evidence_refs", "severity": "hard_fail", "message": "High-authority actions require evidence references."})
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/operator-events"},
        "record": {"method": "POST", "endpoint": "/ops/brain/operator-events"},
    }
```

- [ ] **Step 6: Export, wire service, and wire API**

Update exports in `nexusnet/browser/__init__.py` and `nexusnet/vision/__init__.py`.

Add service fields:

```python
    brain_browser_profile_policy: Any
    brain_operator_events: Any
```

Instantiate with `paths.artifacts_dir`.

Add API endpoints:

```python
    @application.get("/ops/brain/browser/profile-policy")
    def ops_brain_browser_profile_policy():
        return services.brain_browser_profile_policy.summary()

    @application.post("/ops/brain/browser/profile-policy")
    def ops_brain_browser_profile_policy_evaluate(payload: dict[str, Any] = Body(...)):
        return services.brain_browser_profile_policy.evaluate(BrowserProfilePolicyRequest.model_validate(payload))

    @application.get("/ops/brain/operator-events")
    def ops_brain_operator_events():
        return services.brain_operator_events.summary()

    @application.post("/ops/brain/operator-events")
    def ops_brain_operator_events_record(payload: dict[str, Any] = Body(...)):
        return services.brain_operator_events.record(OperatorEventRequest.model_validate(payload))
```

- [ ] **Step 7: Run tests**

Run:

```powershell
pytest tests/test_operator_permission_events.py tests/test_browser_context_memory.py tests/test_multimodal_computer_use.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit this task only**

Run:

```powershell
git add nexusnet/browser/profile_policy.py nexusnet/browser/__init__.py nexusnet/vision/operator_events.py nexusnet/vision/__init__.py nexus/services.py nexus/api/app.py tests/test_operator_permission_events.py
git commit -m "feat: add governed operator event receipts"
```

---

### Task 6: Edge Model Passport And Certification

**Files:**
- Create: `nexusnet/runtime/model_passport.py`
- Modify: `nexusnet/runtime/__init__.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_edge_model_certification.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `QuantizationCatalog`, `assign_model`, `NexusServices`, and `create_app`.

Expected: risk is MEDIUM because this adds a runtime surface and API endpoints.

- [ ] **Step 2: Write failing tests**

Create `tests/test_edge_model_certification.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.model_passport import EdgeModelCertificationRegistry, ModelPassportRequest, CertificationRunRequest
from tests.test_nexus_phase1_foundation import make_project


def test_model_passport_records_bounded_task_strengths_and_refusals():
    registry = EdgeModelCertificationRegistry()

    passport = registry.register_passport(
        ModelPassportRequest(
            model_id="LiquidAI/LFM2.5-350M",
            parameter_count=350_000_000,
            context_tokens=32768,
            runtime_formats=["onnx", "gguf"],
            memory_budget_mb=768,
            latency_envelope_ms={"p50_decode": 35.0},
            task_strengths=["structured_output", "tool_call_formatting"],
            task_refusals=["knowledge_intensive_programming", "high_stakes_factual_recall"],
            license_status="needs_review",
            provenance_refs=["https://huggingface.co/LiquidAI/LFM2.5-350M"],
        )
    )

    assert passport["status"] == "registered"
    assert passport["deployment_boundary"] == "task-certified-edge-model-not-default-brain"
    assert "knowledge_intensive_programming" in passport["task_refusals"]


def test_certification_blocks_knowledge_task_without_retrieval_support():
    registry = EdgeModelCertificationRegistry()
    registry.register_passport(
        {
            "model_id": "edge-small",
            "parameter_count": 350_000_000,
            "context_tokens": 8192,
            "runtime_formats": ["onnx"],
            "memory_budget_mb": 512,
            "latency_envelope_ms": {"p50_decode": 40.0},
            "task_strengths": ["structured_output"],
            "task_refusals": ["knowledge_intensive_programming"],
            "license_status": "approved",
            "provenance_refs": ["source::model-card"],
        }
    )

    run = registry.certify(
        CertificationRunRequest(
            run_id="cert::edge-small",
            model_id="edge-small",
            scenarios=["extraction", "tool_call_formatting", "knowledge_intensive_programming"],
            device_matrix={"desktop_cpu": {"latency_ms": 42, "memory_mb": 410}},
            benchmark_refs=["eval::edge-small"],
            retrieval_support_enabled=False,
            evidence_refs=["artifact::benchmark"],
        )
    )

    assert run["status"] == "blocked"
    assert "certification_blocks_refused_task_without_support" in {finding["rule_id"] for finding in run["findings"]}


def test_model_certification_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    passport = client.post(
        "/ops/brain/model-passports",
        json={
            "model_id": "edge-api",
            "parameter_count": 350000000,
            "context_tokens": 8192,
            "runtime_formats": ["onnx"],
            "memory_budget_mb": 512,
            "latency_envelope_ms": {"p50_decode": 45},
            "task_strengths": ["extraction"],
            "task_refusals": ["high_stakes_factual_recall"],
            "license_status": "approved",
            "provenance_refs": ["source::api"],
        },
    )
    assert passport.status_code == 200
    assert passport.json()["status"] == "registered"

    summary = client.get("/ops/brain/model-passports")
    assert summary.status_code == 200
    assert summary.json()["passport_count"] == 1
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_edge_model_certification.py -q
```

Expected: failure because `model_passport.py` does not exist.

- [ ] **Step 4: Implement model passport registry**

Create `nexusnet/runtime/model_passport.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


LicenseStatus = Literal["approved", "needs_review", "blocked"]


class ModelPassportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    parameter_count: int
    active_parameter_count: int | None = None
    context_tokens: int
    runtime_formats: list[str] = Field(default_factory=list)
    memory_budget_mb: int
    latency_envelope_ms: dict[str, float] = Field(default_factory=dict)
    task_strengths: list[str] = Field(default_factory=list)
    task_refusals: list[str] = Field(default_factory=list)
    license_status: LicenseStatus = "needs_review"
    provenance_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CertificationRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    model_id: str
    scenarios: list[str] = Field(default_factory=list)
    device_matrix: dict[str, Any] = Field(default_factory=dict)
    benchmark_refs: list[str] = Field(default_factory=list)
    retrieval_support_enabled: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EdgeModelCertificationRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "runtime" / "model-passports" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._passports: dict[str, dict[str, Any]] = {}
        self._runs: list[dict[str, Any]] = []

    def register_passport(self, request: ModelPassportRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ModelPassportRequest) else ModelPassportRequest.model_validate(request)
        passport = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "edge-model-certification",
            "model_id": normalized.model_id,
            "status": "registered" if normalized.license_status != "blocked" else "blocked",
            "created_at": utcnow().isoformat(),
            "parameter_count": normalized.parameter_count,
            "active_parameter_count": normalized.active_parameter_count,
            "context_tokens": normalized.context_tokens,
            "runtime_formats": normalized.runtime_formats,
            "memory_budget_mb": normalized.memory_budget_mb,
            "latency_envelope_ms": normalized.latency_envelope_ms,
            "task_strengths": normalized.task_strengths,
            "task_refusals": normalized.task_refusals,
            "license_status": normalized.license_status,
            "provenance_refs": normalized.provenance_refs,
            "deployment_boundary": "task-certified-edge-model-not-default-brain",
            "metadata": normalized.metadata,
        }
        self._passports[passport["model_id"]] = passport
        self._persist("passport", passport["model_id"], passport)
        return passport

    def certify(self, request: CertificationRunRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, CertificationRunRequest) else CertificationRunRequest.model_validate(request)
        passport = self._passports.get(normalized.model_id)
        findings = _certification_findings(normalized, passport)
        run = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "edge-model-certification",
            "run_id": normalized.run_id,
            "model_id": normalized.model_id,
            "status": "blocked" if findings else "certified-shadow",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "scenarios": normalized.scenarios,
            "device_matrix": normalized.device_matrix,
            "benchmark_refs": normalized.benchmark_refs,
            "retrieval_support_enabled": normalized.retrieval_support_enabled,
            "evidence_refs": normalized.evidence_refs,
            "passport_snapshot": passport,
            "findings": findings,
            "certification_boundary": "certified-by-task-and-device-not-global-model-reputation",
            "metadata": normalized.metadata,
        }
        self._runs.insert(0, run)
        self._runs = self._runs[:50]
        self._persist("certification", run["run_id"], run)
        return run

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "edge-model-certification",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(run.get("status") == "blocked" for run in self._runs) else ("live-bound" if self._passports or self._runs else "static-canon"),
            "passport_count": len(self._passports),
            "certification_count": len(self._runs),
            "passports": list(self._passports.values()),
            "latest_certification": self._runs[0] if self._runs else None,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, prefix: str, record_id: str, payload: dict[str, Any]) -> None:
        if self.records_dir is None:
            return
        path = self.records_dir / f"{prefix}_{record_id.replace(':', '_').replace('/', '_')}.json"
        payload["artifact_path"] = str(path)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _certification_findings(request: CertificationRunRequest, passport: dict[str, Any] | None) -> list[dict[str, str]]:
    findings = []
    if passport is None:
        findings.append({"rule_id": "certification_requires_model_passport", "severity": "hard_fail", "message": "Certification requires a registered model passport."})
        return findings
    refused = set(passport.get("task_refusals") or [])
    requested_refused = refused & set(request.scenarios)
    if requested_refused and not request.retrieval_support_enabled:
        findings.append({"rule_id": "certification_blocks_refused_task_without_support", "severity": "hard_fail", "message": "Refused task scenarios require retrieval or teacher support."})
    if not request.benchmark_refs:
        findings.append({"rule_id": "certification_requires_benchmark_refs", "severity": "hard_fail", "message": "Certification requires benchmark references."})
    if not request.device_matrix:
        findings.append({"rule_id": "certification_requires_device_matrix", "severity": "hard_fail", "message": "Certification requires device matrix evidence."})
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/model-passports"},
        "register_passport": {"method": "POST", "endpoint": "/ops/brain/model-passports"},
        "certify": {"method": "POST", "endpoint": "/ops/brain/model-certifications"},
    }
```

- [ ] **Step 5: Export and wire**

Update `nexusnet/runtime/__init__.py` lazy exports for:

```python
"EdgeModelCertificationRegistry",
"ModelPassportRequest",
"CertificationRunRequest",
```

Add `__getattr__` cases importing from `.model_passport`.

Wire service and API:

```python
from nexusnet.runtime.model_passport import CertificationRunRequest, EdgeModelCertificationRegistry, ModelPassportRequest
```

Add `brain_edge_model_certification: Any` to `NexusServices`, instantiate with `paths.artifacts_dir`, and add endpoints:

```python
    @application.get("/ops/brain/model-passports")
    def ops_brain_model_passports():
        return services.brain_edge_model_certification.summary()

    @application.post("/ops/brain/model-passports")
    def ops_brain_model_passports_register(payload: dict[str, Any] = Body(...)):
        return services.brain_edge_model_certification.register_passport(ModelPassportRequest.model_validate(payload))

    @application.post("/ops/brain/model-certifications")
    def ops_brain_model_certifications(payload: dict[str, Any] = Body(...)):
        return services.brain_edge_model_certification.certify(CertificationRunRequest.model_validate(payload))
```

- [ ] **Step 6: Run tests**

Run:

```powershell
pytest tests/test_edge_model_certification.py tests/test_quantization_catalog.py tests/test_hive_model_growth_engine.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit this task only**

Run:

```powershell
git add nexusnet/runtime/model_passport.py nexusnet/runtime/__init__.py nexus/services.py nexus/api/app.py tests/test_edge_model_certification.py
git commit -m "feat: add edge model certification passports"
```

---

### Task 7: Concept Telemetry Plane

**Files:**
- Create: `nexusnet/telemetry/concept_plane.py`
- Modify: `nexusnet/telemetry/__init__.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_concept_telemetry_plane.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `GenAITraceRegistry`, `NexusEngramIndex`, `NexusServices`, and `create_app`.

Expected: risk is MEDIUM because this adds a telemetry surface and API endpoints.

- [ ] **Step 2: Write failing tests**

Create `tests/test_concept_telemetry_plane.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.telemetry import ConceptTelemetryRegistry, ConceptTelemetryRequest, SAEExperimentRequest
from tests.test_nexus_phase1_foundation import make_project


def test_concept_telemetry_records_behavioral_proxy_without_activation_claim():
    registry = ConceptTelemetryRegistry()

    record = registry.record_concept(
        ConceptTelemetryRequest(
            concept_id="concept::source-confidence",
            trace_refs=["trace::1"],
            labels=["source_confidence", "uncertainty"],
            concept_kind="behavioral_proxy",
            confidence=0.82,
            safety_flags=["hallucination-risk"],
            contains_private_data=False,
        )
    )

    assert record["status"] == "recorded"
    assert record["concept_kind"] == "behavioral_proxy"
    assert record["activation_claim_allowed"] is False


def test_concept_telemetry_blocks_activation_claim_without_open_model_record():
    registry = ConceptTelemetryRegistry()

    record = registry.record_concept(
        {
            "concept_id": "concept::closed-model-activation",
            "trace_refs": ["trace::closed"],
            "labels": ["deception"],
            "concept_kind": "activation_feature",
            "confidence": 0.9,
            "safety_flags": [],
            "contains_private_data": False,
        }
    )

    assert record["status"] == "blocked"
    assert "activation_features_require_sae_experiment" in {finding["rule_id"] for finding in record["findings"]}


def test_sae_experiment_records_research_only_open_model_metadata():
    registry = ConceptTelemetryRegistry()

    experiment = registry.record_sae_experiment(
        SAEExperimentRequest(
            experiment_id="sae::mistral-layer-12",
            model_id="mistral-open",
            layer="12",
            token_count=4096,
            activation_capture_method="local_forward_hooks",
            sae_config={"hidden_dim": 8192, "sparsity": 0.05},
            reconstruction_metrics={"loss": 0.12},
            feature_examples=["source confidence feature"],
            evidence_refs=["artifact::sae-run"],
        )
    )

    assert experiment["status"] == "research-only"
    assert experiment["closed_model_boundary"] == "no-closed-model-internals-from-output-only-traces"


def test_concept_telemetry_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/concept-telemetry/concepts",
        json={
            "concept_id": "concept::api",
            "trace_refs": ["trace::api"],
            "labels": ["uncertainty"],
            "concept_kind": "behavioral_proxy",
            "confidence": 0.7,
            "safety_flags": [],
            "contains_private_data": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    summary = client.get("/ops/brain/concept-telemetry")
    assert summary.status_code == 200
    assert summary.json()["concept_count"] == 1
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_concept_telemetry_plane.py -q
```

Expected: failure because `concept_plane.py` does not exist.

- [ ] **Step 4: Implement concept plane**

Create `nexusnet/telemetry/concept_plane.py` with a `ConceptTelemetryRegistry` that:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ConceptKind = Literal["behavioral_proxy", "activation_feature"]


class ConceptTelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concept_id: str
    trace_refs: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    concept_kind: ConceptKind = "behavioral_proxy"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    safety_flags: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    sae_experiment_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SAEExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    model_id: str
    layer: str
    token_count: int
    activation_capture_method: str
    sae_config: dict[str, Any] = Field(default_factory=dict)
    reconstruction_metrics: dict[str, float] = Field(default_factory=dict)
    feature_examples: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

Implement methods `record_concept`, `record_sae_experiment`, and `summary`. Use these findings:

```python
def _concept_findings(request: ConceptTelemetryRequest) -> list[dict[str, str]]:
    findings = []
    if request.concept_kind == "activation_feature" and not request.sae_experiment_ref:
        findings.append({"rule_id": "activation_features_require_sae_experiment", "severity": "hard_fail", "message": "Activation-feature claims require an SAE experiment reference."})
    if request.contains_private_data:
        findings.append({"rule_id": "concept_telemetry_blocks_private_content_capture", "severity": "hard_fail", "message": "Concept telemetry stores labels and trace refs only, not private content."})
    return findings
```

Set concept payload fields:

```python
            "activation_claim_allowed": normalized.concept_kind == "activation_feature" and not findings,
            "manifold_caution_label": "behavioral_proxy_not_internal_activation" if normalized.concept_kind == "behavioral_proxy" else "activation_experiment_required",
```

Set SAE experiment fields:

```python
            "status": "research-only",
            "closed_model_boundary": "no-closed-model-internals-from-output-only-traces",
            "promotion_allowed": False,
```

- [ ] **Step 5: Export, wire service, and wire API**

Export `ConceptTelemetryRegistry`, `ConceptTelemetryRequest`, and `SAEExperimentRequest`.

Add service field `brain_concept_telemetry: Any`, instantiate with `paths.artifacts_dir`, and add endpoints:

```python
    @application.get("/ops/brain/concept-telemetry")
    def ops_brain_concept_telemetry():
        return services.brain_concept_telemetry.summary()

    @application.post("/ops/brain/concept-telemetry/concepts")
    def ops_brain_concept_telemetry_concepts(payload: dict[str, Any] = Body(...)):
        return services.brain_concept_telemetry.record_concept(ConceptTelemetryRequest.model_validate(payload))

    @application.post("/ops/brain/concept-telemetry/sae-experiments")
    def ops_brain_concept_telemetry_sae(payload: dict[str, Any] = Body(...)):
        return services.brain_concept_telemetry.record_sae_experiment(SAEExperimentRequest.model_validate(payload))
```

- [ ] **Step 6: Run tests**

Run:

```powershell
pytest tests/test_concept_telemetry_plane.py tests/test_genai_observability_registry.py tests/test_engram_memory_index.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit this task only**

Run:

```powershell
git add nexusnet/telemetry/concept_plane.py nexusnet/telemetry/__init__.py nexus/services.py nexus/api/app.py tests/test_concept_telemetry_plane.py
git commit -m "feat: add concept telemetry plane"
```

---

### Task 8: Codegraph Required Context Gate

**Files:**
- Create: `nexusnet/operations/codegraph_gate.py`
- Modify: `nexusnet/operations/__init__.py`
- Modify: `nexusnet/policy/kernel.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Create: `tests/test_codegraph_gate.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `PolicyKernel`, `AgenticPipelineRuntime`, `NexusServices`, and `create_app`.

Expected: risk is MEDIUM because code-change policy expands.

- [ ] **Step 2: Write failing tests**

Create `tests/test_codegraph_gate.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.codegraph_gate import CodegraphGate, CodegraphRunManifestRequest
from nexusnet.policy import PolicyKernel
from tests.test_nexus_phase1_foundation import make_project


def test_codegraph_gate_blocks_code_edit_without_impact_evidence():
    gate = CodegraphGate()

    report = gate.evaluate(
        CodegraphRunManifestRequest(
            manifest_id="codegraph::missing-impact",
            run_kind="code_edit",
            indexed_repo="NexusNet",
            indexed_commit="abc",
            worktree_commit="def",
            graph_query_ref="gitnexus::query::policy",
            impact_target="PolicyKernel",
            impact_risk="missing",
            affected_processes=[],
            detect_changes_ref="",
        )
    )

    assert report["status"] == "blocked"
    assert "codegraph_gate_requires_impact_evidence" in {finding["rule_id"] for finding in report["findings"]}
    assert "codegraph_gate_blocks_stale_index" in {finding["rule_id"] for finding in report["findings"]}


def test_codegraph_gate_allows_docs_only_without_impact_target():
    gate = CodegraphGate()

    report = gate.evaluate(
        {
            "manifest_id": "codegraph::docs",
            "run_kind": "docs_only",
            "indexed_repo": "NexusNet",
            "indexed_commit": "abc",
            "worktree_commit": "abc",
            "graph_query_ref": "",
            "impact_target": "",
            "impact_risk": "not_required",
            "affected_processes": [],
            "detect_changes_ref": "gitnexus::detect::docs",
        }
    )

    assert report["status"] == "allowed"
    assert report["policy_boundary"] == "code-affecting-runs-require-current-graph-impact-and-detect-changes"


def test_policy_kernel_blocks_code_change_missing_codegraph_manifest():
    report = PolicyKernel.default().scan(
        [
            {
                "target_id": "code::planner",
                "target_type": "code_change",
                "metadata": {"tests_provided": True, "codegraph_manifest_ref": ""},
            }
        ]
    )

    assert report.summary.allow_merge is False
    assert "code_change_requires_codegraph_manifest" in {finding.rule_id for finding in report.findings}


def test_codegraph_gate_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/codegraph-gate/manifests",
        json={
            "manifest_id": "codegraph::api",
            "run_kind": "code_edit",
            "indexed_repo": "NexusNet",
            "indexed_commit": "abc",
            "worktree_commit": "abc",
            "graph_query_ref": "gitnexus::query::api",
            "impact_target": "RetrievalPlanner",
            "impact_risk": "LOW",
            "affected_processes": ["retrieval planning"],
            "detect_changes_ref": "gitnexus::detect::api",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "allowed"
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_codegraph_gate.py -q
```

Expected: failure because codegraph gate module and policy rule do not exist.

- [ ] **Step 4: Implement codegraph gate**

Create `nexusnet/operations/codegraph_gate.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


RunKind = Literal["code_edit", "docs_only", "research_only"]
ImpactRisk = Literal["missing", "not_required", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


class CodegraphRunManifestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_id: str
    run_kind: RunKind
    indexed_repo: str
    indexed_commit: str
    worktree_commit: str
    graph_query_ref: str = ""
    impact_target: str = ""
    impact_risk: ImpactRisk = "missing"
    affected_processes: list[str] = Field(default_factory=list)
    detect_changes_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CodegraphGate:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "operations" / "codegraph-gate" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def evaluate(self, request: CodegraphRunManifestRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, CodegraphRunManifestRequest) else CodegraphRunManifestRequest.model_validate(request)
        findings = _findings(normalized)
        report = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "codegraph-gate",
            "manifest_id": normalized.manifest_id,
            "run_kind": normalized.run_kind,
            "indexed_repo": normalized.indexed_repo,
            "indexed_commit": normalized.indexed_commit,
            "worktree_commit": normalized.worktree_commit,
            "status": "blocked" if findings else "allowed",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "graph_query_ref": normalized.graph_query_ref,
            "impact_target": normalized.impact_target,
            "impact_risk": normalized.impact_risk,
            "affected_processes": normalized.affected_processes,
            "detect_changes_ref": normalized.detect_changes_ref,
            "findings": findings,
            "policy_boundary": "code-affecting-runs-require-current-graph-impact-and-detect-changes",
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(report)
        return report

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._records[:limit]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "codegraph-gate",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in records) else ("live-bound" if records else "static-canon"),
            "manifest_count": len(records),
            "latest_manifest": records[0] if records else None,
            "manifests": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, report: dict[str, Any]) -> None:
        self._records.insert(0, report)
        self._records = self._records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{report['manifest_id'].replace(':', '_')}.json"
            report["artifact_path"] = str(path)
            path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _findings(request: CodegraphRunManifestRequest) -> list[dict[str, str]]:
    findings = []
    if request.run_kind == "code_edit" and request.impact_risk == "missing":
        findings.append({"rule_id": "codegraph_gate_requires_impact_evidence", "severity": "hard_fail", "message": "Code edits require GitNexus impact evidence."})
    if request.run_kind == "code_edit" and request.indexed_commit != request.worktree_commit:
        findings.append({"rule_id": "codegraph_gate_blocks_stale_index", "severity": "hard_fail", "message": "Codegraph index commit differs from worktree commit."})
    if request.run_kind == "code_edit" and not request.detect_changes_ref:
        findings.append({"rule_id": "codegraph_gate_requires_detect_changes", "severity": "hard_fail", "message": "Code edits require detect-changes evidence before commit."})
    if request.impact_risk in {"HIGH", "CRITICAL"}:
        findings.append({"rule_id": "codegraph_gate_requires_manual_review_for_high_risk", "severity": "hard_fail", "message": "High or critical impact changes require manual review."})
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/codegraph-gate"},
        "evaluate": {"method": "POST", "endpoint": "/ops/brain/codegraph-gate/manifests"},
    }
```

- [ ] **Step 5: Add policy rule**

In `PolicyKernel.default()`, add:

```python
                PolicyRule(
                    rule_id="code_change_requires_codegraph_manifest",
                    title="Code changes require codegraph manifest evidence",
                    severity="hard_fail",
                    target_types=["code_change"],
                    description="Blocks code-affecting changes that do not carry GitNexus graph, impact, and detect-changes evidence.",
                    required_evidence=["codegraph_manifest_ref"],
                    promotion_gate="codegraph-required-context-gate",
                ),
```

Add to `_evaluate_rule`:

```python
        if rule.rule_id == "code_change_requires_codegraph_manifest":
            if not metadata.get("codegraph_manifest_ref"):
                return "Code change is missing codegraph manifest evidence."
```

- [ ] **Step 6: Export, wire service, and wire API**

Export `CodegraphGate` and `CodegraphRunManifestRequest` from `nexusnet/operations/__init__.py`.

Add service field `brain_codegraph_gate: Any`, instantiate with `paths.artifacts_dir`, and add endpoints:

```python
    @application.get("/ops/brain/codegraph-gate")
    def ops_brain_codegraph_gate():
        return services.brain_codegraph_gate.summary()

    @application.post("/ops/brain/codegraph-gate/manifests")
    def ops_brain_codegraph_gate_manifests(payload: dict[str, Any] = Body(...)):
        return services.brain_codegraph_gate.evaluate(CodegraphRunManifestRequest.model_validate(payload))
```

- [ ] **Step 7: Run tests**

Run:

```powershell
pytest tests/test_codegraph_gate.py tests/test_policy_kernel.py tests/test_agentic_pipeline_runtime.py -q
```

Expected: existing `code_change_requires_tests` expectations may need one additional `codegraph_manifest_ref` in test payloads. Update test fixtures with `codegraph_manifest_ref: "gitnexus::manifest::test"` where they are intentionally safe.

- [ ] **Step 8: Commit this task only**

Run:

```powershell
git add nexusnet/operations/codegraph_gate.py nexusnet/operations/__init__.py nexusnet/policy/kernel.py nexus/services.py nexus/api/app.py tests/test_codegraph_gate.py tests/test_policy_kernel.py tests/test_agentic_pipeline_runtime.py
git commit -m "feat: add codegraph required context gate"
```

---

### Task 9: Control Panel Integration

**Files:**
- Modify: `nexus/api/app.py`
- Modify: `ui/control-panel/index.html`
- Modify: `ui/control-panel/app.js`
- Modify: `ui/control-panel/styles.css`
- Create: `tests/test_video_assimilation_control_panel.py`

- [ ] **Step 1: Run impact analysis**

Run GitNexus impact for `create_app`. Use API impact for `/ops/brain/visualizer/state` if GitNexus exposes route impact.

Expected: risk is MEDIUM or HIGH because Control Panel state is broad. If HIGH, pause and review the UI/API patch plan before editing.

- [ ] **Step 2: Write failing tests**

Create `tests/test_video_assimilation_control_panel.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_video_assimilation_surfaces_are_visible_in_control_panel(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Video Assimilation" in ui.text
    assert "videoAssimilationScorecard" in ui.text
    assert "retrievalPlannerScorecard" in ui.text
    assert "operatorEventsScorecard" in ui.text
    assert "conceptTelemetryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/brain/canon/video-assimilation-targets" in app_js
    assert "/ops/brain/retrieval/planner" in app_js
    assert "/ops/brain/operator-events" in app_js
    assert "/ops/brain/concept-telemetry" in app_js
    assert "renderVideoAssimilationScorecard" in app_js


def test_visualizer_overlay_contains_new_assimilation_scorecards(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "video-assimilation-ui"})

    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert "video_assimilation_scorecard" in control_panel
    assert "retrieval_planner_scorecard" in control_panel
    assert "codegraph_gate_scorecard" in control_panel
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```powershell
pytest tests/test_video_assimilation_control_panel.py -q
```

Expected: failure because UI ids and visualizer overlay keys do not exist.

- [ ] **Step 4: Add visualizer overlay keys**

Find the Control Panel overlay payload in `nexus/api/app.py` and add these keys to the existing `control_panel` object:

```python
                "video_assimilation_scorecard": services.brain_assimilation_targets.video_scorecard(session_id=session_id),
                "retrieval_planner_scorecard": services.brain_retrieval_planner.summary(),
                "self_improvement_lineage_scorecard": services.brain_self_improvement_lineage.summary(),
                "verifier_search_scorecard": services.brain_verifier_search.summary(),
                "browser_profile_policy_scorecard": services.brain_browser_profile_policy.summary(),
                "operator_events_scorecard": services.brain_operator_events.summary(),
                "edge_model_certification_scorecard": services.brain_edge_model_certification.summary(),
                "concept_telemetry_scorecard": services.brain_concept_telemetry.summary(),
                "codegraph_gate_scorecard": services.brain_codegraph_gate.summary(),
```

- [ ] **Step 5: Add HTML containers**

Add a new section in `ui/control-panel/index.html` near existing governance/evolution scorecard sections:

```html
      <section class="evolution-dossier-deck">
        <div class="panel-head compact">
          <div>
            <div class="eyebrow">Video Assimilation</div>
            <h3>Targets, Source Status, Shadow Gates, Operator Surfaces</h3>
          </div>
        </div>
        <div id="videoAssimilationScorecard" class="evolution-dossier-grid"></div>
        <div id="retrievalPlannerScorecard" class="evolution-dossier-grid"></div>
        <div id="operatorEventsScorecard" class="evolution-dossier-grid"></div>
        <div id="conceptTelemetryScorecard" class="evolution-dossier-grid"></div>
      </section>
```

- [ ] **Step 6: Add JS state and endpoints**

In `ui/control-panel/app.js`, add DOM ids:

```javascript
  videoAssimilationScorecard: document.getElementById("videoAssimilationScorecard"),
  retrievalPlannerScorecard: document.getElementById("retrievalPlannerScorecard"),
  operatorEventsScorecard: document.getElementById("operatorEventsScorecard"),
  conceptTelemetryScorecard: document.getElementById("conceptTelemetryScorecard"),
```

Add state keys:

```javascript
  videoAssimilation: null,
  retrievalPlanner: null,
  operatorEvents: null,
  conceptTelemetry: null,
```

Add endpoints:

```javascript
  videoAssimilation: "/ops/brain/canon/video-assimilation-targets",
  retrievalPlanner: "/ops/brain/retrieval/planner",
  operatorEvents: "/ops/brain/operator-events",
  conceptTelemetry: "/ops/brain/concept-telemetry",
```

Add render functions using the existing card/list helpers:

```javascript
function renderVideoAssimilationScorecard(payload) {
  renderScorecard(dom.videoAssimilationScorecard, "Video Assimilation", payload, [
    ["Targets", payload?.target_count],
    ["Primary Verified", payload?.coverage_summary?.primary_verified_count],
    ["Shadow", payload?.coverage_summary?.shadow_only_count],
    ["Clean Room", payload?.coverage_summary?.clean_room_required_count],
  ]);
}

function renderRetrievalPlannerScorecard(payload) {
  renderScorecard(dom.retrievalPlannerScorecard, "Retrieval Planner", payload, [
    ["Plans", payload?.plan_count],
    ["Blocked", payload?.blocked_count],
    ["Runtime", payload?.runtime_state],
  ]);
}

function renderOperatorEventsScorecard(payload) {
  renderScorecard(dom.operatorEventsScorecard, "Operator Events", payload, [
    ["Events", payload?.event_count],
    ["Blocked", payload?.blocked_count],
    ["Runtime", payload?.runtime_state],
  ]);
}

function renderConceptTelemetryScorecard(payload) {
  renderScorecard(dom.conceptTelemetryScorecard, "Concept Telemetry", payload, [
    ["Concepts", payload?.concept_count],
    ["SAE Experiments", payload?.sae_experiment_count],
    ["Runtime", payload?.runtime_state],
  ]);
}
```

Add these render calls wherever existing scorecards are rendered:

```javascript
  renderVideoAssimilationScorecard(state.videoAssimilation);
  renderRetrievalPlannerScorecard(state.retrievalPlanner);
  renderOperatorEventsScorecard(state.operatorEvents);
  renderConceptTelemetryScorecard(state.conceptTelemetry);
```

- [ ] **Step 7: Add compact CSS**

Add to `ui/control-panel/styles.css`:

```css
#videoAssimilationScorecard,
#retrievalPlannerScorecard,
#operatorEventsScorecard,
#conceptTelemetryScorecard {
  min-height: 120px;
}
```

- [ ] **Step 8: Run tests**

Run:

```powershell
pytest tests/test_video_assimilation_control_panel.py tests/test_policy_kernel.py tests/test_multimodal_computer_use.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit this task only**

Run:

```powershell
git add nexus/api/app.py ui/control-panel/index.html ui/control-panel/app.js ui/control-panel/styles.css tests/test_video_assimilation_control_panel.py
git commit -m "feat: expose video assimilation in control panel"
```

---

### Task 10: End-To-End Verification And Run Log

**Files:**
- Modify: `docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md`

- [ ] **Step 1: Run targeted test suite**

Run:

```powershell
pytest `
  tests/test_video_assimilation_targets.py `
  tests/test_synthetic_truth_guard.py `
  tests/test_retrieval_planner.py `
  tests/test_assimilation_lineage_verifier_search.py `
  tests/test_operator_permission_events.py `
  tests/test_edge_model_certification.py `
  tests/test_concept_telemetry_plane.py `
  tests/test_codegraph_gate.py `
  tests/test_video_assimilation_control_panel.py `
  -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run existing adjacent regression tests**

Run:

```powershell
pytest `
  tests/test_policy_kernel.py `
  tests/test_memory_quality_ledger.py `
  tests/test_knowledge_artifact_compiler.py `
  tests/test_browser_context_memory.py `
  tests/test_multimodal_computer_use.py `
  tests/test_eval_registry.py `
  tests/test_self_improvement_layer.py `
  tests/test_quantization_catalog.py `
  tests/test_claude_code_assimilation_targets.py `
  -q
```

Expected: all selected tests pass.

- [ ] **Step 3: Run path and placeholder safety scan**

Run:

```powershell
$patterns = @("[A-Za-z]:\\\\", "uri-scheme-file", "placeholder-token", "deferred-detail")
foreach ($pattern in $patterns) {
  rg -n $pattern `
    docs/assimilation/videos/2026-05-06 `
    docs/superpowers/plans/2026-05-06-video-assimilation-implementation.md `
    docs/autonomous/TASK_SCOPE_2026_VIDEO_ASSIMILATION_IMPLEMENTATION.md `
    docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md `
    nexusnet nexus ui tests
}
```

Expected: no new matches from files touched by this implementation. Pre-existing matches in unrelated dirty files must be logged and left untouched.

- [ ] **Step 4: Run GitNexus detect changes**

Run GitNexus detect changes for repo `NexusNet`, scope `all`.

Expected: changes are limited to the planned surfaces. If affected execution flows include unrelated surfaces, record them in the run log and inspect before commit.

- [ ] **Step 5: Update run log**

Append to `docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md`:

```markdown
## Completion Evidence

Implemented surfaces:

- Video assimilation target ledger.
- Synthetic truth guard source-status gate.
- Agentic retrieval planner.
- Self-improvement lineage and verifier search.
- Operator event receipts and browser profile policy.
- Edge model passport/certification.
- Concept telemetry plane.
- Codegraph required context gate.
- Control Panel visibility.

Verification:

- Targeted video assimilation tests: pass.
- Adjacent governance/retrieval/operator/runtime tests: pass.
- Path and placeholder scan: pass for touched files.
- GitNexus detect changes: reviewed before commit.

Remaining boundaries:

- External repos remain source references only.
- Self-improvement, verifier search, generated surfaces, computer-use actions, and edge model certification remain shadow/refs-only until operator promotion gates pass.
```

- [ ] **Step 6: Commit final log update**

Run:

```powershell
git add docs/autonomous/VIDEO_ASSIMILATION_RUN_LOG.md
git commit -m "docs: record video assimilation verification"
```

---

## Self-Review Checklist

Coverage:

- Synthetic Truth Guard is covered by Task 2.
- DGM, Space Agent, and AlphaEvolve self-improvement/search mechanics are covered by Task 4.
- Agentic RAG is covered by Task 3.
- Jarvis and TARS operator patterns are covered by Task 5 and Task 9.
- Edge small model training and certification is covered by Task 6.
- Black-box interpretability/concept telemetry is covered by Task 7.
- GitNexus codegraph gating is covered by Task 8.
- Control Panel implementation is covered by Task 9.

Implementation boundaries:

- No external implementation code is imported.
- Every high-authority feature is gated, shadow-only, or refs-only.
- Every task has a focused test entrypoint.
- Existing dirty-tree work is protected by task-local staging.

Execution order:

- Task 0 must run first.
- Task 1 and Task 2 must run before Task 9.
- Tasks 3 through 8 can run independently after Task 0.
- Task 9 runs after Tasks 1 through 8.
- Task 10 runs last.
