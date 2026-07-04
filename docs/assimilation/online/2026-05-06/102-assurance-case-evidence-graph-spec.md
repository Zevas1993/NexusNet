# Assurance Case Evidence Graph Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet certification packets and buyer-facing trust reports.

## Source Evidence

- OMG SACM specification page: https://www.omg.org/spec/SACM/
- OMG SACM 2.3 about page: https://www.omg.org/spec/SACM/2.3/About-SACM
- OMG SACM 2.3 machine-readable documents: https://www.omg.org/spec/SACM/machine-readable
- Source status: official Object Management Group specification pages.

## Finding

Structured assurance cases organize claims, arguments, and evidence so a system's safety or security claims can be audited. This is exactly the missing bridge between NexusNet's many evidence artifacts and a buyer or operator asking, "why should I trust this lane?"

## NexusNet Assimilation Target

Create assurance-case graphs for major NexusNet capabilities: local model execution, high-authority tool use, memory promotion, plugin installation, release packaging, and agent self-improvement suggestions.

## Proposed NexusNet Components

- `AssuranceClaim`: explicit claim about a NexusNet lane, artifact, or deployment.
- `ArgumentNode`: rationale that links claims to subclaims and evidence.
- `EvidenceReference`: trace, eval report, test output, provenance record, source doc, or signed receipt.
- `AssumptionAndContextNode`: conditions under which the claim holds.
- `AssuranceGapReport`: missing evidence, stale evidence, contradicted claims, and unresolved risks.

## Promotion Gates

- Every buyer-facing trust claim must link to concrete evidence.
- Separate evidence from argument; do not let summaries replace raw proof.
- Version assurance cases with the artifacts they describe.
- Mark assumptions and scope limits explicitly.
- Run gap reports before release, certification, or sales handoff.

## Risks

- Assurance cases can become paperwork if they are not generated from real evidence.
- Claims can be overstated unless scope and assumptions are strict.
- Evidence links need durability and privacy classification.
