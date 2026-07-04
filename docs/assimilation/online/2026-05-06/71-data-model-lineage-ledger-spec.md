# Data Model Lineage Ledger Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet datasets, eval packs, model packs, and research artifacts.

## Source Evidence

- OpenLineage homepage: https://openlineage.io/
- OpenLineage repository: https://github.com/OpenLineage/OpenLineage
- lakeFS docs: https://docs.lakefs.io/v1.73/
- MLflow Model Registry docs: https://www.mlflow.org/docs/2.2.1/model-registry.html
- DataLad reproducibility paper: https://arxiv.org/abs/2505.06558
- Source status: official docs, public repository, and primary paper pages.

## Finding

Data and model lineage tools solve a recurring AI product problem: knowing which data, code, run, model, prompt, and environment produced a result. NexusNet already needs this across evals, model packs, research reports, memory, and release artifacts.

## NexusNet Assimilation Target

Add a lineage ledger that connects data inputs, model routes, prompts, eval runs, artifacts, and releases. This is the operational layer beneath candidate promotion and buyer-safe packaging.

## Proposed NexusNet Components

- `LineageRunRecord`: run ID, job, dataset, model, prompt, code commit, environment, inputs, outputs, and status.
- `DatasetVersionRecord`: source, checksum, license, schema, split, filters, and privacy class.
- `ModelVersionRecord`: weights, tokenizer, quantization, adapter, runtime, and certification.
- `LineageQuerySurface`: answer "what produced this?" and "what used this?" locally.
- `PromotionEvidenceBundle`: lineage plus eval plus provenance plus reviewer decision.

## Promotion Gates

- Every promoted model, prompt, eval, and release artifact needs lineage.
- Preserve source licenses and privacy classes with lineage records.
- Keep private datasets out of exported buyer-safe reports unless scrubbed.
- Link lineage to content-addressed evidence and AI BOM records.

## Risks

- Lineage without enforcement becomes passive documentation.
- Too much metadata can leak private workspace details.
- External lineage platforms may be heavier than NexusNet needs.
