# Scientific Provenance Crate Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet research, eval, and memory export formats.

## Source Evidence

- W3C PROV overview: https://www.w3.org/TR/prov-overview/
- W3C PROV data model: https://www.w3.org/TR/prov-dm/
- RO-Crate 1.2 specification: https://www.researchobject.org/ro-crate/specification/1.2/
- RO-Crate project site: https://www.researchobject.org/ro-crate/
- Source status: W3C Recommendations/notes and official RO-Crate specification pages.

## Finding

W3C PROV gives a mature vocabulary for entities, activities, agents, derivation, attribution, and provenance validity. RO-Crate packages research objects with machine-readable metadata. NexusNet can use these patterns for research artifacts, memory exports, eval runs, and source-grounded reasoning dossiers.

## NexusNet Assimilation Target

Package NexusNet research/eval/memory artifacts as provenance crates. A crate should tell a future operator what data was used, what activity transformed it, which model/tool/agent acted, what artifact resulted, and how to reproduce or audit the chain.

## Proposed NexusNet Components

- `ProvenanceCrate`: directory or bundle containing artifacts, metadata, checksums, and privacy policy.
- `ProvEntity`: source document, model pack, prompt, trace, memory, eval report, or release artifact.
- `ProvActivity`: ingest, parse, summarize, evaluate, transform, train, route, or export step.
- `ProvAgent`: human, model, tool, script, connector, or policy engine involved.
- `CrateValidationCommand`: verifies required metadata, checksums, and source links.

## Promotion Gates

- Use stable identifiers and content digests for every entity.
- Preserve raw-source links next to derived summaries.
- Include privacy classification and export restrictions.
- Validate crates before moving them into memory, buyer evidence, or release artifacts.
- Treat provenance crates as evidence carriers, not mutation authority.

## Risks

- Provenance graphs can become too verbose without useful views.
- Packaging private evidence requires redaction and access controls.
- Metadata quality will degrade unless creation is automated.
