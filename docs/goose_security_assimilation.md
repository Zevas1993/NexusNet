# Goose Security Assimilation

## Scope
- Goose-inspired permission modes, sandboxing, persistent instructions, and adversary review are assimilated as bounded security patterns.
- NexusNet explicitly rejects fail-open reviewer failure for high-risk paths.

## What Landed
- Permission-mode catalog and sandbox profile summaries.
- Persistent guardrail instructions that are always-injected conceptually and visible read-only.
- Adversary review service with fail-closed-or-escalate behavior and artifact provenance.

## Operationalization
- Adversary review now classifies high-risk gateway requests into explicit risk families, writes report artifacts, and surfaces family counts and latest report IDs in operator inspection.
- Gateway resolutions now carry fallback reason and policy-path provenance into adversary review rather than only reporting the final decision.
- Review detail endpoints now expose payload and markdown artifacts for bounded operator audit without changing the fail-closed or escalate semantics.
- Additional red-team families now cover chained approval-bypass attempts and recipe/subagent privilege confusion while preserving fail-closed or escalate behavior.
- Extension or ACP privilege-inheritance confusion is now treated as an explicit review family and escalates instead of widening capability silently.
- Bundle-level permission escalation attempts are now surfaced as a separate bounded review family so governed extension artifacts and gateway outcomes can be audited together.
- Gateway-linked Goose execution history now preserves the extension policy-set and bundle-family provenance that high-risk review decisions were made against.
- Adversary reviews now also emit audit-export artifacts so operator review can inspect decision provenance without changing fail-closed semantics.
- Read-only adversary review compare views now highlight risk-family, tool, extension, and decision deltas between two reviews for operator drill-down.
- Visualizer/operator Goose compare controls now surface adversary review comparison alongside gateway, policy, certification, and ACP comparison so high-risk review drift stays visible in the same read-only inspection surface.
- The shared Goose compare surface now groups adversary drift beside lifecycle, certification, permission, ACP, and gateway sections so high-risk operator review stays readable under one read-only compare contract.
- The closeout posture keeps future ACP live probes bounded and provider-gated, which preserves the same fail-closed or escalate discipline if ACP ever moves beyond simulated readiness.

## Boundaries
- High-risk paths never fail open on reviewer failure.
- NexusNet uses fail-closed or escalation to SafetyAO, CritiqueAO, or manual approval.
- The visualizer remains read-only and governance remains authoritative.

## Sources
- Goose permissions guide: https://goose-docs.ai/docs/guides/goose-permissions
- Goose persistent instructions guide: https://goose-docs.ai/docs/guides/using-persistent-instructions
- Goose repository: https://github.com/aaif-goose/goose
