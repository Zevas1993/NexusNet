# Reproducible Rebuilder Network Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet release, model-pack, and plugin build gates.

## Source Evidence

- Reproducible Builds docs: https://reproducible-builds.org/docs/
- NixOS reproducible builds status: https://reproducible.nixos.org/
- OSS Rebuild docs: https://docs.oss-rebuild.dev/
- GNU Guix manual: https://guix.gnu.org/manual/
- Source status: official reproducible-builds, NixOS, OSS Rebuild, and GNU Guix documentation.

## Finding

Reproducible builds let independent infrastructure verify that a binary artifact corresponds to source and build inputs. For NexusNet, the hidden win is not just release security; it is buyer trust for model pack tooling, plugins, eval runners, native helpers, and packaged builds.

## NexusNet Assimilation Target

Create a rebuilder lane for NexusNet artifacts. Release bundles, native helper binaries, plugin packages, and eval runners should have reproducibility metadata and, where practical, independent rebuild evidence.

## Proposed NexusNet Components

- `RebuildRecipe`: source digest, environment digest, commands, expected artifact digests, and toolchain versions.
- `IndependentRebuildReport`: third-party or separate-machine rebuild result and diffoscope-style summary.
- `ArtifactReproducibilityScore`: reproducible, partially reproducible, unreproducible, or not applicable.
- `BuildVarianceLedger`: records timestamps, paths, ordering, locale, randomness, and compiler sources of nondeterminism.
- `BuyerVerificationBundle`: minimal instructions and metadata for a buyer to verify artifacts.

## Promotion Gates

- Record build inputs and environment before publishing any release artifact.
- Use separate rebuild infrastructure for high-value artifacts.
- Store diffs for unreproducible outputs rather than hiding them.
- Treat reproducibility as evidence, not as a replacement for signing or testing.
- Avoid embedding local workstation paths or timestamps in shareable artifacts.

## Risks

- Many ecosystems require cleanup before bit-for-bit reproducibility is realistic.
- Rebuilders can be expensive for large native or model-related artifacts.
- Reproducible malware is still malware; this only proves correspondence.
