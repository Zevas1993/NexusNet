# NexusNet Computer Fabric MVP Design

Status: approved architecture design, pending implementation plan
Date: 2026-05-05
Scope: NexusNet governed computer/sandbox/runtime fabric inspired by Perplexity Computer, Manus Sandbox, Manus Cloud Computer, Manus Browser Operator, and the Software 3.0 neural-compute video review.

## 1. Purpose

NexusNet Computer Fabric is the governed execution layer that lets NexusNet act through real compute surfaces without losing its core doctrine: policy first, evidence first, replayable state, artifact trust, operator visibility, and no silent production mutation.

The user-facing goal is simple:

```text
Ask NexusNet for an outcome.
NexusNet chooses the right computer.
The computer researches, browses, edits, runs, tests, builds, schedules, or hosts.
Every action is visible, replayable, policy-gated, and trust-scanned.
Only reviewed outputs can influence live NexusNet state.
```

The product goal is to outperform Perplexity Computer and Manus Computer by combining:

- Perplexity-style search, agent orchestration, connectors, background work, persistent memory, and secure sandbox framing.
- Manus-style temporary sandboxes, persistent always-on computers, local browser operator, desktop/local-folder bridge, scheduled tasks, projects, and executable skills.
- NexusNet-native governance: Artifact Trust, policy manifests, replay ledgers, control-panel scorecards, promotion gates, rollback evidence, and local-first privacy boundaries.

This design is for the MVP architecture and implementation plan. It is not a request to implement code yet.

## 2. External Research Baseline

### 2.1 Software 3.0 / Neural Compute Video

The watched video framed a staircase from today's practical systems toward a future neural computer:

```text
Tier 1: generative content inside conventional UI
Tier 2: generative regions inside conventional app state
Tier 3: narrow-domain generative loops
Tier 4: neural substrate with deterministic tool fallback
```

The practical conclusion for NexusNet is to build deterministic computer execution first. Generated-pixel UI and neural substrate loops belong behind the fabric as later R&D, not in the first implementation slice.

The useful transferable ideas are:

- explicit state beats opaque hidden state for v0,
- browser/file/code tools should sit below the model as deterministic affordances,
- each action should update a persistent state ledger,
- a neural or VLM computer-use layer must remain observe-first until permission and sandbox evidence exist,
- deterministic tools should handle anything that must be correct.

### 2.2 Perplexity Computer

Research sources:

- `https://www.perplexity.ai/help-center/en/articles/13837784-what-is-computer`
- `https://www.perplexity.ai/es-es/hub/blog/introducing-perplexity-computer`
- `https://research.perplexity.ai/articles/browsesafe`

Perplexity's strongest patterns:

- a general digital worker rather than a passive answer engine,
- background/asynchronous execution,
- search-native intelligence with citations,
- multi-tool orchestration,
- sub-agents for specialist work,
- authenticated app connectors,
- persistent memory,
- scheduling and recurring automation,
- secure cloud/isolated sandbox framing,
- defense-in-depth for browser-agent prompt injection.

NexusNet should assimilate the product pattern, not the vendor boundary. The equivalent NexusNet feature must route through NexusBrain policy, the Neural Bus, Artifact Trust, and operator-approved promotion.

### 2.3 Manus Computer

Research sources:

- `https://manus.im/blog/manus-sandbox`
- `https://manus.im/blog/manus-cloud-computer`
- `https://manus.im/docs/features/browser-operator`
- `https://manus.im/docs/features/cloud-browser`
- `https://manus.im/docs/features/desktop`
- `https://manus.im/docs/features/projects`
- `https://manus.im/docs/features/scheduled-tasks`
- `https://manus.im/features/agent-skills`

Manus adds a clearer environment model:

- `Temporary Sandbox`: per-task isolated VM with filesystem, network, browser, shell, and software tools.
- `Cloud Computer`: persistent always-on Ubuntu machine for bots, scheduled scrapers, databases, hosted tools, and persistent knowledge bases.
- `Browser Operator`: local authenticated browser control with explicit authorization, visible actions, logs, and stop/takeover.
- `Desktop / My Computer`: local folder and command-line access with folder scoping and command approval.
- `Projects`: persistent instructions plus knowledge files inherited by tasks.
- `Skills`: reusable executable workflows with progressive disclosure and script execution.
- `Scheduled Tasks`: recurring automation with execution history.

The Manus lesson is that a single "sandbox" abstraction is too small. NexusNet needs multiple computer classes with a shared governance plane.

## 3. Product Thesis

NexusNet should not become a generic remote IDE, a browser automation toy, or a cloud-only coding agent. It should become a governed Computer Fabric:

```text
NexusBrain
  -> Computer Fabric
      -> Ephemeral Computer
      -> Persistent Computer
      -> Operator Computer
  -> Replay Ledger
  -> Artifact Trust
  -> Control Panel
  -> Promotion / rollback gates
```

The winning differentiation is not "can run code." Many products can run code. The winning differentiation is:

- chooses the right environment class,
- grants the minimum viable tool set,
- keeps private data local by default,
- records every meaningful action,
- scans every output,
- proves tests and rollback before promotion,
- exposes the entire state in the Control Panel,
- learns from repeated workflows by packaging governed skills and projects.

## 4. Existing NexusNet Anchors

The MVP should extend existing NexusNet surfaces instead of building a disconnected subsystem.

Primary code anchors:

- `nexusnet/agents/sandbox_factory.py`: current sandbox/worktree agent factory and AFK run manifest.
- `nexusnet/agents/pipelines/service.py`: structured pipeline runtime, blocks, gates, and event ledger.
- `nexusnet/agents/scheduled/service.py`: scheduled agent workflows and execution history.
- `nexusnet/agents/scheduled/artifacts.py`: scheduled artifact store.
- `nexusnet/vision/computer_use.py`: multimodal computer-use planning and permission/sandbox boundaries.
- `nexusnet/browser/context_memory.py`: operator-provided browser context ingestion and local-only privacy boundary.
- `nexusnet/tools/permissions/service.py`: tool permission review and command/write approval posture.
- `nexusnet/security/artifact_trust.py`: trust scan for generated, imported, or runtime artifacts.
- `nexusnet/growth/production_spine.py`: production readiness, replay bundle, signing, and no-production-mutation gates.
- `ui/control-panel/app.js`: scorecard and operator cockpit surfaces.

Existing docs and canon anchors:

- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-01-015`
- `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
- `docs/superpowers/plans/2026-05-01-sandbox-agent-factory-v0-implementation.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`
- `docs/autonomous/PRODUCTION_SPINE_RUN_LOG.md`

## 5. Non-Negotiable Doctrine

### 5.1 No Silent Host Control

NexusNet must never control host files, host browser sessions, local credentials, local apps, or desktop state without explicit operator scope and approval.

Allowed local access is always:

- folder-scoped,
- session-scoped,
- logged,
- revocable,
- denied by default for secrets and private paths,
- local-only unless the operator separately authorizes export.

### 5.2 No Direct Production Mutation

Computer Fabric runs may create patches, artifacts, reports, tools, model variants, datasets, runtime packages, or deployment proposals. They do not mutate production NexusNet state directly.

Promotion requires:

- completed run ledger,
- required checks,
- policy scan,
- Artifact Trust clearance,
- rollback evidence,
- operator approval for high-risk or production-impacting changes.

### 5.3 Environment Class Is a Security Boundary

Every computer session must declare exactly one environment class:

```text
ephemeral
persistent
operator
```

The environment class determines lifecycle, filesystem scope, network posture, credential posture, persistence, schedule eligibility, and cleanup behavior.

### 5.4 Browser Text Is Untrusted Input

Any webpage, PDF, user-generated content, repo file, email, calendar invite, downloaded document, screenshot OCR, or browser DOM content may contain hostile instructions.

Computer Fabric must separate:

```text
operator instruction
system policy
tool result
webpage/document content
model inference
```

Only operator instructions and system policy can authorize actions.

### 5.5 Every Output Is an Artifact

Anything the fabric produces is an artifact:

- patch,
- generated file,
- report,
- dataset,
- app,
- script,
- runtime package,
- browser export,
- screenshot,
- model output bundle,
- scheduled job result,
- persistent computer backup,
- public URL,
- credential request,
- deployment proposal.

Artifacts must carry provenance and trust status before they are consumed by later NexusNet lanes.

## 6. Environment Classes

### 6.1 Ephemeral Computer

Purpose: one-off task execution in an isolated, disposable environment.

Use for:

- code edits,
- tests,
- builds,
- research reports,
- data analysis,
- web app prototypes,
- generated documents,
- safe browser automation against public sites,
- package installation experiments,
- runtime proof runs,
- candidate assimilation experiments.

Lifecycle:

```text
create -> run -> collect artifacts -> trust scan -> cleanup
```

Required properties:

- isolated worktree or sandbox filesystem,
- TTL,
- no persistent credentials by default,
- network deny-by-default unless task-scoped,
- command log,
- file diff,
- output artifact bundle,
- replayable event stream,
- cleanup proof.

Provider candidates:

- local Python venv,
- local Node/npm workspace,
- Docker,
- Podman,
- devcontainer,
- WSL-backed Linux environment,
- future Firecracker/gVisor/microVM provider,
- remote sandbox provider when policy allows.

MVP target:

Extend `SandboxAgentFactory` from a planning manifest into a real `ComputerSession` launch path for local provider classes first.

### 6.2 Persistent Computer

Purpose: always-on or durable environment for work that must continue across tasks or time.

Use for:

- 24/7 bots,
- scheduled reports,
- scheduled scrapers,
- live databases,
- ongoing research ledgers,
- self-hosted open-source tools,
- long-running benchmarks,
- watch/monitor jobs,
- reusable project workspace,
- persistent knowledge base,
- local/private long-running machine when operator wants it.

Lifecycle:

```text
provision -> configure -> run/sleep/wake -> scheduled execution -> backup/export -> retire
```

Required properties:

- named computer identity,
- owner and project scope,
- storage quota,
- resource quota,
- schedule policy,
- network egress policy,
- inbound/public URL policy,
- secrets policy,
- backup/restore policy,
- cost and uptime ledger,
- health state,
- manual stop and pause controls,
- artifact export boundary.

Provider candidates:

- local always-on workstation folder plus venv,
- WSL distro,
- Docker Compose project,
- remote Linux VM,
- cloud container app,
- future Kubernetes/Ray worker lane.

MVP target:

Do not host arbitrary public services first. Start with persistent scheduled local or repo-scoped jobs whose outputs are written to the scheduled artifact store and Artifact Trust scan path.

### 6.3 Operator Computer

Purpose: permissioned bridge to the operator's real browser, selected local folders, local CLI tools, and possibly local GPU.

Use for:

- authenticated browser workflows,
- premium site research using user sessions,
- local file organization,
- local build/test flows that require installed tools,
- local hardware use,
- local-only private document processing,
- browser context ingestion,
- tasks blocked by data-center IP or CAPTCHA in cloud/browser sandboxes.

Lifecycle:

```text
request -> operator grants scope -> observe -> propose actions -> approve/run -> log -> revoke
```

Required properties:

- explicit scope grant,
- visible actions,
- stop/takeover control,
- per-command approval unless an allow rule is configured,
- folder-scoped filesystem access,
- no credential capture,
- no raw private export by default,
- local-only data plane,
- browser/action log,
- redaction and replay summary.

Provider candidates:

- browser extension,
- local desktop helper,
- local CLI bridge,
- MCP connector bridge,
- Codex/app local tool bridge in development contexts.

MVP target:

Keep Operator Computer observe-first. It can ingest operator-provided browser context and produce action plans before any autonomous browser or CLI control is enabled.

## 7. Core Components

### 7.1 ComputerFabricService

Central service that accepts computer session requests, chooses an environment class, applies policy, starts or attaches to a provider, records events, and produces a session summary.

Responsibilities:

- classify requested work,
- select environment class,
- resolve provider,
- compile permission policy,
- create session manifest,
- start or attach environment,
- record events,
- collect artifacts,
- trigger Artifact Trust scans,
- expose scorecard payloads.

### 7.2 ComputerSessionManifest

Project-local manifest written before execution starts.

Required fields:

```text
session_id
created_at
requested_by
goal
environment_class
provider
project_scope
privacy_class
risk_level
allowed_tools
blocked_tools
network_policy
filesystem_policy
credential_policy
schedule_policy
ttl_policy
approval_policy
required_checks
artifact_contract
replay_contract
rollback_contract
control_panel_refs
```

The manifest is the source of truth for what the computer was allowed to do.

### 7.3 EnvironmentProviderRegistry

Registry of concrete providers behind the three environment classes.

Provider interface:

```text
prepare(manifest) -> provider_state
execute(action) -> event
snapshot() -> snapshot_ref
collect_artifacts() -> artifact_refs
pause() -> lifecycle_event
resume() -> lifecycle_event
stop() -> lifecycle_event
destroy() -> cleanup_event
```

Providers must not define their own policy. They receive a compiled policy and must enforce or fail closed.

### 7.4 PermissionPolicyCompiler

Converts task intent and environment class into concrete permissions.

Inputs:

- user goal,
- environment class,
- privacy class,
- data sensitivity,
- requested tools,
- repository scope,
- browser scope,
- network needs,
- credential needs,
- schedule needs,
- production-impact risk.

Outputs:

- allowed tools,
- blocked tools,
- approval requirements,
- network allowlist,
- filesystem roots,
- credential bindings,
- export rules,
- required scans,
- required tests,
- stop conditions.

This should extend existing tool permission and computer-use policy logic instead of duplicating it.

### 7.5 ComputerReplayLedger

Append-only session event ledger.

Event classes:

```text
session.created
policy.compiled
provider.prepared
operator.approval_requested
operator.approval_granted
operator.approval_denied
command.started
command.completed
command.failed
file.created
file.modified
file.deleted
browser.opened
browser.navigation
browser.action
browser.takeover_requested
artifact.created
artifact.scanned
check.started
check.completed
check.failed
session.paused
session.resumed
session.completed
session.failed
session.destroyed
```

The ledger must be compact enough for Control Panel inspection but complete enough for replay, debugging, and future training/eval use after privacy filtering.

### 7.6 ArtifactTrustBridge

Connects session outputs to `ArtifactTrustRegistry`.

Required behavior:

- every output file gets an artifact record,
- artifacts include session provenance,
- unsafe serialization is blocked,
- missing checksum/signature is flagged,
- license/provenance gaps are visible,
- untrusted artifacts cannot become production inputs,
- trust scan outputs are kept out of the scanned source bundle to avoid recursive contamination.

### 7.7 Skill and Project Bridge

Assimilates Manus Skills and Projects patterns as NexusNet-governed reusable workflows.

Skill behavior:

- skill metadata loads cheaply,
- detailed instructions load only when triggered,
- resources/scripts load on demand,
- scripts execute only inside approved environment classes,
- skills can be benchmarked from successful runs,
- team/shared skills require review and provenance.

Project behavior:

- project instruction and knowledge base can be attached to sessions,
- task-level state remains separate from project-level state,
- updates to project files affect only future sessions unless explicitly reloaded,
- project sharing does not imply sharing private task artifacts.

### 7.8 Scheduler and Persistent Job Bridge

Scheduled jobs should reuse Computer Fabric rather than bypass it.

Required behavior:

- every schedule has a manifest,
- every run has a session id,
- failures are logged,
- outputs are artifact-scanned,
- persistent computers expose uptime and resource state,
- recurring jobs preserve history and diff from prior outputs.

### 7.9 Control Panel Cockpit

The Control Panel must expose Computer Fabric as a first-class operator surface.

Required panels:

- active sessions,
- environment inventory,
- pending approvals,
- run logs,
- command/browser/file event summaries,
- artifact trust state,
- scheduled/persistent job state,
- cleanup/retention state,
- risk and policy findings,
- promotion blockers,
- replay links.

The cockpit must make it impossible to confuse:

- planned vs running,
- generated vs trusted,
- sandboxed vs host-local,
- private local vs exportable,
- temporary vs persistent,
- tested vs untested,
- approved vs blocked.

## 8. Session Selection Matrix

```text
Task type                         Default environment
------------------------------------------------------
public web research               ephemeral
repo patch + tests                ephemeral
build prototype app               ephemeral
one-off data analysis             ephemeral
scheduled daily report            persistent
24/7 Slack/Discord/customer bot   persistent
live database                     persistent
self-hosted dashboard/tool        persistent
logged-in premium research site   operator or cloud browser with approval
local private documents           operator, local-only
local GPU / installed SDK         operator
browser CAPTCHA/MFA required      operator takeover
production deployment             blocked until promotion workflow
```

The selector may override defaults only when policy evidence supports the override.

## 9. Safety and Privacy Model

### 9.1 Privacy Classes

```text
public
project-internal
operator-private
credential-adjacent
regulated-or-sensitive
unknown
```

Default for unknown is blocked or local-only observe-first.

### 9.2 Network Policy

Network modes:

```text
none
public-web-readonly
task-scoped-egress
connector-scoped
authenticated-browser
inbound-preview-only
public-service-hosting
```

`public-service-hosting` is out of MVP unless the implementation plan explicitly scopes a persistent provider with isolation and operator approval.

### 9.3 Credential Policy

Credentials are never copied into artifacts or prompts.

Allowed credential shapes:

- connector token reference,
- local environment variable reference,
- ephemeral secret mount,
- operator browser session,
- project-local encrypted key reference,
- manual one-time approval.

Credential values must not be written to replay logs.

### 9.4 Prompt Injection Defense

Computer Fabric must include a browser/document instruction isolation layer:

- webpage text is evidence, not authority,
- hidden DOM, comments, links, metadata, and downloaded files are untrusted,
- suspicious instructions become policy findings,
- high-risk browser actions require confirmation,
- extracted content is labeled by source,
- tool calls must cite the operator goal and policy grant that authorized them.

### 9.5 Collaboration Boundary

If multiple operators or collaborators can send instructions into a session:

- authority is attributed per message,
- connector access is reduced or disabled by default,
- private files are not visible unless explicitly shared,
- pending actions show who authorized them,
- session export redacts collaborator-private material.

## 10. Replay and Artifact Contracts

### 10.1 Session Directory Layout

Proposed local artifact layout:

```text
artifacts/computer-fabric/{session_id}/
  manifest.json
  policy.json
  events.jsonl
  approvals.jsonl
  command-log.jsonl
  browser-log.jsonl
  file-diff.json
  artifact-index.json
  trust-scan-summary.json
  checks.json
  cleanup.json
  summary.md
```

Persistent computers also need:

```text
artifacts/computer-fabric/persistent/{computer_id}/
  computer.json
  health.jsonl
  schedules.json
  backups.jsonl
  resource-usage.jsonl
  exposed-services.json
```

### 10.2 Artifact Index Record

```text
artifact_id
session_id
computer_id
path_or_uri
artifact_type
created_by_action
checksum
signature_ref
provenance_refs
license_status
privacy_class
export_allowed
trust_status
promotion_allowed
```

### 10.3 Completion States

```text
completed-trusted
completed-untrusted-output
completed-review-required
failed-policy
failed-provider
failed-checks
failed-timeout
blocked-approval-required
cancelled-by-operator
destroyed
```

## 11. MVP Implementation Slices

### Slice 1: Computer Session Contract

Add data contracts and a service shell for:

- session request,
- environment class,
- provider kind,
- policy profile,
- manifest write,
- event ledger write,
- summary payload.

No real autonomous host control is required in this slice.

### Slice 2: Ephemeral Local Provider

Add a controlled local provider that can run a tiny safe command set inside a repo-local temporary workspace or venv.

Allowed first commands should be boring:

- inspect environment,
- run targeted tests,
- create a generated artifact in the session directory,
- collect stdout/stderr,
- write event ledger.

### Slice 3: Artifact Trust Integration

Route generated outputs into `ArtifactTrustRegistry`.

Acceptance condition:

- untrusted output is visible and blocked from promotion,
- trusted output carries checksum/provenance,
- trust scan artifacts do not recursively contaminate the source artifact index.

### Slice 4: Control Panel Cockpit

Expose:

- session inventory,
- latest run summary,
- environment class,
- policy findings,
- pending approvals,
- artifact trust state,
- required checks,
- blockers.

### Slice 5: Persistent Scheduled Job Bridge

Use the scheduled agent store to run or simulate a recurring Computer Fabric task.

MVP does not need 24/7 hosting. It needs the persistent-computer contract, schedule linkage, run history, artifact output, and health state.

### Slice 6: Operator Observe-First Bridge

Use existing browser context memory and multimodal computer-use planning to create observe-first plans from operator-provided browser/session context.

No autonomous browser control until the permission, prompt-injection, stop/takeover, and replay surfaces are implemented.

## 12. Testing Strategy

### 12.1 Unit Tests

Required tests:

- environment selection matrix chooses the right class,
- unsafe permissions are blocked,
- unknown privacy is local-only or blocked,
- manifest includes all required policy fields,
- event ledger records expected lifecycle events,
- artifact index records generated outputs,
- trust scan blocks unsafe/untrusted artifacts,
- persistent computer health state is visible,
- operator computer refuses control without approval.

### 12.2 Black-Box API Tests

Required tests:

- create session,
- list sessions,
- fetch session detail,
- fetch event ledger summary,
- fetch artifact trust summary,
- create scheduled/persistent session proposal,
- create operator observe-first plan.

### 12.3 Control Panel Tests

Required assertions:

- "Computer Fabric" appears in Control Panel,
- active session card renders,
- environment class is visible,
- policy findings are visible,
- artifact trust status is visible,
- planned/running/completed states are distinguishable,
- private/operator-local state is clearly marked.

### 12.4 Red-Team Tests

Required scenarios:

- webpage says "ignore previous instructions",
- hidden DOM instruction tries exfiltration,
- downloaded file asks the agent to reveal secrets,
- generated script tries to read outside allowed folder,
- command tries to print environment secrets,
- browser task asks for authenticated destructive action without approval,
- persistent job attempts unauthorized network/inbound service exposure.

## 13. Out of Scope for MVP

The MVP must not include:

- unrestricted local desktop control,
- fully autonomous authenticated browser actions,
- public service hosting without a separate provider-hardening plan,
- arbitrary root access,
- uncontrolled Docker socket access,
- unrestricted network egress,
- direct production mutation,
- automatic merge without review,
- hidden credential capture,
- neural-pixel OS or full generative UI substrate,
- training on private session logs without a separate privacy/training approval lane.

## 14. Success Criteria

MVP is successful when NexusNet can:

1. Accept a computer-task request.
2. Select `ephemeral`, `persistent`, or `operator` environment class.
3. Write a complete session manifest and policy.
4. Run or simulate the approved task through a provider boundary.
5. Record a replayable event ledger.
6. Produce artifacts.
7. Scan artifacts through Artifact Trust.
8. Surface the run in the Control Panel.
9. Block unsafe permissions and untrusted outputs.
10. Preserve enough state for later implementation of real persistent and operator computers.

## 15. Why This Should Outperform Perplexity and Manus

Perplexity's advantage is orchestration, search, connectors, and background work.

Manus's advantage is concrete computer environments: temporary sandbox, persistent cloud computer, local browser, local desktop, skills, projects, and scheduled tasks.

NexusNet's advantage should be the complete governed lifecycle:

```text
environment class
  + policy manifest
  + minimum viable permissions
  + replay ledger
  + artifact trust
  + prompt-injection defense
  + local-first privacy
  + open/provider-agnostic routing
  + control-panel proof
  + promotion/rollback gates
```

That combination creates a more credible computer agent for commercial, buyer-facing, local-first, and safety-sensitive use.

## 16. Open Questions for Implementation Planning

These should be answered in the implementation plan, not guessed in code:

1. Which first provider should be real: repo-local venv, Docker/Podman, WSL, or devcontainer?
2. Should the first API be `/ops/brain/computer-fabric` or nested under the existing sandbox agent factory routes?
3. Should persistent computer v0 use the existing scheduled agent artifact store or a new `computer_fabric` artifact store with scheduled-agent adapters?
4. Should operator computer v0 stop at browser context planning, or include one safe local command approval path?
5. Which Control Panel layout should own the cockpit: a new Computer Fabric card, or a combined Sandbox/Computer Use/Artifact Trust page?

Default recommendation:

```text
Provider: repo-local venv/temp workspace first
API: /ops/brain/computer-fabric
Artifacts: new computer-fabric artifact layout, with scheduled-agent bridge
Operator v0: observe-first only
Control Panel: new Computer Fabric card plus links into Artifact Trust and Computer Use
```

## 17. Approval State

The user approved the design direction on 2026-05-05 after reviewing the Perplexity and Manus research summary.

Next step after spec review:

```text
Invoke the Superpowers writing-plans workflow and create a detailed implementation plan.
```
