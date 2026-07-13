# Final Whole-Branch Fix Report

## Status

COMPLETE_WITH_CONCERNS

Base head: `68829451`.

Scope remains Programs A/B. This wave does not claim Programs C-I, candidate synthesis, frontier inference, Native MoE birth, federation, or Hugging Face publication.

## GitNexus impact evidence

Before production edits, upstream impact was requested for `EvolutionEventStore.append`, `EvolutionEventStore.replay`, registry `register_unit`, `list_units`, `_remember`, `register_genome`, `list_genomes`, pressure `record`, `ranked`, and initialization. The linked-worktree index returned `UNKNOWN`, 0 impacted for each new backend symbol. This is the known linked-worktree indexing limitation.

`renderAutonomousUpdatesScorecard` resolved by exact UID `Function:ui/control-panel/app.js:renderAutonomousUpdatesScorecard`: LOW risk, 3 direct callers, 10 total impacted symbols, 1 process (`renderAll`), and 1 module (`Control-panel`). No new HIGH or CRITICAL pre-edit symbol impact appeared.

The all-scope pre-stage change detector reported 34 files, 987 changed symbols, 96 affected processes, CRITICAL. This is the branch-versus-index baseline and includes the already committed branch, not the seven-file final fix slice. Staged detection is recorded below.

## Defect 1: event-store privacy schema

Root cause: the generic recursive sanitizer allowed arbitrary dictionary keys and all bool/int/float/list containers unless a recognized suffix happened to trigger reference validation.

RED command:

`python -m pytest tests/test_universal_evolution_store.py -q -k 'fails_closed_for_unknown_or_unsafe or rejects_numeric_containers or replay_rejects_hash_consistent_unknown'`

RED result: exit 1; 9 failed, 1 passed, 30 deselected in 0.32s. Failures reproduced path/control/unknown keys, numeric byte sequences and nested numeric containers, non-finite scalars, and hash-consistent external payload replacement.

GREEN implementation: exact event-type payload schema unions for the five current contracts and `legacy-taxonomy.observed`; exact numeric, boolean, metadata, optional-reference, and reference-list fields; finite numeric enforcement; unknown event payloads and fields fail closed. Append and replay call the same validator.

GREEN focused result: 10 passed, 30 deselected in 0.24s. Complete store result at that cycle: 40 passed in 0.33s.

## Defect 2: defensive immutability

Root cause: frozen Pydantic models still contained mutable lists; registry and pressure maps retained and returned the same model instances.

RED command:

`python -m pytest tests/test_universal_evolution_service.py -q -k 'defensively_isolates'`

RED result: exit 1; 3 failed, 23 deselected in 0.40s. Unit, genome, and pressure list mutations all reached internal state.

GREEN implementation: validated deep copies at registry/pressure storage and return boundaries. Public contract types and serialization shapes are unchanged.

GREEN focused result: 3 passed, 23 deselected in 0.31s. Complete service result: 26 passed in 0.63s.

## Defect 3: concurrent append serialization

Root cause: `append()` selected its head through public `replay()` before opening append mode, so independent stores could both select the same sequence and previous hash.

RED command:

`python -m pytest tests/test_universal_evolution_store.py::test_concurrent_store_instances_serialize_head_selection_and_append -q`

RED result: exit 1; 1 failed in 0.27s with `EvolutionIntegrityError: event 2 has non-contiguous sequence`.

GREEN implementation: one per-path same-process `threading.RLock` plus an OS file lock held across replay/head selection/write/flush/fsync. Windows uses `msvcrt.locking`; POSIX uses `fcntl.flock`; no dependency was added. Public `replay()` takes the same critical section. `append()` calls `_replay_unlocked()` while holding it, avoiding self-deadlock.

GREEN repeat evidence:

- Deterministic synchronized two-store regression: 10 consecutive runs, each 1 passed (0.23-0.24s).
- Combined thread plus spawned-process regression: 5 consecutive runs, each 2 passed and 40 deselected (1.62-1.65s).
- Complete store result after concurrency additions: 41 passed in 0.47s; final documented matrix includes the spawned-process case as well.

## Defect 4: UI semantic boundary validation

Root cause: the availability predicate accepted any string for service and mutation boundaries and did not validate the nested coverage boundary.

RED command:

`python -m pytest tests/test_release_wrapper_runtime.py::test_control_panel_evolution_projection_distinguishes_unavailable_telemetry -q`

RED result: exit 1; 1 failed in 9.96s because `wrong-service-boundary` rendered as available.

GREEN implementation requires these exact values:

- service claim boundary: `registry-and-evidence-state-only; no candidate, experiment, promotion, native-model-birth, or frontier-superiority claim`
- mutation boundary: `read-only-no-protected-state-mutation`
- nested coverage claim boundary: `legacy-lane-coverage-is-not-universal-organism-coverage`

Wrong/missing boundary cases render the explicit unavailable/unverified card. Hostile markers remain on variable pressure ID, prerequisite, uncovered ref, and hash fields.

GREEN result: 1 passed in 8.56s. Fresh final run: 1 passed in 8.68s.

## Files changed

- `nexusnet/evolution/store.py`
- `nexusnet/evolution/registry.py`
- `nexusnet/evolution/pressure.py`
- `ui/control-panel/app.js`
- `tests/test_universal_evolution_store.py`
- `tests/test_universal_evolution_service.py`
- `tests/test_release_wrapper_runtime.py`
- `.superpowers/sdd/final-fix-report.md`

## Required verification

Documented historical 101-test matrix command:

`python -m pytest tests/test_universal_evolution_contracts.py tests/test_universal_evolution_store.py tests/test_universal_evolution_service.py tests/test_universal_evolution_api.py tests/test_self_improvement_coverage_endpoint.py tests/test_hive_self_improvement_engine.py tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q`

Fresh result: exit 0; 116 passed, 0 skipped, 0 failed in 97.01s. The command historically collected 101 tests; the 15 final-wave regressions increase the current count to 116. An earlier timed run of the same command exited 0 in 96.301 wall seconds but suppressed pytest's count, so the direct fresh result above is the count authority.

Restart/hash/privacy smoke: exit 0. Three service constructions over one artifact root produced identical Everything State hashes; 23 events; sequences 1-23; only schema `nexusnet-evolution-event-v1`; payload hashes, event hashes, and previous links independently recomputed; privacy hit count 0 across root path, prompt body, output body, bearer token, private-key marker, and session marker; both explicit unsafe append probes rejected. Runtime truth: 22 registered units, 22 legacy aspects, legacy taxonomy fully covered, universal coverage false.

Other gates:

- Node-backed Control Panel behavior: 1 passed in 8.68s.
- Concurrency thread/process repeat: 5/5 runs green, 2 passed each.
- `python -m compileall -q nexusnet/evolution`: exit 0, no output.
- `git diff --check`: exit 0, no whitespace errors.
- Staged `git diff --cached --check`: exit 0, no whitespace errors; exactly the seven code/test files plus this report.
- Staged GitNexus detection: exit 0; 0 changed symbols, 0 affected processes, risk none, `No changes detected` (linked-worktree mapping limitation).

## Self-review

- Contract/API shapes remain unchanged; validation moved to the generic persistence boundary.
- All five current contract `model_dump(mode="json")` payloads and the legacy taxonomy event remain covered by the matrix.
- Append and replay share one payload validator; replay rejects hash-consistent unsafe external events.
- Numeric arrays are rejected even when values look like bytes; only exact pressure/legacy numeric fields are accepted and values must be finite.
- Registry and pressure internals do not share mutable lists with caller-owned or returned records.
- Lock ownership covers the complete chain operation and public replay; append does not recursively acquire the OS lock.
- UI fixed tokens are semantic gates, while genuinely variable fields retain escaping/XSS coverage.
- No unrelated dirty worktree content was edited or staged.

## Concerns

- The linked-worktree GitNexus index cannot map the new backend symbols, so backend pre-edit impacts are UNKNOWN/zero rather than meaningful graph coverage. Direct tests and staged file scope are the primary evidence for those symbols.
- The POSIX `fcntl` branch is implemented from the standard-library platform contract but was not executed on this Windows host. Windows thread and spawned-process locking were executed repeatedly.
- The persistent `.lock` sidecar is deliberate coordination state next to `events.jsonl`; event durability and fail-closed integrity checks remain unchanged.
- Programs C-I remain outside this fix wave.
