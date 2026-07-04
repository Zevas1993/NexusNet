# Secure Update Trust Root Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet model packs, skills, plugins, and release artifacts.

## Source Evidence

- TUF specification: https://theupdateframework.io/spec/
- TUF project site: https://theupdateframework.io/
- TUF survivable key compromise paper: https://theupdateframework.io/papers/survivable-key-compromise-ccs2010.pdf
- Notary Project docs: https://notaryproject.dev/docs/
- Sigstore Rekor docs: https://docs.sigstore.dev/logging/overview/
- Source status: official specifications, project docs, and primary paper.

## Finding

Secure update systems need more than artifact hashes. TUF-style metadata roles, threshold signatures, expiry, and rollback protection address update-server compromise patterns, while Notary and Sigstore/Rekor provide signing and transparency patterns for OCI and supply-chain artifacts.

## NexusNet Assimilation Target

Create a secure update trust root for NexusNet model packs, skills, plugins, runtime bundles, eval packs, and commercial releases. Updates should be signed, versioned, auditable, rollback-protected, and locally verifiable.

## Proposed NexusNet Components

- `TrustedRoot`: local trust metadata, threshold keys, roles, expiry, and rotation history.
- `TargetMetadata`: artifact digest, version, length, compatibility, license, and policy class.
- `UpdateManifest`: signed manifest for model packs, skills, plugins, and release bundles.
- `TransparencyLogRecord`: optional Rekor or private transparency anchor for released artifacts.
- `RollbackProtection`: remembered latest trusted version and anti-freeze checks.

## Promotion Gates

- Verify signatures, hashes, length, compatibility, and expiry before install.
- Reject rollback to older trusted versions unless operator explicitly enters recovery mode.
- Separate signing roles for root, targets, snapshots, and timestamps where practical.
- Keep offline/local verification possible for buyer-owned deployments.
- Test compromised mirror, stale metadata, wrong target length, and rollback cases.

## Risks

- Key management is operationally hard and must be documented for buyers.
- A trusted signature does not prove the artifact is useful or safe.
- Transparency logs can leak release metadata if used without a privacy plan.
