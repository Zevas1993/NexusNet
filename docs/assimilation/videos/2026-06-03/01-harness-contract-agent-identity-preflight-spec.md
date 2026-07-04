# Harness Contract And Agent Identity Preflight Assimilation Spec

Status: candidate assimilation target
Date added: 2026-06-03
Canon entry: `PB-2026-06-03-094`
Primary canon addendum: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
Primary ledger: `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`

## Source Evidence

Local video-watcher evidence:

- YES Harness report: `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-improvement-2026-06-03\yes-harness-self-optimization-preview\YTDown_YouTube_YES-Harness-Self-optimization-w-9B-LLM-L_Media_aaViBfjnh78_001_1080p_20260603_045102\WATCH_REPORT.md`
- auth.md report: `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-improvement-2026-06-03\auth-md-autonomous-agents-preview\YTDown_YouTube_Unlock-Autonomous-AI-Agents-with-auth-md_Media_Dqp_b8GHLXU_001_1080p_20260603_045407\WATCH_REPORT.md`
- Current YES Harness full watcher report: `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-2026-06-03\YTDown_YouTube_YES-Harness-Self-optimization-w-9B-LLM-L_Media_aaViBfjnh78_001_1080p_20260603_054026\WATCH_REPORT.md`
- Current auth.md full watcher report: `C:\Users\ChrisBoyd\Documents\Codex\video-watch\nexusnet-2026-06-03\YTDown_YouTube_Unlock-Autonomous-AI-Agents-with-auth-md_Media_Dqp_b8GHLXU_001_1080p_20260603_054750\WATCH_REPORT.md`

Primary source refs:

- `https://arxiv.org/abs/2605.30621`
- `https://github.com/workos/auth.md`

Existing NexusNet anchors:

- `docs/SELF_IMPROVEMENT_LAYER.md`
- `nexusnet/agents/harnesses/ledger.py`
- `nexusnet/agents/harnesses/routing.py`
- `nexusnet/agents/harnesses/registry.py`
- `nexusnet/agents/pipelines/service.py`
- `nexusnet/tools/action_harness.py`
- `nexusnet/tools/permissions/service.py`
- `nexusnet/security/artifact_trust.py`
- `tests/test_harness_improvement_ledger.py`
- `tests/test_agentic_pipeline_runtime.py`
- `tests/test_tool_action_harness.py`

The local video-watcher reports are Codex observation evidence, not NexusNet runtime state. Any future NexusNet-owned evidence must be copied or regenerated under the project-root artifact boundary with source refs, checksums, and redaction gates.

## Assimilation Verdict

Assimilate as a NexusNet candidate named **Harness Contract And Agent Identity Preflight**.

The target is not a new autonomous pipeline runner and not an automatic model self-update system. It is a preflight, evidence ledger, and runtime scorecard that verifies whether an agent run actually loaded the required harness, followed that harness, and held only the identity, scopes, and credentials needed for the requested work.

## Accepted Pattern

The YES Harness lesson is that harness availability is not enough. A model can fail before useful work in two different ways:

- Activation failure: the required skill, prompt, memory packet, tool policy, or eval context was not loaded.
- Adherence failure: the harness was loaded, but the agent trajectory ignored or contradicted it.

The additional implementation lesson is that harness updating and harness benefit should be scored separately. A small or local model can propose useful harness updates, but weaker solver models may still fail to load or follow the harness. NexusNet should therefore track skill-load rate, harness-following rate, and loaded-pass rate as separate evidence fields instead of treating an evolved prompt, memory file, or skill file as intrinsically useful.

The auth.md lesson is that autonomous agents need discoverable, scoped, auditable identity and credential delegation before normal API, MCP, or tool use. Human OAuth copied into agent workflows is not enough for long-running governed agents.

NexusNet should combine those lessons into one runtime contract:

- Required harness artifacts are declared before the run.
- Loaded harness artifacts are recorded at run start.
- Adherence checks are recorded during and after the trajectory.
- Agent identity, auth source, scopes, token expiry, owner/claim status, and service endpoints are recorded without storing raw secrets.
- The run is allowed, blocked, or sent to operator review based on the contract evidence.

## Rejected Pattern

Do not assimilate the videos as:

- A permission to bypass existing `ToolActionHarness`, policy, sandbox, eval, or governance gates.
- A direct-fine-tuning trigger based on harness failure evidence.
- A raw-token or raw-secret ledger.
- A replacement for the existing `HarnessImprovementLedger`, provider registry, self-improvement layer, or agentic pipeline runtime.
- A product-specific dependency on WorkOS or any one identity provider.

## Proposed Runtime Contract

Candidate module:

- `nexusnet/agents/harnesses/contract.py`

Candidate primary types:

- `HarnessContract`
- `HarnessArtifactRequirement`
- `HarnessActivationEvidence`
- `HarnessAdherenceEvidence`
- `AgentIdentityEvidence`
- `HarnessContractDecision`
- `HarnessContractLedger`

Minimum contract fields:

```yaml
harness_contract:
  contract_id: string
  task_family: string
  agent_id: string
  model_route: string
  required_artifacts:
    - artifact_id: string
      artifact_type: skill | prompt | memory_pack | tool_policy | eval_pack | auth_scope
      source_ref: string
      required: true
  activation_evidence:
    loaded_artifact_ids: []
    missing_required_artifact_ids: []
    context_digest: string
    skill_load_rate: number
  adherence_evidence:
    followed_artifact_ids: []
    contradicted_artifact_ids: []
    harness_adherence_failure: boolean
    loaded_pass_rate: number
    reviewer_ref: string
  identity_evidence:
    identity_provider: local | auth_md | oauth | service_account | operator_delegated
    discovery_ref: string
    proof_type: string
    scopes: []
    token_expiry_ref: string
    account_owner_ref: string
    raw_secret_stored: false
  decision:
    status: allow | block | review_required
    reasons: []
    required_next_gate: string
    rollback_ref: string
```

## Implementation Path

1. Add the contract model and in-memory ledger under `nexusnet/agents/harnesses/`.
2. Add a preflight builder that consumes the existing harness provider registry, routing policy, task type, data sensitivity, sandbox permission mode, and requested tools.
3. Wire the preflight into `AgenticPipelineRuntime` as an evidence packet on each block or run, without changing execution behavior at first.
4. Wire `ToolActionHarness.plan_action()` to accept an optional harness contract decision and require `review_required` or `block` for missing required artifacts, unsafe scopes, raw-secret exposure, or unclaimed identity.
5. Feed contract failures into the existing self-improvement layer only as review-gated improvement events or eval candidates. Do not allow direct prompt, skill, route, credential, or model mutation.
6. Add a read-only canon/control surface showing contract count, missing artifact rate, adherence failure rate, identity scope failures, and recent review-required decisions.
7. Add a small-model harness updater lane only after the preflight ledger exists. It may propose prompt, skill, memory, or tool-policy diffs, but those diffs stay shadow-only until the solver model proves activation, adherence, and task pass-rate gains.
8. Add tests before implementation for allowed, missing-artifact, loaded-but-not-followed, unsafe-scope, raw-secret, review-required, and shadow-only small-model update paths.

## Required Tests

Focused test targets:

- `tests/test_harness_contract_preflight.py`
- `tests/test_agentic_pipeline_runtime.py`
- `tests/test_tool_action_harness.py`
- `tests/test_harness_improvement_ledger.py`
- Control Panel/API scorecard tests if a surface is added.

Minimum test cases:

- A run with all required artifacts loaded and adhered to returns `allow`.
- A run missing a required skill or memory pack returns `review_required` or `block`.
- A run that loads a harness but fails adherence records `harness_adherence_failure`.
- A run requesting private data with external auth but no scoped identity is blocked.
- A run that attempts to store a raw token or secret is blocked.
- A contract failure can create a self-improvement candidate, but cannot mutate protected state.
- A small-model harness update candidate is side-barred if the solver fails to load or follow it, even when the update text itself is syntactically valid.

## Security And Policy Gates

- No raw OAuth tokens, API keys, private screenshots, raw prompts, raw outputs, private file contents, or unredacted local paths may be stored in the contract ledger.
- Credentials must be represented by digest, vault ref, expiry ref, or policy ref only.
- External identity providers are optional adapters, not core dependencies.
- Any auth.md-style discovery must be signed, source-pinned, scope-limited, and replayable.
- Promotion beyond read-only ledger/preflight requires sandbox proof, security review, eval deltas, rollback plan, and operator/governance approval.

## First Milestone

Implement a non-mutating `HarnessContractLedger` and preflight decision surface that can be called by the agentic pipeline and tool action harness. The first milestone is successful if it produces reviewable evidence and blocks unsafe or incomplete runs without changing model weights, registered skills, provider routes, credentials, or production runtime state.
