# OWASP Agentic Skill Risk Spec

Status: P1 online assimilation target. Research-only until current OWASP drafts are pinned and mapped to NexusNet's actual skill/tool inventory.

## Source Evidence

- OWASP MCP Top 10: https://owasp.org/www-project-mcp-top-10/
- OWASP Agentic Skills Top 10: https://owasp.org/www-project-agentic-skills-top-10/
- OWASP Agentic AI threats and mitigations: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- Source status: official OWASP project and OWASP GenAI Security Project pages.

## Finding

OWASP's agentic work separates protocol/tool risks from skill-behavior risks. That distinction matters for NexusNet because MCP security is not enough; a skill can be dangerous because of what it orchestrates even when the underlying tool call is syntactically valid.

## NexusNet Assimilation Target

Add an agentic skill risk registry. Every NexusNet skill, MCP server, protocol bridge, and tool bundle should carry a risk passport covering capabilities, data access, authority level, failure modes, approval requirements, and audit expectations.

## Proposed NexusNet Components

- `SkillRiskPassport`: purpose, owner, capability scope, data scope, authority level, dependencies, and threat class.
- `ToolManifestAttestation`: versioned manifest for exposed tools, schemas, permissions, and provenance.
- `BehaviorPolicyGate`: evaluates whether a skill workflow is permitted, not only whether a tool schema is valid.
- `ThirdPartySkillReview`: onboarding checklist for external skills, MCP servers, and protocol bridges.
- `SkillAuditTimeline`: changes, approvals, incidents, revocations, and retest history.

## Promotion Gates

- Default-deny third-party skills until reviewed and explicitly enabled.
- Require agent identity, session scope, revocation, and traceability for high-authority skills.
- Separate read-only, mutating, networked, financial, shell, and credential-adjacent capabilities.
- Re-review skills when manifests, dependencies, or prompt instructions change.

## Risks

- OWASP agentic guidance is a living body of work and may change quickly.
- Risk passports can become checkbox artifacts if not enforced in runtime gates.
- A safe individual tool can still become unsafe when composed into an autonomous workflow.
