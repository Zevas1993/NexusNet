# Grammar Constrained Decoder Kernel Spec

Status: P1 online assimilation target. Research-only until mapped against NexusNet model routes, local runtimes, and tool-call parsers.

## Source Evidence

- XGrammar docs: https://xgrammar.mlc.ai/docs/tutorials/constrained_decoding.html
- XGrammar repository: https://github.com/mlc-ai/xgrammar
- XGrammar paper: https://arxiv.org/abs/2411.15100
- LMQL docs: https://lmql.ai/docs/
- Microsoft Guidance page: https://www.microsoft.com/en-us/research/project/guidance-control-lm-output/downloads/
- Source status: official docs, public repositories, and primary paper page.

## Finding

Constrained decoding is a code-level reliability primitive: invalid tokens are masked during sampling so the output must follow a grammar or schema. This is stronger than asking the model to "please return JSON" and is especially valuable for tool calls, plan DSLs, policy decisions, state patches, and verifier outputs.

## NexusNet Assimilation Target

Add a grammar-constrained decoder kernel for high-authority structured outputs. NexusNet should require constrained generation or strict post-validation for plans, tool calls, permissions, memory writes, policy decisions, and eval reports.

## Proposed NexusNet Components

- `StructuredOutputContract`: schema, grammar, decoder backend, model route, validator, and fallback policy.
- `GrammarDecodeTrace`: grammar version, accepted tokens, rejected-token count, parse result, and validation result.
- `ToolPlanGrammar`: constrained format for multi-tool plans before execution.
- `PolicyDecisionGrammar`: constrained allow, deny, approval, sandbox, and redaction decisions.
- `SchemaDriftRegression`: tests real NexusNet schemas against constrained decoders and fallback validators.

## Promotion Gates

- Use constrained decoding only for structure; still validate semantics and policy.
- Benchmark grammar overhead per runtime and model route.
- Keep schema wording stable and versioned because field names can influence model behavior.
- Never execute malformed or partially parsed high-authority outputs.

## Risks

- Grammar engines differ in JSON Schema coverage and runtime overhead.
- Structured correctness does not imply factual or policy correctness.
- Some local runtimes may not support the same constrained-decoding features.
