# ASTRA Personal Context Spec

Status: P2 online assimilation target. Research-only until dataset/code are inspected.

## Source Evidence

- ASTRA-bench paper: https://arxiv.org/abs/2603.01357
- Source status: primary paper page.

## Finding

ASTRA-bench evaluates tool-use reasoning and action planning with time-evolving personal context. It reports significant degradation under complex personal context and identifies argument generation as a major bottleneck.

## NexusNet Assimilation Target

Use ASTRA-bench as a consented personal-context test pattern. NexusNet should validate tool arguments against current personal context, temporal state, and user preferences before acting, while keeping private context local and permission-scoped.

## Proposed NexusNet Components

- `PersonalContextFixture`: synthetic life events, preferences, contacts, resources, and temporal updates.
- `ToolArgumentVerifier`: validates required fields, entity references, dates, permissions, and ambiguity.
- `TemporalContextResolver`: resolves current versus historical personal facts with source lineage.
- `ClarifyBeforeActGate`: asks the user when context is insufficient or ambiguous.

## Promotion Gates

- Use synthetic fixtures first; never scrape private personal data by default.
- Require opt-in for any real personal context source.
- Block tool calls with unresolved argument ambiguity.
- Show why a personal context fact was selected.

## Risks

- Personal context is privacy-sensitive even when it appears mundane.
- Tool-argument bugs can cause real-world side effects.
- Longitudinal context can become stale without explicit revision policies.
