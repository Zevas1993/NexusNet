# Verifiable Agent Credential Passport Spec

Status: P2 online assimilation target. Research-only until mapped to NexusNet agent identity, tool certification, and buyer trust flows.

## Source Evidence

- W3C Verifiable Credentials Data Model 2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C Verifiable Credentials overview: https://www.w3.org/TR/vc-overview/
- W3C DID Core: https://www.w3.org/TR/did-core/
- W3C VC 2.0 Recommendation announcement: https://www.w3.org/news/2025/the-verifiable-credentials-2-0-family-of-specifications-is-now-a-w3c-recommendation/
- Source status: W3C Recommendation and official overview/news pages.

## Finding

Verifiable Credentials provide a standard model for issuer-holder-verifier claims secured against tampering. DIDs provide a decentralized identifier model. For NexusNet, the practical use is not user identity hype; it is portable, verifiable claims about agents, model packs, eval results, plugin reviews, and buyer deployments.

## NexusNet Assimilation Target

Create an agent credential passport that can present machine-verifiable claims: model route certified, tool sandbox tested, eval suite passed, release signed, plugin reviewed, or buyer instance configured with a specific trust root.

## Proposed NexusNet Components

- `AgentCredential`: signed claim about an agent, tool, model pack, eval, or deployment.
- `CredentialIssuerRegistry`: accepted issuers, keys, trust levels, and revocation/status mechanisms.
- `CredentialPresentation`: subset of credentials disclosed to an operator, buyer, or verifier.
- `AgentPassportView`: Control Panel surface showing current credentials and gaps.
- `CredentialVerificationTrace`: verification result, issuer, proof method, status, and subject match.

## Promotion Gates

- Credentials must bind to immutable artifact digests, not vague product names.
- Verify issuer, signature/proof, subject, expiration, and status before display.
- Avoid exposing private deployment details in credentials intended for external sharing.
- Treat credentials as claims requiring evidence links, not absolute truth.
- Provide a revocation or supersession path.

## Risks

- DID/VC ecosystems are broad and can become integration-heavy.
- Bad issuers can sign misleading claims.
- Credential metadata can leak customer or deployment information.
