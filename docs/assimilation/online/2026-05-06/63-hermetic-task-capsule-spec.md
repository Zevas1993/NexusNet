# Hermetic Task Capsule Spec

Status: P1 online assimilation target. Research-only until Windows compatibility and NexusNet release/build paths are tested.

## Source Evidence

- Nix official docs: https://nix.dev/index.html
- Bazel hermeticity docs: https://bazel.build/concepts/hermeticity
- Bazel remote caching docs: https://bazel.build/remote/caching
- Devbox docs: https://www.jetify.com/devbox
- Reproducibility with Nix paper: https://arxiv.org/abs/2402.00424
- Source status: official docs and primary paper page.

## Finding

Hermetic environments are a quiet force multiplier. If a task capsule pins tools, dependencies, environment variables, and build inputs, NexusNet can replay code tasks, evals, model conversions, and release builds without relying on workstation accidentals.

## NexusNet Assimilation Target

Create hermetic task capsules for coding agents, eval runs, model-pack certification, and release packaging. A capsule should define the environment as data and make drift visible.

## Proposed NexusNet Components

- `TaskCapsuleSpec`: tools, versions, env vars, inputs, outputs, cache policy, network policy, and host constraints.
- `CapsuleLockfile`: resolved package versions, hashes, runtime images, and fetch sources.
- `CapsuleReplayCommand`: one command to recreate the environment and rerun the task.
- `HostDriftReport`: explains which local host details were ignored, used, or leaked.
- `CapsuleCachePolicy`: separates safe build cache from private or non-reproducible artifacts.

## Promotion Gates

- Avoid local absolute paths in exported capsule metadata.
- Verify capsule replay on a clean workspace before trusting results.
- Keep network access explicit and disabled by default for replay.
- Record capsule digest in eval and release provenance.

## Risks

- Nix and Bazel can be heavy for Windows-first workflows.
- Hermeticity can be undermined by undeclared network, time, locale, GPU, or environment dependencies.
- Reproducible setup does not guarantee secure or correct behavior.
