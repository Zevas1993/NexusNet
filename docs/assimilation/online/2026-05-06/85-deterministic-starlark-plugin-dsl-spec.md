# Deterministic Starlark Plugin DSL Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet plugin, policy, and build-manifest authoring.

## Source Evidence

- Bazel Starlark language docs: https://bazel.build/rules/language
- Starlark language specification: https://github.com/bazelbuild/starlark/blob/master/spec.md
- Bazel hermeticity docs: https://preview.bazel.build/basics/hermeticity
- Source status: official Bazel docs and authoritative Starlark specification.

## Finding

Starlark is a small, deterministic, hermetic extension language used by Bazel. Its value for NexusNet is not build-system mimicry; it is the idea of a Python-like configuration and plugin DSL that avoids ambient I/O and makes evaluation predictable.

## NexusNet Assimilation Target

Use a deterministic DSL pattern for NexusNet plugin manifests, model-route rules, eval packs, policy bundles, and build recipes. The DSL should be expressive enough to compose constraints but restricted enough to evaluate safely, cacheably, and reproducibly.

## Proposed NexusNet Components

- `DeterministicDslRuntime`: evaluates trusted configuration expressions with no ambient filesystem, network, clock, or subprocess access.
- `PluginRuleFile`: Starlark-like manifest for declaring tools, effects, tests, model routes, and install constraints.
- `DslImportGraph`: records all imports and source digests used by a rule file.
- `DslEvaluationTrace`: deterministic output, warnings, and rejected ambient access.
- `RuleReplayTest`: verifies the same inputs produce identical outputs across machines.

## Promotion Gates

- Deny ambient I/O during rule evaluation.
- Hash all rule inputs and imports.
- Require deterministic ordering for maps, sets, and generated manifests.
- Run replay tests before accepting marketplace or third-party rule bundles.
- Keep high-authority permissions outside the DSL unless separately approved.

## Risks

- A DSL can become a second programming language that needs documentation and support.
- Hermetic evaluation is undermined if host functions expose broad authority.
- Determinism does not imply correctness; generated policy still needs tests.
