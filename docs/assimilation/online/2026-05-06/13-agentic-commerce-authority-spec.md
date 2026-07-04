# Agentic Commerce Authority Spec

Status: P3 watchlist. Research-only authority pattern; not a payment implementation plan.

## Source Evidence

- AP2 core protocol specification: https://agentpaymentsprotocol.info/specification/core/
- AP2 prompt-injection red-team paper: https://arxiv.org/abs/2601.22569
- AP2 zero-trust runtime verification paper: https://arxiv.org/abs/2602.06345
- AIP identity/delegation paper: https://arxiv.org/abs/2603.24775
- Source status: protocol documentation plus primary paper pages.

## Finding

Agentic commerce research is useful even outside payments because it treats delegated agent action as a signed, scoped, replay-resistant authority problem. The key patterns are identity, intent, settlement/completion proof, context binding, consume-once semantics, expiration, and runtime verification under concurrency.

## NexusNet Assimilation Target

Translate payment-style authority into a general NexusNet "delegated authority token" for high-impact actions: write files, run commands, use MCP, act in browser/desktop, publish commits, send messages, or access private resources.

## Proposed NexusNet Components

- `AuthorityMandate`: who authorized what, allowed scope, expiration, max spend/risk, and target resource.
- `ConsumeOnceActionToken`: prevents replay of one-time approvals.
- `ContextBoundApproval`: binds approval to exact task, target, source, and current state hash.
- `CompletionProof`: records what action actually happened and whether it matched the mandate.

## Promotion Gates

- Do not implement payments unless explicitly scoped later.
- Start with file/shell/browser authority, where NexusNet already has relevant risk.
- Require human-readable approval previews and machine-verifiable tokens.

## Risks

- Payment protocols are immature and security research is active.
- Authority tokens can add friction if used for low-risk actions.
- Signing without runtime verification still leaves replay and context-redirect gaps.
