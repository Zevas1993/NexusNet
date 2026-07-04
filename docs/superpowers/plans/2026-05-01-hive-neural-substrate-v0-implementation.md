# Hive Neural Substrate v0 Implementation Plan

Date: 2026-05-01
Status: active
Approved spec: `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

## Goal

Build the first executable Hive Neural Substrate v0 subsystem inside NexusNet. This is not a full model-training stack yet. It is the live neural-harness substrate that makes the approved architecture inspectable, testable, and extensible:

- explicit neural planes
- seeded hive node roster
- sparse expert routing
- recurrent deliberation loop
- policy/immune blocking
- checkpoint metadata
- candidate assimilation with sandbox/eval gates
- curator review
- API and Control Panel scorecard surface

## Constraints

- Preserve the current dirty workspace and do not revert unrelated files.
- New substrate code must be deterministic and local-first.
- Candidate promotion must never happen without source, sandbox, eval, policy, and rollback/sidebar evidence.
- Write-like actions must be blocked unless a checkpoint reference is present.
- Runtime artifacts must be written under the project artifact tree, not hidden in global state.
- The source-canon rule remains active: additions not in the original canon must be represented by post-book canon addendum and assimilation ledger entries.

## Files To Add

- `nexusnet/hive/__init__.py`
- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

## Files To Modify

- `nexus/services.py`
  - Import and instantiate `HiveNeuralSubstrate`.
  - Add `brain_hive_substrate` to `NexusServices`.
- `nexus/api/app.py`
  - Import hive request models.
  - Add live hive substrate routes.
- `ui/control-panel/index.html`
  - Add a Hive Neural Substrate v0 scorecard panel.
- `ui/control-panel/app.js`
  - Fetch `/ops/brain/canon/hive-substrate`.
  - Render plane count, node count, latest run, policy controls, and operator actions.

## TDD Sequence

1. Add failing tests for the runtime contracts and API.
2. Run `python -m pytest tests/test_hive_neural_substrate.py -q` and confirm failure before implementation.
3. Implement new hive substrate module.
4. Run the hive tests again and fix runtime contract issues.
5. Run GitNexus impact before editing shared service/API symbols.
6. Wire `nexus/services.py` and `nexus/api/app.py`.
7. Add the Control Panel scorecard surface.
8. Run the targeted verification set.

## Required Runtime Behavior

### Summary

`HiveNeuralSubstrate.summary()` must return:

- `surface_id`
- `runtime_state`
- `plane_count`
- `node_count`
- `planes`
- `nodes`
- `required_controls`
- `operator_actions`
- latest run/candidate metadata if present

### Forward Pass

`HiveNeuralSubstrate.run_forward_pass(request)` must:

- create an activation record
- select experts using sparse capability overlap
- emit a route decision
- execute a bounded recurrent loop
- create checkpoint metadata before any write action can proceed
- block unsafe write actions with no checkpoint reference
- run the policy kernel over tool/update-like action metadata
- persist a trace artifact
- return lifecycle state `completed` or `blocked`

### Assimilation Candidate

`HiveNeuralSubstrate.assimilate_candidate(request)` must:

- create an expert genome candidate
- require source references
- require sandbox and eval references before promotion
- side-bar candidates that are interesting but not safe to promote
- block candidates with no provenance
- persist the candidate decision artifact
- expose rollback/sidebar rules in the response

### Curator

`HiveNeuralSubstrate.curate()` must:

- inspect the seeded/current node roster
- report duplicate or stale capability clusters
- recommend archive/merge/keep actions
- avoid mutating protected substrate nodes

## API Routes

- `GET /ops/brain/hive-substrate`
- `POST /ops/brain/hive-substrate/forward-pass`
- `POST /ops/brain/hive-substrate/assimilate`
- `GET /ops/brain/hive-substrate/curator`
- `GET /ops/brain/canon/hive-substrate`

## Verification Commands

```powershell
python -m pytest tests/test_hive_neural_substrate.py -q
python -m pytest tests/test_hive_neural_substrate.py tests/test_agentic_pipeline_runtime.py tests/test_claude_code_assimilation_targets.py tests/test_policy_kernel.py -q
python -m compileall nexusnet/hive nexus/services.py nexus/api/app.py
git diff --check -- nexusnet/hive tests/test_hive_neural_substrate.py nexus/services.py nexus/api/app.py ui/control-panel/index.html ui/control-panel/app.js
```

## Done When

- Tests prove the substrate runtime, API, blocked write path, candidate sidebar path, curator path, and Control Panel references.
- Targeted regression tests pass.
- Compile and whitespace checks pass.
- GitNexus post-change detection has been run or a reason is documented if it cannot complete.
