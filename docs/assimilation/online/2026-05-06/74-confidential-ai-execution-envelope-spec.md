# Confidential AI Execution Envelope Spec

Status: P2 online assimilation target. Research-only until a real NexusNet deployment profile requires confidential or remote execution.

## Source Evidence

- Confidential Containers overview: https://confidentialcontainers.org/docs/overview/
- Confidential Containers attestation docs: https://confidentialcontainers.org/docs/attestation/
- NVIDIA Confidential Containers attestation docs: https://docs.nvidia.com/datacenter/cloud-native/confidential-containers/latest/attestation.html
- Open Enclave SDK docs: https://openenclave.io/sdk/
- Source status: official project and vendor docs.

## Finding

Confidential containers and enclave systems use remote attestation to prove a workload is running inside a measured trusted execution environment before secrets are released. NVIDIA's documentation extends this pattern to CPU and GPU enclave evidence for model or container decryption. This is not a magic privacy solution, but it is a useful trust envelope for sensitive remote inference and buyer-managed deployments.

## NexusNet Assimilation Target

Define a confidential execution envelope for any future NexusNet run that must leave the local machine while still protecting model packs, user inputs, or private context. The default product posture should remain local-first; this target is for optional high-assurance deployment lanes.

## Proposed NexusNet Components

- `ConfidentialRunProfile`: hardware/TEE type, runtime image, model pack, policy digest, and allowed endpoints.
- `AttestationRecord`: verifier result, measurement, signer identity, expiration, and evidence hash.
- `EncryptedInputEnvelope`: payload encrypted only for an attested runtime measurement.
- `KeyReleasePolicy`: conditions under which decryption keys can be released.
- `ConfidentialTraceDigest`: redacted trace hash proving what ran without exposing private content.

## Promotion Gates

- Release secrets only after attestation passes against an expected policy digest.
- Keep a local fallback path for operators who do not need remote confidential execution.
- Never log plaintext private prompts, secrets, or model keys in the remote environment.
- Record measurement, verifier, and policy version in the run trace.
- Treat side channels, operator trust, and cloud-region boundaries as explicit residual risk.

## Risks

- Confidential computing adds hardware, cloud, and deployment complexity.
- Attestation can prove measurements, not that the measured application is semantically safe.
- Side-channel and supply-chain risks remain and need separate controls.
