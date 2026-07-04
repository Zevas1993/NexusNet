# Effect Typed Authority Surface Spec

Status: P2 online assimilation target. Research-only until translated into practical NexusNet TypeScript/Python/Kotlin patterns.

## Source Evidence

- Deno security and permissions docs: https://docs.deno.com/runtime/fundamentals/security/
- Deno run permissions docs: https://docs.deno.com/runtime/reference/cli/run/
- Unison abilities docs: https://www.unison-lang.org/docs/language-reference/abilities-and-ability-handlers/
- Koka effect types paper: https://arxiv.org/abs/1406.2061
- Source status: official docs and primary paper page.

## Finding

Effect systems make side effects explicit. Deno demonstrates runtime permission prompts and deny-by-default I/O, while Unison and Koka show type-level ways to express required effects. NexusNet can borrow the idea without adopting these languages wholesale.

## NexusNet Assimilation Target

Make every NexusNet tool, skill, and agent step declare its effects before execution. The operator should know whether a step reads files, writes files, uses network, spawns processes, calls a connector, sends data externally, or mutates memory.

## Proposed NexusNet Components

- `EffectSignature`: read, write, network, subprocess, connector, memory, browser, desktop, model, and export effects.
- `DeclaredVsObservedEffectTrace`: compares declared effects to runtime behavior and flags undeclared effects.
- `EffectPolicyGate`: checks whether the run grant permits the declared effects.
- `EffectPromptSurface`: shows human-readable effect requests before approval.
- `EffectRegressionSuite`: synthetic tools that attempt undeclared effects and must be blocked.

## Promotion Gates

- Default-deny undeclared effects.
- Require narrower effect scopes for high-authority actions.
- Record effect signatures in tool manifests, traces, and eval reports.
- Test declared-vs-observed enforcement before third-party tool onboarding.

## Risks

- Runtime effect observation is hard across languages and OS boundaries.
- Declarations can lie unless enforced by sandboxing and monitoring.
- Too many prompts can create approval fatigue unless grouped carefully.
