# Data Agent Enterprise Query Spec

Status: P1 online assimilation target. Research-only until DataAgentBench datasets, licenses, and execution runner requirements are inspected.

## Source Evidence

- DataAgentBench repository: https://github.com/ucbepic/DataAgentBench
- DataAgentBench paper: https://arxiv.org/abs/2603.20576
- DS-Bench paper: https://arxiv.org/abs/2505.15621
- DSBench paper: https://arxiv.org/abs/2409.07703
- Source status: public repository plus primary paper pages for data-agent and data-science benchmark families.

## Finding

DataAgentBench stresses realistic enterprise data workloads: multi-database integration, ill-formatted joins, unstructured text transformation, and domain knowledge. DS-Bench and DSBench add data-science coding and analysis depth. Together they point to a data-agent lane where the core failure mode is not syntax, but incorrect assumptions over messy data.

## NexusNet Assimilation Target

Create a DataOps certification lane for NexusNet. Data agents should prove query planning, schema linking, data cleaning, statistical caution, evidence citations, and no-answer behavior before producing business analysis or changing data pipelines.

## Proposed NexusNet Components

- `DataTaskPassport`: data sources, schema map, allowed queries, privacy class, expected answer form, and verifier.
- `SchemaLinkTrace`: table/column/entity matches, join assumptions, and rejected join paths.
- `DataQualityGate`: flags nulls, duplicates, type coercion, malformed keys, and suspicious outliers.
- `StatisticalValidityCheck`: records uncertainty, sample size, test choice, causal limits, and confidence.
- `DataAnswerEvidencePack`: includes query text, result digest, citations, charts, and known caveats.

## Promotion Gates

- Require verifiable queries or code for every analytic claim.
- Block causal claims unless the task and evidence support them.
- Keep private data out of prompts unless local policy explicitly permits it.
- Test "cannot determine from available data" cases.

## Risks

- Data-agent benchmarks can be expensive if they require multiple databases and heavy runners.
- Schema complexity may dominate model quality.
- A plausible chart or written analysis can still be wrong if the joins or assumptions are wrong.
