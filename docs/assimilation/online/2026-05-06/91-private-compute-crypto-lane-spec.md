# Private Compute Crypto Lane Spec

Status: P2 online assimilation target. Research-only until NexusNet has a narrow privacy-preserving compute use case.

## Source Evidence

- OpenFHE project site: https://openfhe.org/
- OpenFHE documentation: https://openfhe-development.readthedocs.io/
- MP-SPDZ repository: https://github.com/data61/MP-SPDZ
- FHE developer resources: https://fhe.org/learn/developer/
- Source status: official project docs, source repository, and community technical reference site.

## Finding

FHE and MPC make it possible to compute over encrypted or privately held data under strict constraints. They are not general replacements for local inference, but they are useful for narrow privacy-preserving comparisons, aggregates, or scoring where raw data cannot be shared.

## NexusNet Assimilation Target

Design a private compute lane for very small, bounded computations: private benchmark aggregation, cross-organization capability scoring, encrypted preference tallies, or shared safety statistics without exposing raw traces.

## Proposed NexusNet Components

- `PrivateComputeTask`: declarative computation, input type, crypto backend, and leakage budget.
- `EncryptedSignalBundle`: encrypted inputs, public parameters, consent record, and source digest.
- `MpcOrFheBackendAdapter`: adapter for accepted FHE or MPC libraries.
- `PrivateResultVerifier`: verifies result format, participant threshold, and privacy settings.
- `CryptoCostEstimate`: expected runtime, memory, communication, and hardware requirements.

## Promotion Gates

- Start with aggregates and comparisons, not arbitrary inference.
- Record exactly what leakage is allowed through output, timing, metadata, and participant set.
- Require cryptography review before production use.
- Keep fallback local-only paths for operators who do not need shared private compute.
- Benchmark cost before promising product behavior.

## Risks

- FHE and MPC are easy to overpromise and hard to operate.
- Output leakage can still reveal sensitive patterns.
- Performance may be unacceptable for interactive agent workflows.
