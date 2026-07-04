# OccuBench Professional Faults Spec

Status: P2 online assimilation target. Research-only until project assets are inspected.

## Source Evidence

- OccuBench paper: https://arxiv.org/abs/2604.10866
- Source status: primary paper page with project page reference.

## Finding

OccuBench evaluates agents across professional occupational domains using language environment simulators. It includes controlled fault injection and highlights that implicit data degradation, such as missing fields or truncated data without obvious error signals, is harder than explicit failures.

## NexusNet Assimilation Target

Use OccuBench as a robustness pattern for expert lanes. NexusNet should not only test whether an expert can complete a task under clean conditions; it should test whether the expert detects bad, missing, stale, or truncated inputs before acting.

## Proposed NexusNet Components

- `ExpertDomainScenario`: industry/domain, tools, simulated environment, documents, and allowed actions.
- `FaultInjectionProfile`: explicit error, implicit degradation, mixed fault, stale data, and missing field variants.
- `DataQualityGate`: detects incomplete, truncated, contradictory, or degraded tool responses.
- `ExpertCapabilityProfile`: per-domain strengths/weaknesses rather than one global agent score.

## Promotion Gates

- Treat simulator quality as part of the benchmark, not a given.
- Require explicit "insufficient data" success cases.
- Keep high-stakes domains as synthetic simulations only unless later approved.

## Risks

- LLM-simulated environments can create false confidence.
- Professional domains may imply legal/medical/financial stakes; keep outputs advisory and synthetic.
- Domain-specific performance can drift with model changes.
