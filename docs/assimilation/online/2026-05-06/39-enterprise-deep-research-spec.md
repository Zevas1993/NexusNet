# Enterprise Deep Research Spec

Status: P2 online assimilation target. Research-only until DRBench assets, licenses, and local evaluation mechanics are inspected.

## Source Evidence

- DRBench repository: https://github.com/ServiceNow/drbench
- DRBench paper entry: https://openreview.net/forum?id=IGYQ4c92e2
- iAgentBench project page: https://iagentbench.github.io/iAgentBench/
- Source status: public repository and official project pages for enterprise deep-research and sensemaking benchmarks.

## Finding

DRBench evaluates deep-research agents across public and private enterprise-like sources including chat, files, spreadsheets, PDFs, websites, and email. It emphasizes multi-hop synthesis, contextual awareness, citations, and insight quality rather than simple fact lookup.

## NexusNet Assimilation Target

Create a DeepResearch lane for NexusNet that treats reports as evidence-bearing artifacts. The agent should plan research, search multiple approved source classes, cite every material claim, distinguish public from private context, and produce an auditable insight ledger.

## Proposed NexusNet Components

- `ResearchQuestionPassport`: audience, decision context, source boundaries, required evidence types, and citation policy.
- `SourceClassLedger`: public web, private docs, chat, spreadsheet, PDF, email, repo, and memory references with access scopes.
- `ClaimEvidenceMatrix`: every conclusion linked to sources, confidence, freshness, and contradictions.
- `InsightScorer`: separates factual coverage, synthesis quality, actionability, and citation correctness.
- `PrivateContextGate`: blocks unapproved export of private workspace material.

## Promotion Gates

- Require citations for decision-impacting claims.
- Separate public-source evidence from private enterprise evidence in the final artifact.
- Preserve negative findings and conflicting evidence.
- Keep deep-research outputs advisory until reviewed for high-stakes decisions.

## Risks

- Deep research can create convincing but overconfident synthesis.
- Private-source handling creates privacy and shareability risk.
- Model-graded insight quality needs calibration against deterministic evidence checks.
