# Red Team Toolchain Spec

Status: P1 online assimilation target. Research-only until tool licenses, payload policies, and local runner safety are inspected.

## Source Evidence

- Promptfoo repository: https://github.com/promptfoo/promptfoo
- Promptfoo red-team configuration: https://www.promptfoo.dev/docs/red-team/configuration/
- PyRIT repository: https://github.com/microsoft/PyRIT
- Garak repository: https://github.com/NVIDIA/garak
- Source status: official public repositories and official tool documentation.

## Finding

Promptfoo, PyRIT, and Garak provide practical open-source red-team and evaluation tooling for LLM applications. Promptfoo is especially relevant because its current red-team plugins include coding-agent, MCP, RAG, exfiltration, sandbox escape, terminal-output injection, and verifier-sabotage categories.

## NexusNet Assimilation Target

Create a local red-team regression pack for NexusNet authority boundaries. The pack should exercise prompt injection, RAG poisoning, MCP tool poisoning, coding-agent sabotage, sandbox escape, secret exfiltration, and cross-session leakage using canaries and blocked test surfaces.

## Proposed NexusNet Components

- `RedTeamCasePassport`: attack class, target surface, payload source, expected refusal or containment behavior, and severity.
- `AttackSurfaceRegistry`: maps browser, shell, file, MCP, memory, RAG, code, and agent-to-agent surfaces.
- `CanarySecretStore`: synthetic secrets and files used only to prove non-exfiltration.
- `RedTeamRunner`: local runner that executes cases, records traces, and produces regression reports.
- `RemediationLedger`: links failed cases to fixes, retests, and residual risk.

## Promotion Gates

- Use canaries and synthetic data only; never test with real private secrets.
- Block payloads that would create real malware, credential theft, or uncontrolled exfiltration.
- Run destructive tests only inside disposable sandboxes.
- Require red-team regressions before enabling new high-authority tools or protocols.

## Risks

- Automated red-team tools produce false positives and false negatives.
- Payload libraries can include unsafe content that needs strict containment.
- Security regressions can be hidden if reports are not wired into release gates.
