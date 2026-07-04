# Artifact Provenance Supply Chain Spec

Status: P1 online assimilation target. Research-only until NexusNet release packaging, local build scripts, and buyer handoff artifacts are mapped.

## Source Evidence

- SLSA provenance spec: https://slsa.dev/spec/v1.2/provenance
- SLSA latest spec: https://slsa.dev/spec/latest/
- Sigstore docs: https://docs.sigstore.dev/
- in-toto project: https://in-toto.io/
- Source status: official supply-chain security specifications and project documentation.

## Finding

SLSA, Sigstore, and in-toto provide mature patterns for proving where artifacts came from, how they were built, who or what signed them, and whether they were tampered with. NexusNet can adapt these ideas beyond binaries: model packs, skill bundles, evaluation reports, research artifacts, MCP manifests, and release packages all need provenance.

## NexusNet Assimilation Target

Create signed provenance for every sellable or shareable NexusNet artifact. The goal is buyer trust and local auditability: an operator should know which source, model, config, skill, test run, and build process produced an artifact.

## Proposed NexusNet Components

- `ArtifactProvenanceRecord`: source commit, build command, environment digest, inputs, outputs, timestamp, signer, and verification result.
- `ModelPackAttestation`: model source, license, quantization, checksum, runtime compatibility, and certification result.
- `SkillBundleAttestation`: manifest, permissions, dependencies, tests, red-team status, and signer identity.
- `EvalReportSignature`: benchmark version, dataset version, model route, prompt version, and score digest.
- `ReleaseVerificationCommand`: one command that verifies signatures, checksums, and expected provenance locally.

## Promotion Gates

- Do not publish or hand off release artifacts without checksum and provenance metadata.
- Treat unsigned model packs and third-party skills as untrusted by default.
- Keep local workstation paths out of provenance exported to buyers.
- Re-sign and re-verify whenever build inputs change.

## Risks

- Provenance can leak local paths, usernames, or private build details if not scrubbed.
- Signatures prove origin, not safety or quality.
- Keyless signing and transparency logs may need online access, which must be optional for local-only development.
