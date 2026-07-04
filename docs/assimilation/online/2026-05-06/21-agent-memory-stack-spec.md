# Agent Memory Stack Spec

Status: P1 online assimilation target. Research-only until local memory candidates are inspected and mapped to NexusNet memory/KAC code.

## Source Evidence

- Memory survey: https://arxiv.org/abs/2603.07670
- Hindsight paper: https://arxiv.org/abs/2512.12818
- Hindsight repository: https://github.com/vectorize-io/hindsight
- MemMachine paper: https://arxiv.org/abs/2604.04853
- MemX paper: https://arxiv.org/abs/2603.16171
- MemoryAgentBench paper: https://arxiv.org/abs/2507.05257
- xMemory paper: https://arxiv.org/abs/2602.02007
- Source status: primary paper pages plus public repository page.

## Finding

Recent memory work is converging on a few core principles: memory is a write-manage-read loop, raw episodes should remain available to preserve ground truth, retrieval should avoid redundant top-k similarity, reflection must be auditable, and systems need selective forgetting, contradiction handling, low-confidence rejection, and privacy governance.

## NexusNet Assimilation Target

Refine NexusNet memory and KAC around evidence-preserving memory. The system should store raw episodes and refs separately from synthesized beliefs, distinguish facts from reflections, reject low-confidence recalls, and expose why a memory was retrieved.

## Proposed NexusNet Components

- `MemoryWriteGate`: filters what may be stored, what must be redacted, and what remains refs-only.
- `EpisodePreservingStore`: keeps raw source episodes immutable with derived memories linked back to them.
- `MemoryHierarchy`: themes, entities, episodes, raw messages, beliefs, and contradictions.
- `RecallConfidenceGate`: supports low-confidence rejection instead of forcing spurious memories into context.
- `SelectiveForgettingPolicy`: explicit retention, redaction, expiration, and operator removal paths.

## Promotion Gates

- Never overwrite raw source episodes with summaries.
- Keep private-memory export disabled by default.
- Require provenance for every reflected belief.
- Test retrieval on multi-session, temporal, multi-hop, and "no answer in memory" cases.

## Risks

- Memory benchmark claims are highly sensitive to model/provider and dataset setup.
- Local-first memory can still leak private information through logs and traces.
- Reflection can blur evidence and inference unless schema boundaries are enforced.
