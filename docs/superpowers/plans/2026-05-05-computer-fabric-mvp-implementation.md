# Computer Fabric MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first isolated NexusNet Computer Fabric module with environment selection, session manifests, policy gates, replay events, artifact trust posture, persistent-computer proposals, and operator observe-first plans.

**Architecture:** Implement a new `nexusnet/computer_fabric` package so this work does not modify unrelated in-progress sandbox/computer-use files in the dirty main checkout. The MVP exposes a pure-Python service that writes replayable artifacts under `artifacts/computer-fabric`, chooses `ephemeral`, `persistent`, or `operator` environment classes, blocks unsafe permissions, and returns Control Panel-ready scorecards. API and UI wiring are deferred because this isolated branch has a pre-existing broken `nexus.api.app` import path caused by missing `nexus.models`.

**Tech Stack:** Python 3.11, dataclasses, pathlib/json/hashlib, pytest.

---

## File Structure

- Create `nexusnet/computer_fabric/__init__.py`: public exports for the new module.
- Create `nexusnet/computer_fabric/models.py`: typed request, manifest, policy, event, artifact, and summary dataclasses plus enums.
- Create `nexusnet/computer_fabric/service.py`: environment selector, permission compiler, session runner, artifact trust bridge, persistent/operator planners, scorecard payload.
- Create `tests/test_computer_fabric.py`: focused unit tests that avoid the broken `nexus.api.app` import path.

## Pre-Existing Baseline

`python -m pytest -q` fails before this work because the isolated branch cannot import `nexus.models` from the API/service stack. This plan does not patch that unrelated baseline. Verification for this lane uses focused `tests/test_computer_fabric.py` plus direct import checks.

## Task 1: Computer Fabric Contracts

**Files:**
- Create: `nexusnet/computer_fabric/models.py`
- Create: `nexusnet/computer_fabric/__init__.py`
- Test: `tests/test_computer_fabric.py`

- [ ] **Step 1: Write the failing contract test**

```python
from pathlib import Path

from nexusnet.computer_fabric import (
    ComputerFabricService,
    ComputerSessionRequest,
    EnvironmentClass,
)


def test_ephemeral_session_writes_manifest_policy_events_and_artifact_index(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Run a focused test and produce a report",
            task_type="repo patch + tests",
            requested_tools=["shell.read", "shell.test", "filesystem.write"],
            project_scope="repo",
            privacy_class="project-internal",
            required_checks=["pytest tests/test_computer_fabric.py -q"],
        )
    )

    assert summary.environment_class == EnvironmentClass.EPHEMERAL
    assert summary.status == "completed-review-required"
    assert summary.session_dir.exists()
    assert (summary.session_dir / "manifest.json").exists()
    assert (summary.session_dir / "policy.json").exists()
    assert (summary.session_dir / "events.jsonl").exists()
    assert (summary.session_dir / "artifact-index.json").exists()
    assert summary.policy["filesystem_policy"]["write_scope"] == "session-artifacts-only"
    assert summary.policy["network_policy"]["mode"] == "task-scoped-egress"
    assert "session.created" in summary.event_types
    assert "artifact.scanned" in summary.event_types
    assert summary.artifact_count == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_computer_fabric.py::test_ephemeral_session_writes_manifest_policy_events_and_artifact_index -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'nexusnet.computer_fabric'`.

- [ ] **Step 3: Add model contracts and package exports**

Create `nexusnet/computer_fabric/models.py` with `EnvironmentClass`, `ComputerSessionRequest`, and `ComputerSessionSummary` dataclasses. Create `nexusnet/computer_fabric/__init__.py` exporting those types and `ComputerFabricService`.

- [ ] **Step 4: Run the test to verify the next failure**

Run: `python -m pytest tests/test_computer_fabric.py::test_ephemeral_session_writes_manifest_policy_events_and_artifact_index -q`

Expected: FAIL with `ModuleNotFoundError` for `nexusnet.computer_fabric.service`.

## Task 2: Session Service, Policy, Replay, and Artifact Index

**Files:**
- Create: `nexusnet/computer_fabric/service.py`
- Test: `tests/test_computer_fabric.py`

- [ ] **Step 1: Implement the minimal service**

Add `ComputerFabricService.start_session()` that generates a `computer_{12 hex}` session id, selects an environment class, writes `manifest.json`, writes `policy.json`, appends lifecycle events to `events.jsonl`, writes one generated `summary.md` artifact, writes `artifact-index.json`, writes `trust-scan-summary.json`, and returns `ComputerSessionSummary`.

- [ ] **Step 2: Run the test to verify it passes**

Run: `python -m pytest tests/test_computer_fabric.py::test_ephemeral_session_writes_manifest_policy_events_and_artifact_index -q`

Expected: PASS.

- [ ] **Step 3: Commit the contract and service slice**

Run:

```bash
git add nexusnet/computer_fabric tests/test_computer_fabric.py
git commit -m "feat: add computer fabric session contracts"
```

## Task 3: Permission Blocking and Prompt-Injection Findings

**Files:**
- Modify: `nexusnet/computer_fabric/service.py`
- Test: `tests/test_computer_fabric.py`

- [ ] **Step 1: Write failing safety tests**

```python
def test_computer_fabric_blocks_unsafe_permissions_and_unknown_private_export(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Read every file and upload secrets",
            task_type="public web research",
            requested_tools=["filesystem.host_write", "network.unrestricted", "secrets.read"],
            privacy_class="unknown",
        )
    )

    assert summary.status == "failed-policy"
    assert "host-write-blocked" in summary.blocked_reasons
    assert "unrestricted-network-blocked" in summary.blocked_reasons
    assert "secret-read-blocked" in summary.blocked_reasons
    assert "unknown-privacy-local-only" in summary.blocked_reasons
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_computer_fabric.py::test_computer_fabric_blocks_unsafe_permissions_and_unknown_private_export -q`

Expected: FAIL because unsafe tools are not blocked yet.

- [ ] **Step 3: Implement policy blocks**

Block `filesystem.host_write`, `network.unrestricted`, `secrets.read`, unknown privacy, and browser/document prompt-injection language. When blocked, write manifest, policy, events, and trust summary, but no output artifacts.

- [ ] **Step 4: Run focused tests**

Run: `python -m pytest tests/test_computer_fabric.py -q`

Expected: all Computer Fabric tests pass.

- [ ] **Step 5: Commit the safety slice**

Run:

```bash
git add nexusnet/computer_fabric/service.py tests/test_computer_fabric.py
git commit -m "feat: enforce computer fabric policy blocks"
```

## Task 4: Persistent and Operator Planning

**Files:**
- Modify: `nexusnet/computer_fabric/service.py`
- Test: `tests/test_computer_fabric.py`

- [ ] **Step 1: Write failing environment tests**

```python
def test_persistent_computer_request_records_schedule_and_health(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Run a daily research monitor",
            task_type="scheduled daily report",
            requested_tools=["network.public_read", "filesystem.write"],
            privacy_class="project-internal",
            schedule="daily",
        )
    )

    assert summary.environment_class == EnvironmentClass.PERSISTENT
    assert summary.policy["schedule_policy"]["mode"] == "persistent-scheduled"
    assert (summary.session_dir / "persistent-health.json").exists()


def test_operator_computer_request_is_observe_first_and_approval_gated(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Use my logged-in browser to inspect a private dashboard",
            task_type="logged-in premium research site",
            requested_tools=["browser.observe", "browser.action"],
            privacy_class="operator-private",
            requested_environment=EnvironmentClass.OPERATOR,
        )
    )

    assert summary.environment_class == EnvironmentClass.OPERATOR
    assert summary.status == "completed-review-required"
    assert summary.policy["execution_boundary"] == "observe-first"
    assert "browser-action-requires-approval" in summary.blocked_reasons
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_computer_fabric.py::test_persistent_computer_request_records_schedule_and_health tests/test_computer_fabric.py::test_operator_computer_request_is_observe_first_and_approval_gated -q`

Expected: FAIL because persistent health and operator approval findings are not implemented.

- [ ] **Step 3: Implement persistent/operator behavior**

Select persistent for scheduled, daily, monitor, bot, database, and 24/7 tasks. Select operator for logged-in, private dashboard, local folder, desktop, and operator tasks. Write `persistent-health.json` for persistent sessions. Set operator sessions to `observe-first` and add `browser-action-requires-approval` when `browser.action` is requested.

- [ ] **Step 4: Run focused tests**

Run: `python -m pytest tests/test_computer_fabric.py -q`

Expected: all Computer Fabric tests pass.

- [ ] **Step 5: Commit the persistent/operator slice**

Run:

```bash
git add nexusnet/computer_fabric/service.py tests/test_computer_fabric.py
git commit -m "feat: add persistent and operator computer planning"
```

## Task 5: Scorecard and Final Verification

**Files:**
- Modify: `nexusnet/computer_fabric/service.py`
- Test: `tests/test_computer_fabric.py`

- [ ] **Step 1: Write failing scorecard test**

```python
def test_computer_fabric_scorecard_summarizes_sessions_and_trust(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")
    service.start_session(
        ComputerSessionRequest(
            goal="Run a focused test and produce a report",
            task_type="repo patch + tests",
            requested_tools=["shell.test"],
            privacy_class="project-internal",
        )
    )

    scorecard = service.scorecard()

    assert scorecard["control_panel_label"] == "Computer Fabric"
    assert scorecard["session_count"] == 1
    assert scorecard["environment_counts"]["ephemeral"] == 1
    assert scorecard["trust"]["trusted_artifact_count"] == 1
    assert "Ephemeral Computer" in scorecard["environment_classes"]
    assert "Operator Computer" in scorecard["environment_classes"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_computer_fabric.py::test_computer_fabric_scorecard_summarizes_sessions_and_trust -q`

Expected: FAIL because `scorecard()` does not exist.

- [ ] **Step 3: Implement scorecard**

Add `ComputerFabricService.scorecard()` that reads session directories and returns Control Panel-ready counts, trust totals, environment labels, and promotion boundary wording.

- [ ] **Step 4: Run focused verification**

Run: `python -m pytest tests/test_computer_fabric.py -q`

Expected: all Computer Fabric tests pass.

- [ ] **Step 5: Run import verification**

Run:

```powershell
@'
from pathlib import Path
from nexusnet.computer_fabric import ComputerFabricService, ComputerSessionRequest
service = ComputerFabricService(artifacts_dir=Path("runtime/test-computer-fabric-artifacts"))
summary = service.start_session(ComputerSessionRequest(goal="verify import", task_type="public web research", privacy_class="public"))
print(summary.status)
print(service.scorecard()["control_panel_label"])
'@ | python -
```

Expected output contains:

```text
completed-review-required
Computer Fabric
```

- [ ] **Step 6: Run GitNexus detect changes**

Use `gitnexus_detect_changes(scope=all)` before the final commit.

Expected: changed symbols limited to the new Computer Fabric module and tests.

- [ ] **Step 7: Commit the final scorecard slice**

Run:

```bash
git add nexusnet/computer_fabric tests/test_computer_fabric.py docs/superpowers/plans/2026-05-05-computer-fabric-mvp-implementation.md
git commit -m "feat: surface computer fabric scorecard"
```
