# Proof Carrying Action Guard Spec

Status: P2 online assimilation target. Research-only until limited to narrow high-value invariants.

## Source Evidence

- Lean 4 project/docs: https://lean4.dev/
- Theorem Proving in Lean 4: https://docs.lean-lang.org/theorem_proving_in_lean4//Introduction/
- Dafny reference manual: https://dafny.org/dafny/DafnyRef/DafnyRef
- F* project site: https://www.fstar-lang.org/
- Why3 docs: https://www.why3.org/doc/
- Source status: official theorem proving and verification-language docs.

## Finding

Lean, Dafny, F*, and Why3 show different ways to make correctness claims checkable by proof assistants or SMT-backed verifiers. NexusNet should not try to prove everything, but high-risk actions can require a compact, checkable obligation before execution.

## NexusNet Assimilation Target

Add proof-carrying action guards for narrow authority boundaries: policy transitions, memory promotion, release manifest signing, model-pack trust decisions, and irreversible file/workspace mutations. The proof artifact can be formal for small invariants or structured and machine-checkable for pragmatic cases.

## Proposed NexusNet Components

- `ActionObligation`: invariant that must hold before an action executes.
- `ProofArtifact`: proof term, verifier output, SMT certificate, or structured witness.
- `ProofCheckerAdapter`: local checker for Lean, Dafny, F*, Why3, or lightweight internal invariants.
- `InvariantLibrary`: approved reusable obligations for authority, privacy, lineage, and rollback.
- `ProofFailureTrace`: explains which obligation failed and blocks execution.

## Promotion Gates

- Start with narrow invariants that are cheap to check and expensive to violate.
- Proof checking must be deterministic and local.
- Fail closed when the proof artifact is missing, stale, or unverifiable.
- Store proof artifact hashes in the run trace.
- Do not let generated proofs silently become production authority without review.

## Risks

- Formal proofs are expensive to author and maintain.
- A proof can certify the wrong property if the obligation is poorly specified.
- Solver-backed checks can be brittle across versions unless pinned.
