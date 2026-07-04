# Trusted Time Attestation Receipts Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet audit, release, and evidence bundles.

## Source Evidence

- RFC 3161 Time-Stamp Protocol: https://www.rfc-editor.org/rfc/rfc3161.html
- Roughtime repository: https://roughtime.googlesource.com/roughtime
- OpenTimestamps project site: https://opentimestamps.org/
- RFC 9334 RATS architecture: https://www.rfc-editor.org/rfc/rfc9334.html
- RFC 9711 Entity Attestation Token: https://www.rfc-editor.org/rfc/rfc9711.html
- Source status: official RFCs and project sites/repositories.

## Finding

Audit evidence needs credible time and credible environment claims. RFC 3161 timestamps, Roughtime-style signed time, OpenTimestamps, and RATS/EAT attestation tokens show how to bind statements to time, nonce, signer, platform evidence, and verifier policy.

## NexusNet Assimilation Target

Add trusted time and attestation receipts to NexusNet high-value evidence. Release builds, eval pass claims, memory exports, signed statements, and operator approvals should be able to prove when they existed and which environment or verifier produced them.

## Proposed NexusNet Components

- `TrustedTimestampReceipt`: artifact hash, timestamp source, policy, nonce, signature, and verification status.
- `AttestationReceipt`: environment evidence, verifier identity, nonce, claims, and expiration.
- `ReceiptBundle`: time, attestation, signature, transparency, and provenance receipts linked to one artifact.
- `ReceiptVerifier`: validates nonce, signature, policy, artifact hash, freshness, and revocation/status.
- `EvidenceTimeLine`: orders evidence events using signed receipts and local monotonic run sequence.

## Promotion Gates

- Timestamp hashes, not raw private content.
- Require nonce or challenge binding where replay matters.
- Keep accepted timestamp/attestation authorities configurable for offline deployments.
- Record verification failures rather than silently falling back to local clock time.
- Do not overstate time evidence; it proves existence before/at a time, not correctness.

## Risks

- Trusted time authorities and attestation verifiers become trust dependencies.
- Public timestamping can leak artifact existence metadata.
- Attestation claims are only as strong as the verifier policy and hardware/root trust.
