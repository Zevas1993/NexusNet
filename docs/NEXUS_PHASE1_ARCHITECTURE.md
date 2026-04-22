# Nexus Phase 1 Architecture

## Core Separation

### NexusNet
The neural wrapper/core:

- attaches teacher and specialist models
- owns the canonical wrapped inference path
- shapes prompts, memory, compression, retrieval, and reflection
- records benchmark, optimization, and architecture history
- forms the bridge from wrapper intelligence to native student emergence

### Nexus
The operational platform around the core:

- hosts APIs, CLI, and ops surfaces
- routes work into NexusNet
- records traces, approvals, and experiments
- manages runtime and governance at the system level

### Future Native NexusNet
The longer-horizon native model path:

- expert capsules
- router evolution
- distillation lineages
- dream-generated candidate data
- benchmark-gated promotion into the platform

The repo must preserve this distinction. NexusNet is already the active brain wrapper. More native student components remain a staged foundry track.

## Canonical Runtime Spine

Phase 1 canonical core code lives in `nexusnet/`, with the surrounding host runtime in `nexus/`.

Core path:

1. `nexus.services.build_services`
2. `nexusnet.core.NexusBrain`
3. `nexusnet.adapters`
4. `nexusnet.memory.NeuralMemoryCortex`
5. `nexusnet.telemetry.BrainTelemetryLogger`
6. `nexusnet.benchmarks.BenchmarkHarness`
7. `nexus.operator.OperatorKernel`
8. `nexus.api.app`

Legacy surfaces remain as compatibility shims:

- `app/main.py`
- `apps/api/main.py`
- selected `core/*` and `services/*` modules needed by old tests and scripts

## Perceive -> Plan -> Act -> Reflect

### Perceive

- ingest request and session state
- pull recent working memory
- optionally retrieve local knowledge

### Plan

- select AO
- select expert capsule
- resolve model alias and runtime backend
- compute approval requirement

### Act

- NexusNet assembles prompt with memory and retrieval context
- NexusNet invokes the attached model adapter
- NexusNet falls back to the mock runtime if the selected backend fails

### Reflect

- NexusNet critiques groundedness and hallucination risk
- NexusNet writes episodic, semantic, and optimization memory
- NexusNet writes telemetry logs
- the host platform persists execution trace
- append audit event

## Module Map

### Ship Now

- `nexusnet.core`
- `nexusnet.adapters`
- `nexusnet.memory`
- `nexusnet.telemetry`
- `nexusnet.benchmarks`
- `nexusnet.dreaming`
- `nexusnet.reflection`
- `nexusnet.curriculum`
- `nexusnet.distillation`
- `nexus.operator`
- `nexus.ao`
- `nexus.agents`
- `nexus.models`
- `nexus.runtimes`
- `nexus.memory`
- `nexus.retrieval`
- `nexus.critique`
- `nexus.governance`
- `nexus.experiments`
- `nexus.api`
- `nexus.cli`
- `nexus.tools`
- `nexus.schemas`

### Prototype Next

- `nexus.curriculum`
- `nexus.dreaming`
- `nexus.foundry`

### Research Track

- learned router policies
- native expert capsules
- shared substrate plus expert composition
- energy-aware routing refinements
- multimodal native substrate work

### Vision Only

- autonomous production self-rewrite
- native superiority claims without held-out evidence

## Storage and Lineage

SQLite is the authority for:

- model registrations
- capability cards
- runtime profiles
- traces and critiques
- memory records
- approvals
- experiment records

Filesystem artifacts are used for:

- retrieval ingest payloads
- dream records
- benchmark outputs
- foundry datasets
- rollback bundles

Every self-improvement path must remain reversible through lineage, approvals, and artifact retention.

## Assimilated External Patterns

The current Phase 1 design intentionally absorbed several high-value implementation patterns from external CLI-agent research work:

- preflight doctor checks
- explicit permission modes
- multi-scope config precedence
- workspace manifests
- model alias and provider-prefix resolution
- shadow-pool dreaming instead of direct production mutation
- compatibility-preserving migration instead of aggressive flattening
- governance mindset for output and promotion control

These are design inputs, not copied product identity.

## Early Mistakes To Avoid

- do not merge Nexus and NexusNet back into one vague label
- do not reintroduce multiple canonical API apps
- do not let the runtime layer collapse to one backend
- do not let dream or tuning outputs bypass approval
- do not remove traceability to simplify implementation
- do not let stale docs describe APIs that no longer exist

## Recommended Near-Term Build Order

1. Harden canonical `nexus/` services and shims
2. Expand `nexusnet/` with dreaming, curriculum, reflection, and distillation loops
3. Add richer ops views over traces, memory, approvals, and transcript state
4. Expand runtime profiling and quantization ledgers
5. Build specialist evaluation suites and student checkpoint artifacts
6. Start more native NexusNet experiments only behind explicit foundry gates
