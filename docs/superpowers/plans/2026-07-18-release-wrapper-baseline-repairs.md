# Release Wrapper Baseline Repairs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the seven root causes behind the eleven reproduced provider-growth and release-wrapper baseline failures while preserving sanitized, fail-closed governance.

**Architecture:** Keep the existing release-wrapper orchestration and persistence model. Make narrow state-transition corrections at the live chat boundaries, gate autonomous work on verified readiness and supervisor pulses, and reuse the existing sanitized runtime projections in the visualizer.

**Tech Stack:** Python 3, FastAPI/TestClient, pytest, JavaScript template literals, GitNexus.

## Global Constraints

- Work only in `F:\NexusNet\NexusNet\.worktrees\windows-accelerator-pack-foundation` on `codex/windows-accelerator-completion-train`.
- Preserve the dirty integration checkout and do not port broad hunks from it.
- Run GitNexus upstream impact analysis before modifying any function or method.
- Warn on HIGH or CRITICAL impact before editing, and run GitNexus change detection before every commit.
- Preserve `raw_content_included: false`, `active_production_mutation_allowed: false`, and sanitized identifiers on every new receipt.
- Use the existing eleven failing tests as the TDD red baseline; do not relax their assertions.
- Execute tasks sequentially in this session; do not delegate.

---

### Task 1: Correct sanitized visualizer metric labels

**Files:**
- Modify: `ui/visualizer/app.js:1360-1415`
- Verify: `tests/test_wrapper_providers_and_growth.py`
- Verify: `tests/test_release_wrapper_runtime.py`

**Interfaces:**
- Consumes: existing `releaseProviderReadiness`, `releaseCanonicalAoCoverage`, `releaseFederatedPacketOutbox`, and `releaseFederatedPacketInbox` sanitized view models.
- Produces: four stable user-facing labels required by the wrapper source guards.

- [ ] **Step 1: Confirm the four source-guard failures are red**

Run the provider-readiness, canonical-AO, outbox, and inbox tests. Expected: each fails only because one required `Wrapper ...` literal is absent.

- [ ] **Step 2: Rename only the four stale captions**

```javascript
<small>Wrapper usable providers</small>
<small>Wrapper canonical AOs</small>
<small>Wrapper packet outbox</small>
<small>Wrapper packet inbox</small>
```

- [ ] **Step 3: Run the four tests again**

Expected: all four pass and no raw-content assertions change.

- [ ] **Step 4: Review and commit**

Run GitNexus change detection, inspect `git diff -- ui/visualizer/app.js`, and commit as `fix(ui): align release wrapper visualizer metrics`.

### Task 2: Keep domain-expert growth pending until explicit admin replay

**Files:**
- Modify: `nexusnet/release_wrapper.py:862-876`
- Verify: `tests/test_wrapper_providers_and_growth.py:409`

**Interfaces:**
- Consumes: `interaction["domain_teacher_eval_handoff"]`.
- Produces: a sanitized `domain_expert_growth_admin_replay` proposal with status `pending-admin-approval`; the existing `/ops/wrapper/domain-expert-growth/admin-replay` endpoint remains the executor.

- [ ] **Step 1: Run the existing domain-routing regression**

Expected: CodingAO and ResearchAO candidates incorrectly show `approved` after ordinary chat.

- [ ] **Step 2: Replace automatic approval with a pending proposal**

```python
handoff["admin_replay_status"] = "pending-admin-approval"
domain_replay = {
    "surface_id": "release-wrapper-domain-expert-growth-admin-replay",
    "status": "pending-admin-approval",
    "session_ref_digest": interaction.get("session_ref_digest"),
    "domain_ao": handoff.get("domain_ao"),
    "teacher_subject": handoff.get("teacher_subject"),
    "handoff_id": handoff.get("handoff_id"),
    "approval_required": True,
    "approval_endpoint": "/ops/approvals",
    "execution_endpoint": "/ops/wrapper/domain-expert-growth/admin-replay",
    "raw_content_included": False,
    "active_production_mutation_allowed": False,
    "mutation_boundary": "live-domain-handoff-proposal-only-until-explicit-admin-replay",
}
```

- [ ] **Step 3: Re-run the domain-routing regression**

Expected: non-selected candidates remain shadow/review, while the explicit FederationAO admin replay is approved and recorded.

- [ ] **Step 4: Review and commit**

Run GitNexus change detection, inspect the focused diff, and commit as `fix(runtime): require admin replay for domain growth`.

### Task 3: Gate automatic federated import readiness on usable providers

**Files:**
- Modify: `nexusnet/release_wrapper.py:1063-1135`
- Modify: `nexusnet/release_wrapper.py:903-927`
- Modify: `nexusnet/release_wrapper.py:6270-6290`
- Verify: `tests/test_wrapper_providers_and_growth.py:252`
- Verify: `tests/test_release_wrapper_runtime.py:3476`

**Interfaces:**
- Consumes: `_provider_readiness_status(provider_id) -> str`.
- Produces: `skipped-provider-not-usable` for unknown/unverified providers and normal quarantined-shadow import evidence for usable providers.

- [ ] **Step 1: Run the OpenAI-compatible readiness regression**

Expected: `mock/default` creates a later federated-import readiness run that replaces the interaction lifecycle as the latest run.

- [ ] **Step 2: Add the provider qualification guard**

```python
provider_readiness_status = self._provider_readiness_status(provider_id)
if provider_readiness_status != "usable":
    return {
        "surface_id": "release-wrapper-live-federated-import-readiness",
        "status": "skipped-provider-not-usable",
        "provider_readiness_status": provider_readiness_status,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
```

Update both callers to attach import evidence only when the returned status does not start with `skipped-`.

- [ ] **Step 3: Re-run the OpenAI-compatible and usable-provider inbox tests**

Expected: `mock/default` preserves its interaction lifecycle as latest; `nexusnet-offline` still auto-imports sanitized packets and the inbox test passes.

- [ ] **Step 4: Review and commit**

Run GitNexus change detection, inspect the focused diff, and commit as `fix(runtime): qualify live federated readiness imports`.

### Task 4: Make degraded provider recovery observation read-only

**Files:**
- Modify: `nexusnet/release_wrapper.py:1699-1722`
- Verify: `tests/test_wrapper_providers_and_growth.py:820`
- Verify: `tests/test_wrapper_providers_and_growth.py:1109`

**Interfaces:**
- Consumes: `HiveForwardPassRequest.requested_actions`.
- Produces: a governed inspection receipt that does not request mutation or require a write checkpoint.

- [ ] **Step 1: Run both degraded-provider regressions**

Expected: the provider failure is recorded, but project heartbeat status is `degraded` because the recovery action is classified as a write without a checkpoint.

- [ ] **Step 2: Convert the recovery probe to an inspection**

```python
{
    "action_id": "release-wrapper-degraded-recovery-probe",
    "action_type": "inspect",
    "target_ref": f"model::{_safe_ref(source_model)}",
    "metadata": {
        "governed_recovery_probe": True,
        "read_only": True,
        "active_production_mutation_allowed": False,
        "requires_admin_approval": False,
        "requires_sandbox_eval": False,
        "requires_rollback": False,
    },
}
```

- [ ] **Step 3: Re-run both degraded-provider regressions**

Expected: provider failure remains sanitized and visible, while project and native hive heartbeats are alive/covered.

- [ ] **Step 4: Review and commit**

Run GitNexus change detection, inspect the focused diff, and commit as `fix(runtime): observe degraded recovery without mutation`.

### Task 5: Gate automatic repair execution on a real supervisor pulse

**Files:**
- Modify: `nexusnet/release_wrapper.py:885-902`
- Modify: `nexusnet/release_wrapper.py:2020-2036`
- Modify: `nexusnet/release_wrapper.py:5597-5745`
- Verify: `tests/test_release_wrapper_runtime.py:3239`
- Verify: `tests/test_release_wrapper_runtime.py:3109`

**Interfaces:**
- Changes: `_record_automatic_release_health_repair_envelope_plan(..., auto_execute: bool) -> dict[str, Any]`.
- Produces: a persisted `planned-admin-approval-required-heartbeat-supervisor-repair` readiness record when no pulse exists; preserves completed automatic execution after an enabled supervisor pulse.

- [ ] **Step 1: Run the pending-repair regression**

Expected: the plan is already completed before the explicit administrator endpoint is called.

- [ ] **Step 2: Pass pulse state explicitly from both chat paths**

```python
auto_execute = supervisor_tick.get("pulse_emitted") is True
automatic_repair_plan = self._record_automatic_release_health_repair_envelope_plan(
    session_id=session_id,
    loop=automatic_repair_loop,
    trigger="wrapper-interaction-auto",
    auto_execute=auto_execute,
)
```

- [ ] **Step 3: Persist a pending plan when `auto_execute` is false**

Record the planned subsystem envelopes through `record_release_readiness_evidence_run` with status `planned-admin-approval-required-heartbeat-supervisor-repair`, empty action results, and the existing sanitized command reference. Return the resulting run ID, update ID, source loop/heartbeat IDs, envelope references, and explicit repair endpoint without calling `_record_autonomous_update_governance_lifecycle`.

- [ ] **Step 4: Preserve the existing lifecycle execution when `auto_execute` is true**

Keep the current sandbox/eval/apply/rollback path and completed envelope construction unchanged behind the true branch.

- [ ] **Step 5: Run both pending and enabled-supervisor regressions**

Expected: the default plan stays pending until the admin endpoint executes it; an enabled immediate supervisor pulse still completes the automatic lifecycle.

- [ ] **Step 6: Review and commit**

Run GitNexus change detection, inspect the focused diff, and commit as `fix(runtime): gate automatic repair on supervisor pulse`.

### Task 6: Fail closed when the production spine is unavailable

**Files:**
- Modify: `nexusnet/release_wrapper.py:1138-1215`
- Verify: `tests/test_release_wrapper_runtime.py:3374`

**Interfaces:**
- Consumes: optional `self.production_spine`.
- Produces: sanitized `degraded-production-spine-unavailable` lifecycle status without attempting a release lifecycle run.

- [ ] **Step 1: Run the degraded production-spine regression**

Expected: chat raises an `AttributeError` after forward-pass coverage already marks the production-spine stage degraded.

- [ ] **Step 2: Add a live-supervisor boundary guard**

```python
if self.production_spine is None:
    return {
        "surface_id": "release-wrapper-live-release-supervisor-product-lifecycle",
        "status": "degraded-production-spine-unavailable",
        "production_spine_release_lifecycle_run_id": None,
        "production_spine_release_lifecycle_rollback_id": None,
        "boot_supervisor_manifest_id": None,
        "initial_release_supervisor_manifest_id": None,
        "blocker": "production_spine_unavailable",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
```

- [ ] **Step 3: Re-run the degraded production-spine regression**

Expected: chat returns 200, coverage has exactly one degraded production-spine stage, and no raw content is retained.

- [ ] **Step 4: Review and commit**

Run GitNexus change detection, inspect the focused diff, and commit as `fix(runtime): degrade safely without production spine`.

### Task 7: Persist heartbeat evidence before boot supervision and verify the train

**Files:**
- Modify: `nexusnet/release_wrapper.py:930-1050`
- Verify: `tests/test_release_wrapper_runtime.py:3109`
- Verify: `tests/test_wrapper_providers_and_growth.py`
- Verify: `tests/test_release_wrapper_runtime.py`

**Interfaces:**
- Consumes: the completed forward-pass, provider, growth, federation, repair, and native-heartbeat evidence already attached to `interaction`.
- Produces: persisted whole-system heartbeat evidence visible to boot readiness before the boot supervisor runs.

- [ ] **Step 1: Run the live release-supervisor regression**

Expected: only the release-readiness boot check fails because the current heartbeat tick is not yet persisted.

- [ ] **Step 2: Move live release lifecycle calls after heartbeat persistence**

Keep latest growth receipt refresh before `_build_whole_system_heartbeat_tick(interaction)`. Build, attach, insert, and persist the heartbeat and any post-repair tick first. Then call `_record_live_release_supervisor_product_lifecycle`, followed by `_record_live_release_run_history_and_refresh_canon_contract`.

- [ ] **Step 3: Re-run the live release-supervisor regression**

Expected: boot status is `boot-smoke-passed`, initial release is `initial-release-go`, and release history/canon receipts remain covered.

- [ ] **Step 4: Run all eleven focused regressions together**

Run:

```powershell
python -m pytest -q `
  tests/test_wrapper_providers_and_growth.py::test_wrapper_provider_readiness_is_honest_sanitized_and_release_visible `
  tests/test_wrapper_providers_and_growth.py::test_openai_compatible_chat_completions_feeds_release_runtime `
  tests/test_wrapper_providers_and_growth.py::test_provider_domain_ao_routing_surfaces_real_prompt_receipts_without_raw_content `
  tests/test_wrapper_providers_and_growth.py::test_provider_ao_execution_receipts_persist_replay_and_feed_release_readiness `
  tests/test_wrapper_providers_and_growth.py::test_openai_compatible_provider_failure_records_degraded_forward_pass_receipt `
  tests/test_wrapper_providers_and_growth.py::test_degraded_provider_forward_pass_records_cache_evidence_and_replays_after_restart `
  tests/test_release_wrapper_runtime.py::test_successful_chat_auto_runs_release_supervisor_and_production_spine_lifecycle_from_live_use `
  tests/test_release_wrapper_runtime.py::test_wrapper_chat_pending_repair_envelope_executes_through_admin_governed_repair_run `
  tests/test_release_wrapper_runtime.py::test_release_wrapper_forward_pass_coverage_records_degraded_subsystem_without_raw_content `
  tests/test_release_wrapper_runtime.py::test_release_wrapper_federated_packet_outbox_exports_sanitized_replayable_packets `
  tests/test_release_wrapper_runtime.py::test_release_wrapper_imports_federated_packets_as_quarantined_shadow_learning
```

Expected: `11 passed`.

- [ ] **Step 5: Run broad affected suites**

Run `python -m pytest tests/test_wrapper_providers_and_growth.py -q` and `python -m pytest tests/test_release_wrapper_runtime.py -q`. Expected: both files pass with zero failures.

- [ ] **Step 6: Run focused Windows accelerator regression and compile checks**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs tests/runtime/test_windows_hardware_discovery.py tests/test_runtime_mode_api.py -q
python -m compileall -q nexusnet
```

Expected: zero failures and exit code 0.

- [ ] **Step 7: Perform final scope review**

Run GitNexus change detection, `git diff --check`, `git status --short`, and inspect `git diff HEAD~7..HEAD -- nexusnet/release_wrapper.py ui/visualizer/app.js tests`. Confirm only approved runtime/UI behavior changed and no test assertion was weakened.

- [ ] **Step 8: Commit final ordering repair**

Commit as `fix(runtime): persist heartbeat before release boot checks`.
