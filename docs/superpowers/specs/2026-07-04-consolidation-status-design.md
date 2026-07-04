# NexusNet Consolidation Status Design

Date: 2026-07-04
Branch: `codex/all-worktrees-integration`
Baseline commit: `b6d6c94a780f531cdd22cf5002542c62f26fdebb`

## Purpose

NexusNet now has an integrated branch with the major worktree slices represented in tracked commits, but the repository still leaves room for confusion because branch names and historical worktree names remain visible. The consolidation update will create one repo-visible source of truth that tells future agents which branch and commit are canonical, which historical worktrees have already been folded in, which artifacts were preserved outside the checkout, and which branch refs are audit history rather than active work.

## Scope

The implementation should be documentation-only. It should not alter runtime code, delete branches, remove preserved artifacts, or change GitNexus configuration.

The primary artifact should be `docs/CONSOLIDATION_STATUS_2026-07-04.md`. That document should be linked from `README.md` and `PROJECT_SUMMARY.md` so future agents see it before making assumptions from branch names alone.

The broader assimilation-target clarification should live separately at `docs/assimilation/ASSIMILATION_TARGET_CLUSTER_REVIEW_2026-07-04.md`. The status document should link to it, but should not absorb its full architectural review. This keeps branch/worktree hygiene separate from assimilation rulings.

## Canonical Facts To Record

- Canonical working branch: `codex/all-worktrees-integration`
- Canonical integrated commit: `b6d6c94a780f531cdd22cf5002542c62f26fdebb`
- GitNexus status at consolidation time: indexed commit and current commit both `b6d6c94`, status up to date
- Only registered worktree after cleanup: `F:/NexusNet/NexusNet`
- Preserved untracked product-sweep artifacts: `F:\NexusNet_Worktrees\_preserved\nexusnet-full-product-sweep-untracked-20260704-113227`
- Integrated ancestor branch refs:
  - `codex/nexusnet-computer-fabric-mvp`
  - `codex/nexusnet-full-product-sweep`
  - `codex/full-assimilation-implementation`
- `codex/universal-runtime-gate` remains a non-ancestor historical branch because the full branch merge was stale/conflicting; its viable runtime-gate content was integrated as `b6d6c94`.

## Document Shape

`docs/CONSOLIDATION_STATUS_2026-07-04.md` should be short and operational:

1. Current canonical state
2. Integrated worktree history
3. Preserved artifacts
4. Branch-ref interpretation
5. Rules for future work
6. Assimilation target review pointer
7. Planned placeholders and future assimilation items
8. Verification evidence from the consolidation run

The language should avoid broad readiness claims. It should say the project is aligned at the tracked repo/worktree level and GitNexus-indexed at the stated commit, not that every product feature is complete.

## Planned Placeholders And Assimilation Items

Placeholders are valid planning artifacts when they clearly represent future work before production. The consolidation document should preserve intentional placeholders, future assimilation items, and roadmap targets as first-class plans, not remove them or treat them as defects.

The distinction should be explicit:

- Valid placeholders identify a planned capability, future assimilation target, open implementation slice, or pre-production gate.
- Valid placeholders state that the item is not production-complete yet.
- Invalid placeholders are ambiguous notes that look like missing information, such as unlabeled `TBD` entries, vague promises, or claims that imply implementation without evidence.

The consolidation document should therefore label future items as `planned`, `pre-production`, `future assimilation`, or `blocked pending evidence` rather than deleting them. This keeps the roadmap intact while preventing future agents from confusing planned work with verified implementation.

## Future Agent Rules

Future work should start from `codex/all-worktrees-integration` unless the user explicitly chooses another branch. Agents should treat old merged branch refs as audit history and should not restart work from those refs without first comparing them to the canonical integration branch. Agents should not delete historical branch refs or preserved artifacts without explicit user approval.

Before any future code change, agents should keep following the project rule to use GitNexus impact analysis for symbol edits and `detect_changes` before committing. Documentation-only updates do not require symbol impact analysis, but they still require `detect_changes` before commit because this repo's `AGENTS.md` requires it before committing.

## Verification Plan

For the documentation-only implementation:

- Run `git status --short --branch` before edits.
- Add the consolidation status document and links from `README.md` and `PROJECT_SUMMARY.md`.
- Run `git diff --check`.
- Run `mcp__gitnexus.detect_changes` with staged scope before commit.
- Commit the documentation update.
- Run `npx gitnexus analyze` after the commit so GitNexus matches the new documentation commit.
- Run `npx gitnexus status`.
- Run `git status --short --branch`.

No pytest run is required for the documentation-only implementation unless code, schemas, routes, or test files are modified.

The spec self-review should not remove intentional roadmap placeholders. It should only correct placeholders that are ambiguous, unlabeled, contradictory, or presented as implemented without evidence.

## Non-Goals

- Delete old branch refs.
- Force-merge `codex/universal-runtime-gate`.
- Move or delete preserved artifact folders.
- Rework project architecture or runtime behavior.
- Rename packages or public entry points.
