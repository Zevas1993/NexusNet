# Privacy Redaction Preflight Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet memory, trace, export, and release workflows.

## Source Evidence

- Microsoft Presidio docs: https://microsoft.github.io/presidio/
- Microsoft Presidio repository: https://github.com/microsoft/presidio
- Guardrails AI docs: https://www.guardrailsai.com/docs
- Source status: official documentation and public repositories.

## Finding

PII detection and anonymization tools such as Presidio show that privacy must happen before prompts, traces, memory writes, eval exports, and shareable artifacts. Guardrail-style validators add the pattern of treating sensitive data checks as composable runtime gates.

## NexusNet Assimilation Target

Add privacy preflight gates for every path that can move data into model context, memory, logs, traces, reports, repos, or buyer handoff artifacts.

## Proposed NexusNet Components

- `SensitiveDataScan`: detected entity, confidence, source span, data class, and action recommendation.
- `RedactionPolicy`: allow, mask, hash, tokenize, drop, or require operator approval.
- `PromptPrivacyGate`: scans context before model calls.
- `TracePrivacyGate`: scans logs and exported traces before persistence or sharing.
- `ArtifactShareabilityGate`: blocks local paths, PII, secrets, private repo data, and sensitive memory from release artifacts.

## Promotion Gates

- Run privacy scans before prompt submission, memory write, trace export, and release packaging.
- Treat workstation paths as shareability risk, not just secrets and API keys.
- Keep raw sensitive spans local and minimize retention.
- Require operator approval before exporting private context.

## Risks

- PII detectors produce false positives and false negatives.
- Redaction can break reproducibility if it removes evidence without placeholders.
- Privacy gates need lane-specific policies for code, docs, screenshots, audio, and memory.
