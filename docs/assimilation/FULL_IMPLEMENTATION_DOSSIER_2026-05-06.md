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
| Control Panel developmental scorecard | `nexusnet/visuals/layout.py`, `ui/control-panel/app.js` | `tests/test_nexusnet_visualizer.py` | read-only operator surface |

## Claims Still Blocked

- Consciousness, sentience, or upload claims
- Production self-mutation
- Active promotion without operator approval
- Learned world-model behavior without model-backed evals
- External benchmark certification without runnable adapters
- OS-level sandbox enforcement without platform-specific proof

## Verification

Final focused suite over the new developmental, authority, evidence, eval-federation,
tool-harness, runtime-ledger, and visualizer surfaces:

```text
pytest tests/test_developmental_body_schema.py tests/test_reference_frame_store.py \
  tests/test_developmental_simulation_and_causal_lab.py \
  tests/test_growth_archive_and_promotion_tribunal.py \
  tests/test_developmental_cortex_kernel.py tests/test_authority_integrity_spine.py \
  tests/test_evidence_store.py tests/test_eval_federation.py \
  tests/test_tool_action_harness.py tests/test_runtime_decision_ledger.py \
  tests/test_nexusnet_visualizer.py -q
=> 29 passed

Package import smoke: IMPORT_SMOKE_OK
app.js syntax: node --check ui/control-panel/app.js => OK
```
