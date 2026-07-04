# Static Taint Flow Gate Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet source scanning, plugin review, and generated-code promotion.

## Source Evidence

- CodeQL data flow docs: https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/
- CodeQL C/C++ data flow docs: https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-cpp/
- CodeQL Go data flow docs: https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-go/
- Semgrep taint analysis docs: https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/overview
- Source status: official CodeQL and Semgrep documentation.

## Finding

Static data-flow and taint analysis tracks untrusted or sensitive data from sources to sinks through code. NexusNet can adapt this beyond classic web vulnerabilities: prompt injection flows to tool calls, secrets flowing to logs, private memory flowing to exports, and untrusted plugin input reaching shell/network sinks.

## NexusNet Assimilation Target

Add a taint-flow gate for NexusNet code, generated patches, plugins, and tool adapters. Before promotion, code should be scanned for source-to-sink flows that violate privacy, authority, or sandbox rules.

## Proposed NexusNet Components

- `TaintSourceCatalog`: prompts, retrieved docs, private memory, credentials, connector payloads, and untrusted plugin input.
- `SensitiveSinkCatalog`: logs, network calls, shell commands, filesystem writes, memory promotion, external model calls, and release artifacts.
- `TaintRulePack`: CodeQL/Semgrep-style rules for NexusNet-specific flows.
- `GeneratedPatchFlowReport`: taint findings attached to an agent-authored code patch.
- `FlowGateDecision`: allow, warn, require review, or block.

## Promotion Gates

- Run taint rules before accepting generated code in high-authority modules.
- Keep source and sink catalogs tied to NexusNet policy classes.
- Require human review for private-data-to-external-sink findings.
- Convert confirmed findings into regression rules.
- Track false positives separately instead of disabling entire rule packs.

## Risks

- Static analysis can miss dynamic behavior and reflection-heavy code.
- False positives can create review fatigue.
- Taint rules must be maintained as code and data flows evolve.
