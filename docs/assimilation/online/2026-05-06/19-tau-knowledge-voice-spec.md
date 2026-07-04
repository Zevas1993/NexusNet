# Tau Knowledge And Voice Spec

Status: P1 online assimilation target. Research-only until tau3 docs and runnable modes are inspected.

## Source Evidence

- Tau-Knowledge paper: https://arxiv.org/abs/2603.04370
- Tau-Voice paper: https://arxiv.org/abs/2603.13686
- Tau2/tau3 repository: https://github.com/sierra-research/tau2-bench
- Source status: primary paper pages plus public benchmark repository.

## Finding

Tau-Knowledge adds unstructured knowledge retrieval to long-horizon customer-support agents. Agents must find roughly 700 interconnected knowledge documents, discover tools through documentation, and produce policy-compliant state changes. Tau-Voice extends this family to full-duplex voice interaction, where task success drops sharply versus text under noise, accents, and turn-taking dynamics.

## NexusNet Assimilation Target

Use tau3 as a combined RAG-plus-action and voice-reliability target. NexusNet should evaluate whether its retrieval planner can support state-changing actions, whether tools can be discovered safely through docs, and whether voice interaction changes reliability enough to require separate gates.

## Proposed NexusNet Components

- `KnowledgeActionDomain`: unstructured docs, discoverable tool docs, database state, and target state.
- `ToolDiscoveryGate`: separates discovered tool references from verified executable tools.
- `VoiceReliabilityProfile`: clean/noisy/accented input conditions, interruption handling, and pass@k decay.
- `ConversationEfficiencyScore`: success plus number of turns, searches, tool calls, and backtracks.

## Promotion Gates

- Do not let docs alone grant tool authority.
- Require source citations for action-driving policy claims.
- Keep voice benchmarks as simulation until microphone/user-data consent is explicit.
- Compare text and voice paths separately; do not infer one from the other.

## Risks

- Knowledge-grounded tasks can fail from retrieval, reasoning, or policy interpretation; diagnostics must separate these.
- Voice introduces privacy and accessibility concerns beyond text chat.
- Full-duplex realtime APIs may require hosted providers, so local-first alternatives need separate evaluation.
