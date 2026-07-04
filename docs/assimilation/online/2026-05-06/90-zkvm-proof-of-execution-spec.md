# zkVM Proof Of Execution Spec

Status: P2 online assimilation target. Research-only until limited to tiny, high-value verification kernels.

## Source Evidence

- RISC Zero project repository: https://github.com/risc0/risc0
- RISC Zero receipt API docs: https://docs.rs/risc0-zkvm/latest/risc0_zkvm/struct.Receipt.html
- RISC Zero proof-system paper: https://dev.risczero.com/proof-system-in-detail.pdf
- SP1 repository: https://github.com/succinctlabs/sp1
- Source status: official project repositories, API docs, and primary proof-system documentation.

## Finding

zkVMs can produce cryptographic receipts that a computation was executed by a specific program image and yielded public output. This is too expensive for broad NexusNet agent work today, but it can be valuable for small proof kernels: eval scoring, policy checks, release manifest checks, or buyer-verifiable acceptance gates.

## NexusNet Assimilation Target

Define a proof-of-execution lane for narrow NexusNet verification programs. A verifier should be able to check that an accepted artifact passed a specific public verifier without rerunning the full private workflow.

## Proposed NexusNet Components

- `ProofKernel`: small deterministic program for policy, eval, release, or digest verification.
- `ProofInputCommitment`: hash of private inputs, public inputs, and source artifact digests.
- `ExecutionReceipt`: zkVM receipt, image id, public journal/output, and verifier version.
- `ProofVerifierAdapter`: local verifier for accepted zkVM receipt formats.
- `ProofPromotionPolicy`: decides when proof evidence is required or optional.

## Promotion Gates

- Use only for small deterministic kernels with stable inputs.
- Verify image id, receipt, public output, and verifier version.
- Do not treat proof success as proof that the policy itself is wise.
- Keep private inputs private and expose only intentional public outputs.
- Fuzz proof kernels and include normal non-ZK test coverage.

## Risks

- zkVMs are complex and can have soundness or completeness bugs.
- Proof generation can be expensive and operationally awkward.
- A proof can faithfully execute the wrong verifier logic.
