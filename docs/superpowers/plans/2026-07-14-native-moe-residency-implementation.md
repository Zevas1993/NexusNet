# Native MoE Residency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working NexusNet-native sparse-MoE inference path that safely packages experts, plans GPU/RAM/storage residency, executes selected experts from tiered safetensors, learns hot-expert locality, prefetches without changing routes, and adaptively disables unhelpful speculative decoding.

**Architecture:** Add a focused `nexusnet.runtime.moe_residency` package and one optional execution-backend seam in `MoECapsuleLayer`. The existing resident `ModuleList` path remains the default reference; tiered execution is attached explicitly for inference and always preserves router IDs, top-k choices, gate weights, and target verification.

**Tech Stack:** Python 3.11+, PyTorch, safetensors, Pydantic-compatible dataclasses, pytest, GitNexus CLI.

## Global Constraints

- Do not add Colibrì as a provider, subprocess, CLI, server, or production dependency.
- Preserve the resident MoE execution path as default and rollback.
- Tiered execution is inference-only; autograd/training stays resident.
- Every existing symbol edit requires GitNexus upstream impact analysis first.
- Every behavior begins with a focused failing test.
- Storage artifacts are safetensors plus digest-verified JSON manifests; never use pickle.
- Prefetch changes residency only, never expert selection or gate weights.
- Speculative output remains target-verified and disables itself on non-positive measured benefit.
- Preserve unrelated dirty-worktree changes and run `gitnexus detect-changes --repo NexusNet` before commits.

---

### Task 1: Residency contracts, admission planning, and heat policy

**Files:**
- Create: `nexusnet/runtime/moe_residency/__init__.py`
- Create: `nexusnet/runtime/moe_residency/schemas.py`
- Create: `nexusnet/runtime/moe_residency/planner.py`
- Create: `nexusnet/runtime/moe_residency/heat.py`
- Test: `tests/runtime/test_moe_residency.py`

**Interfaces:**
- Produces: `HardwareMemorySnapshot`, `MoEResidencyRequest`, `MoEResidencyPlan`, `MoEResidencyPlanner.plan(request)`, and `ExpertHeatPolicy.touch()/repin()`.
- Consumes: no production runtime symbols.

- [ ] **Step 1: Write failing admission and heat-policy tests**

```python
def test_planner_rejects_when_dense_working_set_does_not_fit():
    plan = MoEResidencyPlanner().plan(_request(gpu_available_bytes=64, dense_core_bytes=80))
    assert plan.admission_state == "blocked"
    assert "dense_core_exceeds_gpu_working_set" in plan.blockers

def test_heat_policy_requires_hysteresis_before_replacing_hot_expert():
    policy = ExpertHeatPolicy(slot_count=1, hysteresis=0.25)
    policy.touch("layer0:expert0", count=8)
    assert policy.repin() == ("layer0:expert0",)
    policy.touch("layer0:expert1", count=9)
    assert policy.repin() == ("layer0:expert0",)
    policy.touch("layer0:expert1", count=8)
    assert policy.repin() == ("layer0:expert1",)
```

- [ ] **Step 2: Run the tests and confirm missing-module failures**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py`

Expected: collection fails because `nexusnet.runtime.moe_residency` does not exist.

- [ ] **Step 3: Implement immutable contracts and conservative planner**

```python
@dataclass(frozen=True)
class MoEResidencyPlan:
    plan_id: str
    admission_state: Literal["admitted", "blocked"]
    blockers: tuple[str, ...]
    gpu_expert_slots: int
    ram_expert_slots: int
    cold_store_required: bool
    expected_bottleneck: str
```

The planner subtracts dense core, KV, runtime buffers, and configured headroom before assigning expert slots. It blocks missing/negative telemetry and insufficient dense working sets.

- [ ] **Step 4: Implement deterministic LFRU-style heat and hysteresis**

```python
def score(self, expert_ref: str) -> int:
    state = self._states[expert_ref]
    return (state.heat << 8) + state.last_used_sequence
```

Replacement requires `candidate_score > incumbent_score * (1 + hysteresis)`. Decay halves heat and never changes pinned order without a subsequent `repin()`.

- [ ] **Step 5: Run focused tests**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py`

Expected: all Task 1 tests pass.

### Task 2: Digest-verified expert manifests and tiered safetensor store

**Files:**
- Create: `nexusnet/runtime/moe_residency/manifest.py`
- Create: `nexusnet/runtime/moe_residency/store.py`
- Modify: `tests/runtime/test_moe_residency.py`

**Interfaces:**
- Consumes: Task 1 contracts and heat policy.
- Produces: `ExpertTensorManifest`, `package_swiglu_experts(...)`, `TieredExpertStore.acquire(expert_id, device)`, `TieredExpertStore.prefetch(...)`, `TieredExpertStore.evidence()`.

- [ ] **Step 1: Write failing packaging, digest, and eviction tests**

```python
def test_packaged_expert_round_trips_without_pickle(tmp_path):
    experts = nn.ModuleList([SwiGLUExpert(4, 8), SwiGLUExpert(4, 8)])
    manifest = package_swiglu_experts(experts, tmp_path, model_ref="fixture", layer_id="0")
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)
    loaded = store.acquire(0, torch.device("cpu"))
    assert loaded["w_gate.weight"].equal(experts[0].w_gate.weight)
    assert manifest.experts[0].path.endswith(".safetensors")

def test_digest_mismatch_fails_closed(tmp_path):
    manifest = _package_fixture(tmp_path)
    Path(manifest.experts[0].path).write_bytes(b"corrupt")
    with pytest.raises(ExpertIntegrityError):
        TieredExpertStore(manifest, ram_slots=1, hot_slots=0).acquire(0, torch.device("cpu"))
```

- [ ] **Step 2: Verify the tests fail for missing APIs**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py -k "packaged or digest or eviction"`

Expected: imports or names fail because Task 2 APIs are absent.

- [ ] **Step 3: Implement safetensor packaging and JSON manifest persistence**

```python
save_file({name: value.detach().cpu().contiguous() for name, value in expert.state_dict().items()}, path)
digest = hashlib.sha256(path.read_bytes()).hexdigest()
```

Manifest loading validates schema, expected expert count, unique `(layer_id, expert_id)` records, safe relative paths, file sizes, and SHA-256 digests.

- [ ] **Step 4: Implement bounded RAM/hot LRU caches and evidence**

`acquire()` returns tensors on the requested device, coalesces repeated cache access, records storage/RAM/hot hits separately, and evicts only unleased entries. The portable implementation uses synchronous safetensor reads; prefetch uses a bounded thread pool.

- [ ] **Step 5: Run focused tests**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py`

Expected: all Task 1-2 tests pass.

### Task 3: Optional tiered execution seam in the real MoE layer

**Files:**
- Create: `nexusnet/runtime/moe_residency/execution.py`
- Modify: `nexusnet/hive/net/model.py`
- Modify: `tests/runtime/test_moe_residency.py`
- Test: `tests/test_hive_trainable_net.py`

**Interfaces:**
- Consumes: `TieredExpertStore.acquire()` and `MoECapsuleLayer` selected expert token batches.
- Produces: `ExpertExecutionBackend.execute(expert_id, inputs)`, `TieredSwiGLUExecutionBackend`, `MoECapsuleLayer.set_execution_backend()`.

- [ ] **Step 1: Write a failing resident-versus-tiered equivalence test**

```python
def test_tiered_backend_matches_resident_moe_output(tmp_path):
    torch.manual_seed(7)
    layer = MoECapsuleLayer(4, 8, num_experts=3, top_k=2).eval()
    x = torch.randn(6, 4)
    expected = layer(x)
    backend = TieredSwiGLUExecutionBackend.from_layer(layer, tmp_path, ram_slots=1, hot_slots=1)
    layer.set_execution_backend(backend)
    actual = layer(x)
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
```

- [ ] **Step 2: Verify the equivalence test fails because the seam is absent**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py::test_tiered_backend_matches_resident_moe_output`

Expected: fails because `set_execution_backend` or the backend is missing.

- [ ] **Step 3: Add the optional backend seam without changing default routing**

```python
def set_execution_backend(self, backend: ExpertExecutionBackend | None) -> None:
    if self.training and backend is not None:
        raise RuntimeError("tiered expert execution is inference-only")
    self.execution_backend = backend

expert_out = (
    self.execution_backend.execute(e, x[token_mask])
    if self.execution_backend is not None
    else self.experts[e](x[token_mask])
)
```

The loop, selected IDs, original-score softmax, load accounting, governance bias, and aggregation remain unchanged.

- [ ] **Step 4: Implement functional SwiGLU execution from acquired tensors**

```python
gate = F.linear(x, tensors["w_gate.weight"], tensors.get("w_gate.bias"))
value = F.linear(x, tensors["w_value.weight"], tensors.get("w_value.bias"))
return F.linear(F.silu(gate) * value, tensors["w_out.weight"], tensors.get("w_out.bias"))
```

- [ ] **Step 5: Verify equivalence and existing training behavior**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py tests/test_hive_trainable_net.py`

Expected: all tests pass, including backprop through the untouched resident path.

### Task 4: Heat-driven repinning and cancelable prefetch

**Files:**
- Create: `nexusnet/runtime/moe_residency/prefetch.py`
- Modify: `nexusnet/runtime/moe_residency/execution.py`
- Modify: `nexusnet/runtime/moe_residency/store.py`
- Modify: `tests/runtime/test_moe_residency.py`

**Interfaces:**
- Consumes: execution demand observations and store prefetch.
- Produces: `RouteTransitionPrefetcher.observe(layer_id, experts)`, `.candidates(next_layer_id)`, and backend request-boundary `repin()`.

- [ ] **Step 1: Write failing tests for route-transition prediction and route invariance**

```python
def test_prefetch_learns_layer_transition_without_changing_output(tmp_path):
    prefetcher = RouteTransitionPrefetcher(max_candidates=2)
    for _ in range(4):
        prefetcher.observe("0", (1, 2), "1", (3,))
    assert prefetcher.candidates("0", (1, 2), "1") == (3,)
```

- [ ] **Step 2: Verify the tests fail for missing predictor**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py -k prefetch`

Expected: missing import or API failure.

- [ ] **Step 3: Implement bounded transition counts and store prefetch**

The predictor keys counts by `(source_layer, selected_tuple, target_layer)`. `prefetch()` schedules digest-verified loads through a bounded executor and returns a cancelable future. Store evidence records requests, useful hits, and wasted loads.

- [ ] **Step 4: Run focused and equivalence tests**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py`

Expected: all tests pass and tiered output remains identical.

### Task 5: Adaptive target-verified speculation controller

**Files:**
- Create: `nexusnet/runtime/moe_residency/speculation.py`
- Modify: `tests/runtime/test_moe_residency.py`
- Test: `tests/test_hive_runtime_reasoning.py`

**Interfaces:**
- Consumes: an injected target-verified decode callable compatible with `speculative_decode`.
- Produces: `AdaptiveSpeculationController.run(...)` and per-profile enabled/disabled state.

- [ ] **Step 1: Write failing tests for measured enablement and shutoff**

```python
def test_adaptive_speculation_disables_slower_profile():
    controller = AdaptiveSpeculationController(min_trials=2, min_speedup=1.02)
    controller.observe("disk-cold", baseline_seconds=1.0, candidate_seconds=1.2, accepted=8, proposed=8)
    controller.observe("disk-cold", baseline_seconds=1.0, candidate_seconds=1.1, accepted=8, proposed=8)
    assert controller.enabled("disk-cold") is False
    assert controller.state("disk-cold").reason == "non_positive_end_to_end_benefit"
```

- [ ] **Step 2: Verify missing-controller failure**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py -k speculation`

Expected: missing import or API failure.

- [ ] **Step 3: Implement rolling wall-clock policy**

The controller records bounded aggregate seconds and token counts. It disables after `min_trials` when mean baseline/candidate speedup is below `min_speedup`, regardless of acceptance rate. Disabled profiles return the target-only callable.

- [ ] **Step 4: Run focused and existing speculative correctness tests**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py tests/test_hive_runtime_reasoning.py`

Expected: all tests pass.

### Task 6: Runtime evidence, provenance, and full verification

**Files:**
- Create: `nexusnet/runtime/moe_residency/evidence.py`
- Create: `nexusnet/runtime/moe_residency/provenance.py`
- Create: `docs/third-party/COLIBRI_ASSIMILATION_NOTICE.md`
- Modify: `nexusnet/runtime/moe_residency/__init__.py`
- Modify: `tests/runtime/test_moe_residency.py`

**Interfaces:**
- Consumes: planner, store, heat, prefetch, and speculation evidence.
- Produces: `ExpertResidencyEvidence.snapshot()` and `ColibriAssimilationProvenance`.

- [ ] **Step 1: Write failing redaction and provenance tests**

```python
def test_evidence_contains_metrics_but_no_prompt_content():
    evidence = ExpertResidencyEvidence(plan_ref="plan:1", manifest_ref="manifest:1")
    evidence.record_fallback("load_timeout")
    payload = evidence.snapshot()
    assert payload["fallback_events"] == ["load_timeout"]
    assert "prompt" not in json.dumps(payload).lower()
```

- [ ] **Step 2: Verify missing evidence APIs**

Run: `python -m pytest -q tests/runtime/test_moe_residency.py -k "evidence or provenance"`

Expected: missing import or API failure.

- [ ] **Step 3: Implement sanitized evidence and pinned upstream provenance**

The provenance record identifies `JustVugg/colibri`, commit `748787c3afa8ab336bb51bf616f212a04f209bba`, Apache-2.0, and the eligible `tier.h`/`resource_plan.py` influences. Runtime evidence accepts numeric metrics, refs, and controlled reason codes only.

- [ ] **Step 4: Run verification matrix**

Run:

```powershell
python -m pytest -q tests/runtime/test_moe_residency.py tests/test_hive_trainable_net.py tests/test_hive_runtime_reasoning.py tests/test_runtime_workload_scorecards.py
git diff --check
npx gitnexus detect-changes --repo NexusNet
```

Expected: all tests pass; no whitespace errors; GitNexus reports only the intended runtime, MoE layer, tests, plan, and notice scope.

- [ ] **Step 5: Commit the implementation**

```powershell
git add docs/superpowers/plans/2026-07-14-native-moe-residency-implementation.md docs/third-party/COLIBRI_ASSIMILATION_NOTICE.md nexusnet/runtime/moe_residency nexusnet/hive/net/model.py tests/runtime/test_moe_residency.py
git commit -m "feat: add native tiered MoE inference"
```
