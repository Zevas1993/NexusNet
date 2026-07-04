# SCITT Supply Chain Receipt Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet release, eval, model-pack, and evidence statements.

## Source Evidence

- IETF SCITT working group: https://datatracker.ietf.org/wg/scitt/
- SCITT specifications index: https://scitt.io/scitt-specs.html
- SCITT architecture draft: https://www.ietf.org/archive/id/draft-ietf-scitt-architecture-22.html
- Source status: IETF working group pages and SCITT specification index.

## Finding

SCITT focuses on signed supply-chain statements and transparency receipts. This complements Sigstore and TUF by giving NexusNet a pattern for making statements about artifacts, runs, evaluations, and model packs, then registering those statements with verifiable receipt evidence.

## NexusNet Assimilation Target

Create SCITT-style signed statements for NexusNet artifacts: model pack accepted, eval suite passed, release built, memory corpus exported, plugin reviewed, or policy bundle promoted. The statement and receipt should be machine-verifiable and linked into the evidence DAG.

## Proposed NexusNet Components

- `SignedSupplyChainStatement`: issuer, subject artifact, claim type, claim payload, and signature.
- `TransparencyReceipt`: receipt proving the signed statement was registered by an accepted transparency service.
- `StatementPolicy`: allowed issuers, claim schemas, and required evidence for each statement type.
- `ReceiptVerifier`: validates statement signature and receipt inclusion proof.
- `EvidenceStatementLedger`: links statements to model packs, releases, evals, traces, and docs.

## Promotion Gates

- Define claim schemas before generating signed statements.
- Verify issuer identity and receipt before trusting a statement.
- Keep private statements local or in a private transparency service.
- Link every promotion statement to the raw evidence it summarizes.
- Test stale, forged, mismatched-subject, and missing-receipt cases.

## Risks

- Receipts prove registration of a statement, not that the claim is true.
- Public transparency can leak private release or customer metadata.
- Statement schemas need governance or they become marketing labels.
