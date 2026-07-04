# AI BOM Supply Chain Graph Spec

Status: P1 online assimilation target. Research-only until NexusNet release artifacts, model packs, skill bundles, and dependencies are inventoried.

## Source Evidence

- CycloneDX docs: https://cyclonedx.org/docs/
- SPDX specification: https://spdx.dev/specifications/
- OpenSSF Scorecard repository: https://github.com/ossf/scorecard
- GUAC repository: https://github.com/guacsec/guac
- Source status: official SBOM specifications and public OpenSSF repositories.

## Finding

SBOM ecosystems such as CycloneDX and SPDX, plus OpenSSF Scorecard and GUAC, provide concrete patterns for representing components, dependencies, vulnerabilities, licenses, provenance, and artifact relationships. NexusNet needs an AI-specific bill of materials that covers more than code packages.

## NexusNet Assimilation Target

Create an AI BOM for NexusNet releases, model packs, skills, MCP servers, eval packs, datasets, prompts, and runtime dependencies.

## Proposed NexusNet Components

- `AiBomRecord`: component type, source, version, license, checksum, provenance, owner, and risk class.
- `ModelComponentRecord`: weights, tokenizer, quantization, adapter, runtime, dataset references, and certification status.
- `SkillComponentRecord`: tool manifests, permissions, prompts, dependencies, tests, and red-team status.
- `DependencyRiskView`: license, vulnerability, maintenance, provenance, and local path shareability risks.
- `ReleaseBomExporter`: produces buyer-safe machine-readable and human-readable inventories.

## Promotion Gates

- Every shareable artifact needs a BOM entry before release.
- Third-party models, datasets, and skills must include license and source status.
- Keep local paths and private environment metadata out of exported BOMs.
- Link BOM records to provenance and eval reports.

## Risks

- Standard SBOM formats may not natively capture prompts, evals, model routes, or memory packs.
- BOM completeness depends on disciplined release automation.
- A BOM identifies components but does not prove they are safe.
