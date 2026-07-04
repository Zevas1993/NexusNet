# Content Addressed Evidence DAG Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet traces, memory, evals, and release artifacts.

## Source Evidence

- IPFS Merkle DAG docs: https://docs.ipfs.tech/concepts/merkle-dag/
- IPFS content addressing docs: https://docs.ipfs.tech/concepts/content-addressing/
- IPLD DAG-CBOR spec: https://ipld.io/specs/codecs/dag-cbor/spec/
- IPFS paper: https://arxiv.org/abs/1407.3561
- Source status: official docs and primary paper page.

## Finding

Content addressing gives every artifact an identity derived from its contents. Merkle DAGs and CIDs are a strong pattern for evidence integrity: if a trace, source chunk, model pack, eval report, or prompt changes, its identifier changes too.

## NexusNet Assimilation Target

Create a content-addressed evidence DAG for NexusNet. Memory entries, eval reports, run traces, source chunks, model packs, specs, and release artifacts should link to immutable content digests instead of mutable names alone.

## Proposed NexusNet Components

- `EvidenceCid`: content digest, codec, artifact type, privacy class, and storage location.
- `EvidenceDagNode`: run, trace, source, memory, eval, model, prompt, policy, or release artifact.
- `EvidenceDagEdge`: derived-from, cites, verifies, contradicts, supersedes, or packages.
- `IntegrityCheckCommand`: recomputes digests and reports changed artifacts.
- `PrivateEvidencePolicy`: keeps private CIDs local and blocks public network publication by default.

## Promotion Gates

- Keep content addressing local by default; do not publish private evidence to public networks.
- Record codec and chunking choices because they affect identifiers.
- Link mutable labels to immutable digests.
- Verify evidence DAG integrity before release or buyer handoff.

## Risks

- Content IDs can still reveal sensitive existence patterns if shared.
- Different chunking or encoding creates different IDs for the same logical data.
- Immutable evidence needs redaction strategy when private data was captured by mistake.
