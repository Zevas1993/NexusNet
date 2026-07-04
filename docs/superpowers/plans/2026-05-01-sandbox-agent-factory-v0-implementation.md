# Sandcastle-Style AFK Sandbox Agent Factory v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `PB-2026-05-01-015 - Sandcastle-Style AFK Sandbox Agent Factory` as a source-backed post-book assimilation target and implement a Nexus-native v0 runtime that plans AFK coding-agent work inside governed sandbox/worktree lanes.

**Architecture:** NexusNet will assimilate the Sandcastle pattern without depending on the npm package directly. A new `SandboxAgentFactory` runtime produces deterministic run manifests, backlog/task selection, branch/worktree plans, planner/implementer/reviewer/merger blocks, policy scans, checkpoint metadata, and artifact ledgers. API and Control Panel surfaces expose the factory while promotion remains gated by sandbox, tests, review, rollback, and operator policy.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, existing NexusNet service wiring, existing PolicyKernel, static Control Panel JavaScript.

---

## File Structure

- Create `nexusnet/agents/sandbox_factory.py`
  - Owns `SandboxAgentFactory`, request schemas, manifest creation, policy gating, artifact persistence, summary, and scorecard.
- Modify `nexusnet/agents/__init__.py`
  - Exports the new runtime and request models.
- Modify `nexus/services.py`
  - Instantiates `brain_sandbox_agent_factory`.
- Modify `nexus/api/app.py`
  - Adds `/ops/brain/sandbox-agent-factory` runtime routes.
- Modify `nexusnet/operations/assimilation_targets.py`
  - Adds Sandcastle source refs and assimilation target.
- Modify `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
  - Adds `PB-2026-05-01-015`.
- Modify `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
  - Adds ledger row for `PB-2026-05-01-015`.
- Modify `ui/control-panel/index.html`
  - Adds a Sandbox Agent Factory panel.
- Modify `ui/control-panel/app.js`
  - Fetches and renders `/ops/brain/canon/sandbox-agent-factory`.
- Create `tests/test_sandbox_agent_factory.py`
  - Proves runtime, policy block, API, Control Panel, and assimilation target visibility.

## Task 1: Runtime Contract Tests

**Files:**
- Create: `tests/test_sandbox_agent_factory.py`
- Later create: `nexusnet/agents/sandbox_factory.py`

- [x] **Step 1: Write failing runtime tests**

```python
from pathlib import Path

from nexusnet.agents import SandboxAgentFactory, SandboxAgentFactoryRunRequest


def test_sandbox_agent_factory_creates_afk_manifest_and_artifact(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    result = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="sandbox-session",
            backlog_ref="github:issues?label=sandcastle",
            target_branch="main",
            task_ids=["NN-101", "NN-102"],
            agent_profile="claude-code",
            sandbox_provider="docker",
            workflow_template="parallel-planner-review-merge",
            max_parallel_agents=2,
            prompts={"planner": "select unblocked work", "implementer": "implement and test"},
            required_checks=["pytest tests/test_sandbox_agent_factory.py -q"],
        )
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["surface_id"] == "sandbox-agent-factory"
    assert result["lifecycle_state"] == "planned"
    assert result["manifest"]["worktree_strategy"] == "one-worktree-per-task"
    assert result["manifest"]["sandbox_provider"] == "docker"
    assert result["manifest"]["merge_policy"] == "reviewed-tests-pass-policy-clean"
    assert [block["role"] for block in result["blocks"]] == ["planner", "implementer", "reviewer", "merger"]
    assert result["policy_scan"]["summary"]["allow_merge"] is True
    assert Path(result["artifact_path"]).exists()
```

- [x] **Step 2: Run red test**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: import failure for `SandboxAgentFactory`.

## Task 2: Runtime Implementation

**Files:**
- Create: `nexusnet/agents/sandbox_factory.py`
- Modify: `nexusnet/agents/__init__.py`

- [x] **Step 1: Implement request models and runtime**

`SandboxAgentFactoryRunRequest` must include `session_id`, `backlog_ref`, `target_branch`, `task_ids`, `agent_profile`, `sandbox_provider`, `workflow_template`, `max_parallel_agents`, `prompts`, `required_checks`, `requested_permissions`, and `metadata`.

`SandboxAgentFactory.start()` must return a manifest with `sandbox_provider`, `worktree_strategy`, `branch_prefix`, `merge_policy`, `blocks`, `events`, `checkpoint`, `policy_scan`, and `artifact_path`.

- [x] **Step 2: Verify runtime tests pass**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: runtime tests pass until API/UI tests are added.

## Task 3: Policy Block Tests

**Files:**
- Modify: `tests/test_sandbox_agent_factory.py`

- [x] **Step 1: Add failing blocked-permission test**

Add a test that requests `host_home_write`, `network_unrestricted`, and `merge_without_review` permissions and expects `lifecycle_state == "blocked"` with immune findings.

- [x] **Step 2: Run red test**

Run: `python -m pytest tests/test_sandbox_agent_factory.py::test_sandbox_agent_factory_blocks_unsafe_permissions -q`

Expected: fail until permission classification exists.

- [x] **Step 3: Implement permission classifier**

Unsafe permissions must produce hard findings and a blocked lifecycle before any merge-ready state is exposed.

- [x] **Step 4: Verify green**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: all current sandbox factory tests pass.

## Task 4: Service and API Wiring

**Files:**
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Modify: `tests/test_sandbox_agent_factory.py`

- [x] **Step 1: Add failing API tests**

Test:
- `GET /ops/brain/canon/sandbox-agent-factory`
- `POST /ops/brain/sandbox-agent-factory/runs`
- `GET /ops/brain/sandbox-agent-factory`

- [x] **Step 2: Run red API test**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: route not found.

- [x] **Step 3: Wire service and routes**

Add `brain_sandbox_agent_factory` to `NexusServices`, instantiate it in `build_services`, and expose the three routes.

- [x] **Step 4: Verify green**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: API tests pass.

## Task 5: Canon and Assimilation Target Updates

**Files:**
- Modify: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- Modify: `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
- Modify: `nexusnet/operations/assimilation_targets.py`
- Modify: `tests/test_claude_code_assimilation_targets.py`
- Modify: `tests/test_sandbox_agent_factory.py`

- [x] **Step 1: Add failing target assertions**

Update expected target IDs to include `sandbox-agent-factory`; assert the Sandcastle source ref and controls are present.

- [x] **Step 2: Run red target tests**

Run: `python -m pytest tests/test_claude_code_assimilation_targets.py tests/test_sandbox_agent_factory.py -q`

Expected: target count/source assertions fail.

- [x] **Step 3: Add source refs, target, addendum, and ledger row**

Add public source refs for:
- `https://github.com/mattpocock/sandcastle`
- `https://www.sourcepulse.org/projects/27307520`
- `https://gist.github.com/opticom/c0e5e6954874b1991e3c9b0ab7cfefe1`

Add required controls:
- `worktree_per_agent`
- `sandbox_provider_abstraction`
- `backlog_label_filter`
- `planner_implementer_reviewer_merger_flow`
- `merge_back_policy_gate`
- `logs_and_artifacts_per_run`
- `permissioned_afk_execution`

- [x] **Step 4: Verify green**

Run: `python -m pytest tests/test_claude_code_assimilation_targets.py tests/test_sandbox_agent_factory.py -q`

Expected: all tests pass.

## Task 6: Control Panel Surface

**Files:**
- Modify: `ui/control-panel/index.html`
- Modify: `ui/control-panel/app.js`
- Modify: `tests/test_sandbox_agent_factory.py`

- [x] **Step 1: Add failing UI assertions**

Assert `Sandbox Agent Factory`, `sandboxAgentFactoryScorecard`, `renderSandboxAgentFactoryScorecard`, and `/ops/brain/canon/sandbox-agent-factory` appear in the served UI or JS.

- [x] **Step 2: Run red UI test**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: UI assertion failure.

- [x] **Step 3: Add panel and guarded scorecard fetch**

Follow the existing Hive Neural Substrate panel pattern. Fetch failures must not break the entire Control Panel refresh path.

- [x] **Step 4: Verify green**

Run: `python -m pytest tests/test_sandbox_agent_factory.py -q`

Expected: all sandbox factory tests pass.

## Task 7: Final Verification

**Files:**
- All touched files.

- [x] **Step 1: Run focused tests**

Run:

```powershell
python -m pytest tests/test_sandbox_agent_factory.py tests/test_claude_code_assimilation_targets.py tests/test_agentic_pipeline_runtime.py tests/test_hive_neural_substrate.py tests/test_policy_kernel.py -q
```

Expected: all pass.

- [x] **Step 2: Run compile check**

Run:

```powershell
python -m compileall nexusnet/agents nexus/services.py nexus/api/app.py nexusnet/operations/assimilation_targets.py
```

Expected: exit code 0.

- [x] **Step 3: Run diff whitespace check**

Run:

```powershell
git diff --check -- nexusnet/agents/sandbox_factory.py nexusnet/agents/__init__.py nexus/services.py nexus/api/app.py nexusnet/operations/assimilation_targets.py tests/test_sandbox_agent_factory.py tests/test_claude_code_assimilation_targets.py ui/control-panel/index.html ui/control-panel/app.js docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md docs/superpowers/plans/2026-05-01-sandbox-agent-factory-v0-implementation.md
```

Expected: exit code 0, ignoring Git line-ending warnings if present.

- [x] **Step 4: Run GitNexus change detection**

Run GitNexus `detect_changes(scope="all", repo="NexusNet")`.

Expected: no new high/critical affected processes from this lane. Existing dirty workspace may appear and must be separated in closeout.
