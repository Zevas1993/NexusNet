# CUE Constraint Config Kernel Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet config, manifest, and policy validation.

## Source Evidence

- CUE documentation: https://cue.dev/docs/
- CUE language docs: https://cuelang.org/docs/
- CUE official modules docs: https://cue.dev/docs/official-modules/
- Source status: official CUE documentation.

## Finding

CUE treats configuration, schema, validation, policy constraints, querying, and code generation as one constraint system. This is a strong fit for NexusNet because many failures come from partially valid configs: model packs missing license fields, tools declaring vague effects, memory entries lacking source status, or policy bundles drifting from UI controls.

## NexusNet Assimilation Target

Create a constraint kernel for NexusNet manifests. The same source of truth should validate model cards, runtime routes, tool effects, plugin metadata, eval packs, release manifests, and Control Panel settings.

## Proposed NexusNet Components

- `NexusConstraintSchema`: shared constraints for models, tools, policies, memory, evals, and release artifacts.
- `ConfigUnificationCheck`: merges defaults, local overrides, package manifests, and operator choices, then rejects conflicts.
- `ConstraintModuleRegistry`: versioned official NexusNet schemas for plugin and model authors.
- `ManifestExplainCommand`: explains why a manifest fails and which constraint rejected it.
- `ConstraintDriftReport`: compares live app state to declared schema constraints.

## Promotion Gates

- Validate every imported plugin, model pack, and policy bundle before install.
- Keep schema versions explicit and source-controlled.
- Generate UI forms and docs from the same constraints where practical.
- Reject unknown or misspelled high-risk fields unless explicitly allowed.
- Run fixture tests for invalid manifests, stale versions, and conflicting overrides.

## Risks

- Constraint languages can be hard to debug without good explanation surfaces.
- Overly strict schemas can block useful experimentation.
- Generated artifacts can drift if the schema is not treated as the source of truth.
