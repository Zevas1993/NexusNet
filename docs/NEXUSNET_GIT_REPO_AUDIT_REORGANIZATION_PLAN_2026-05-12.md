# NexusNet Git And Repository Reorganization Audit - 2026-05-12

Status: non-destructive Git hygiene and reorganization plan.

Purpose: classify the dirty NexusNet worktree, identify what should be preserved, what should be ignored or externalized, what needs shareability review, and how to stage the repo without losing patent/canon evidence.

This document intentionally does not move, delete, reset, or stage files. It is the map that should come before any large cleanup.

## Executive Summary

The repo is not simply "dirty" from temporary files. It contains a mixed pile of:

- tracked code changes
- untracked product modules
- untracked tests
- untracked canon and research docs
- untracked patent packet files
- untracked Control Panel/UI work
- generated runtime proof files
- local tooling and index helper files

That means the fix is not `git clean` or one giant commit. The correct path is classification, privacy review, staged commits by subsystem, and only then folder reorganization.

## Current Git Snapshot

Captured on 2026-05-12 from `F:\NexusNet\NexusNet`.

| Field | Value |
| --- | --- |
| Branch | `codex/knowledge-artifact-compiler` |
| HEAD | `f1986e5 docs: record video assimilation verification` |
| Tracked modified files | 46 |
| Untracked files | 387 |
| GitNexus index date | 2026-05-06 |
| GitNexus stats | 1257 files, 21746 symbols, 32126 relationships, 211 processes |

Tracked modified files are concentrated in:

- `nexus/api/app.py`
- `nexus/services.py`
- `nexus/storage.py`
- `nexusnet/core/`
- `nexusnet/runtime/qes/`
- `nexusnet/teachers/`
- `nexusnet/visuals/`
- `tests/`
- `ui/`
- `.gitignore`
- `pytest.ini`

Untracked files by top-level directory:

| Top-level path | Count |
| --- | ---: |
| `docs` | 185 |
| `nexusnet` | 93 |
| `tests` | 59 |
| `patent` | 29 |
| `runtime` | 13 |
| `ui` | 3 |
| `tools` | 2 |
| `.gitnexusignore` | 1 |
| `config` | 1 |
| `nexus` | 1 |

Untracked files by extension:

| Extension | Count |
| --- | ---: |
| `.md` | 204 |
| `.py` | 154 |
| `.json` | 7 |
| `.svg` | 7 |
| `.txt` | 3 |
| `.docx` | 2 |
| `.jsonl` | 2 |
| `.yaml` | 2 |
| `.css` | 1 |
| `.html` | 1 |
| `.js` | 1 |
| `.pdf` | 1 |
| `.ps1` | 1 |
| `.gitnexusignore` | 1 |

## Largest Untracked Files

Large untracked files are important because they affect repo size, review quality, and public shareability.

| Size | Path | Classification |
| ---: | --- | --- |
| 8,792,280 | `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` | Internal canon/source map; shareability review required |
| 612,050 | `nexusnet/hive/substrate.py` | Product code, needs code review and tests |
| 407,683 | `nexusnet/growth/production_spine.py` | Product code, needs code review and tests |
| 317,385 | `ui/control-panel/app.js` | Product UI, needs lint/runtime review |
| 258,035 | `docs/autonomous/PRODUCTION_SPINE_RUN_LOG.md` | Run log/evidence, decide publish policy |
| 163,169 | `docs/autonomous/DATASET_RADAR_RUN_LOG.md` | Run log/evidence, decide publish policy |
| 149,246 | `nexusnet/canon/realization.py` | Product/canon scorecard code |
| 143,254 | `tests/test_hive_neural_substrate.py` | Test evidence |
| 131,835 | `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md` | Canon |
| 125,400 | `docs/superpowers/plans/2026-05-06-video-assimilation-implementation.md` | Implementation plan/evidence |
| 112,733 | `tests/test_growth_lifecycle_orchestrator.py` | Test evidence |
| 95,592 | `nexusnet/curriculum/dataset_radar.py` | Product code |
| 84,341 | `docs/superpowers/plans/2026-05-06-nexusnet-full-assimilation-implementation.md` | Implementation plan/evidence |
| 79,092 | `tools/generate_nexusnet_patent_packet.py` | Patent/tooling code |
| 79,068 | `tests/test_nexusnet_production_spine.py` | Test evidence |

## Initial Risk Findings

### 1. The Dirty Tree Is Mixed-Authority

The same dirty state contains product code, patent docs, raw source maps, generated proof files, and tests. A single broad commit would be hard to review and hard to revert.

Recommended action: split into a staged commit series by subsystem.

### 2. Some Internal Docs Are Not Public-Ready

A local path/shareability scan found internal path or sandbox-history references in:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`
- `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- `docs/superpowers/plans/2026-05-06-nexusnet-full-assimilation-implementation.md`

Some references are intentional boundary language, such as warnings about `C:\Users\...`, but others are historical source paths or sandbox links. Treat the exhaustive canon book and raw planning docs as internal until sanitized.

Recommended action: create a public/shareable evidence bundle separate from internal canon.

### 3. No High-Confidence Secrets Found In The Focused Scan

A focused scan for common API key/private key patterns over selected project code/docs did not find obvious API keys or private key blocks.

This is not a complete security audit. It does not prove the repo is public-safe.

Recommended action: run a full secret scanner before publishing or pushing.

### 4. Runtime Evidence Is Not All Source Code

Untracked `runtime/` files include pytest collection logs and live proof artifacts. Some of these may be valuable evidence, but they should not all be treated as normal source files.

Recommended action: decide which runtime proofs are durable evidence and which should be ignored or archived outside the repo.

### 5. Line Ending Policy Is Too Broad

`.gitattributes` currently contains:

```text
* text=auto
```

Git reports LF-to-CRLF warnings across many files. This does not prove a broken repo, but it creates noise during staging and diff review.

Recommended action: normalize line endings in a dedicated commit only after content classification is complete.

### 6. `.gitnexusignore` Is Untracked

The `.gitignore` ignores `.gitnexus`, but `.gitnexusignore` itself is untracked. Given the repo's AGENTS/GitNexus workflow, `.gitnexusignore` is probably a project config file and should be reviewed for tracking.

Recommended action: inspect and likely track `.gitnexusignore` in a Git hygiene commit.

## Classification Matrix

| Class | Examples | Default decision |
| --- | --- | --- |
| Core product code | `nexusnet/core`, `nexusnet/hive`, `nexusnet/growth`, `nexusnet/runtime`, `nexus/api/app.py` | Review, test, stage by subsystem |
| Product tests | `tests/test_hive_neural_substrate.py`, `tests/test_nexusnet_production_spine.py`, KAC/self-improvement tests | Stage with matching code subsystem |
| Operator UI | `ui/control-panel`, `ui/visualizer`, `nexusnet/visuals` | Stage after UI smoke/lint review |
| Patent packet | `patent/nexusnet_micro_entity_packet_2026-05-01/` | Preserve; review shareability; stage as patent packet commit |
| Canon docs | `docs/NEXUSNET_*`, canon matrix, post-book addendum | Preserve; separate internal/public classification |
| Research specs | `docs/assimilation/online`, `docs/research`, research diff docs | Keep under docs, possibly move later to `docs/research/` taxonomy |
| Superpowers plans/specs | `docs/superpowers/` | Keep as implementation evidence, but not primary user docs |
| Runtime evidence | `runtime/live-proofs`, `runtime/pytest_collect_*.txt` | Archive or selectively track evidence; ignore scratch |
| Local caches/scratch | `.pytest-tmp`, `pytest-cache-files-*`, `.gitnexus`, runtime temp roots | Ignore, do not stage |

## Proposed Repository Taxonomy

Do not move files immediately. This is the target shape after classification and tests.

```text
docs/
  canon/
    complete-book/
    addenda/
    ledgers/
  patent/
    application-packet/
    support/
    shareable-evidence/
  architecture/
    brain-core/
    hive-substrate/
    runtime/
    memory/
    governance/
  research/
    refreshes/
    candidates/
    assimilation/
  operations/
    run-logs/
    release-checklists/
  superpowers/
    specs/
    plans/

nexusnet/
  core/
  hive/
  growth/
  memory/
  knowledge/
  runtime/
  policy/
  security/
  protocols/
  teachers/
  evals/
  vision/
  canon/

nexus/
  api/
  services/
  storage/
  operator/

ui/
  control-panel/
  visualizer/

runtime/
  state/
  config/
  live-proofs/
```

Notes:

- The taxonomy should be applied gradually.
- Keep source support links valid while reorganizing docs.
- If files move, update patent support charts and docs links in the same commit.
- Avoid moving the exhaustive canon book until a clean shareability decision exists.

## Recommended Commit Series

Use small reviewable commits. Do not stage everything at once.

### Commit 1 - Git Hygiene Baseline

Candidate files:

- `.gitignore`
- `.gitattributes` if line-ending policy changes
- `.gitnexusignore` if reviewed and approved
- this audit document

Purpose:

- establish ignore rules and local tooling boundaries
- reduce future status noise

Verification:

```powershell
git status --short
git diff --check
```

### Commit 2 - Patent Packet And Patent Orientation Docs

Candidate files:

- `patent/nexusnet_micro_entity_packet_2026-05-01/**`
- `tools/generate_nexusnet_patent_packet.py`
- `docs/NEXUSNET_PATENT_ARCHITECTURE_DOSSIER_2026-05-12.md`
- `docs/NEXUSNET_PROJECT_READING_WALKTHROUGH_2026-05-12.md`

Purpose:

- preserve the patent support packet and reviewer map

Verification:

```powershell
rg -n "TBD|TODO|PLACEHOLDER" patent docs/NEXUSNET_PATENT_ARCHITECTURE_DOSSIER_2026-05-12.md docs/NEXUSNET_PROJECT_READING_WALKTHROUGH_2026-05-12.md
rg -n "C:\\Users\\|F:\\|/mnt/data|sandbox:/" patent docs/NEXUSNET_PATENT_ARCHITECTURE_DOSSIER_2026-05-12.md docs/NEXUSNET_PROJECT_READING_WALKTHROUGH_2026-05-12.md
```

### Commit 3 - Canon And Source Map Docs

Candidate files:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
- selected research refresh docs

Purpose:

- preserve internal source record

Precondition:

- decide whether the complete canon book is tracked as internal source material or moved to a private evidence package.

Verification:

```powershell
rg -n "C:\\Users\\|F:\\|/mnt/data|sandbox:/" docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md
```

### Commit 4 - Knowledge Artifact Compiler And KAC Consumers

Candidate files:

- `docs/compiled_knowledge_artifact_layer.md`
- `nexusnet/knowledge/**`
- KAC changes in `nexusnet/growth/`, `nexusnet/dreaming/`, and consumer modules
- `tests/test_knowledge_artifact_compiler.py`
- matching Control Panel card changes

Verification:

```powershell
pytest -q tests/test_knowledge_artifact_compiler.py
node --check ui/control-panel/app.js
```

### Commit 5 - Hive Neural Substrate

Candidate files:

- `nexusnet/hive/**`
- `nexusnet/canon/realization.py`
- hive substrate tests
- related specs under `docs/superpowers/specs/`

Verification:

```powershell
pytest -q tests/test_hive_neural_substrate.py tests/test_hive_neural_network_internals.py tests/test_node_registry_snapshot.py
```

### Commit 6 - Growth, Production Spine, Dreaming, And Self-Improvement

Candidate files:

- `nexusnet/growth/**`
- `nexusnet/dreaming/engine.py`
- `nexusnet/core/self_review.py`
- `nexusnet/core/self_improvement/**`
- matching tests
- selected autonomous run logs if retained

Verification:

```powershell
pytest -q tests/test_hive_model_growth_engine.py tests/test_nexusnet_production_spine.py tests/test_growth_lifecycle_orchestrator.py tests/test_self_improvement_layer.py tests/test_self_review_gate.py
```

### Commit 7 - Runtime, Teachers, Evaluation, And Control Panel

Candidate files:

- `nexusnet/runtime/**`
- `nexusnet/teachers/**`
- `nexusnet/evals/**`
- `nexusnet/visuals/**`
- `ui/control-panel/**`
- `ui/visualizer/**`
- matching tests

Verification:

```powershell
pytest -q tests/test_teacher_registry.py tests/test_teacher_provenance.py tests/test_teacher_routing.py tests/test_runtime_workload_scorecards.py tests/test_inference_economy_router.py tests/test_nexusnet_visualizer.py
node --check ui/control-panel/app.js
node --check ui/visualizer/app.js
```

### Commit 8 - Host API And Nexus Platform Changes

Candidate files:

- `nexus/api/app.py`
- `nexus/services.py`
- `nexus/storage.py`
- `nexus/models/**`
- host platform tests

Verification:

```powershell
pytest -q tests/test_admin_endpoints.py tests/test_hardware_matrix_endpoint.py tests/test_nexus_phase1_foundation.py
```

### Commit 9 - Runtime Evidence Policy

Candidate files:

- selected `runtime/live-proofs/**`
- selected `runtime/pytest_collect_*.txt`
- docs/run logs that need to stay in repo

Alternative:

- move bulky runtime proof bundles to release artifacts or private evidence storage
- keep only a manifest in Git

Verification:

```powershell
git status --short runtime
```

## Immediate Non-Destructive Commands

These commands audit without deleting or staging:

```powershell
git status --short
git diff --stat
git diff --name-status
git ls-files -o --exclude-standard
git diff --check
```

Classify untracked files:

```powershell
git ls-files -o --exclude-standard | ForEach-Object {
  $top = ($_ -split '[\\/]')[0]
  [pscustomobject]@{ Top = $top; Path = $_ }
} | Group-Object Top | Sort-Object Count -Descending | Select-Object Count,Name
```

Find large untracked files:

```powershell
git ls-files -o --exclude-standard | ForEach-Object {
  $item = Get-Item -LiteralPath $_ -ErrorAction SilentlyContinue
  if ($item) { [pscustomobject]@{ Length = $item.Length; Path = $_ } }
} | Sort-Object Length -Descending | Select-Object -First 50
```

Focused high-confidence secret scan:

```powershell
rg -n "OPENAI_API_KEY\s*=|ANTHROPIC_API_KEY\s*=|HF_TOKEN\s*=|HUGGINGFACE.*TOKEN\s*=|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----" docs patent nexusnet nexus config tests --glob "*.md" --glob "*.py" --glob "*.yaml" --glob "*.json" --glob "!docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"
```

Shareability scan:

```powershell
rg -n "C:\\Users\\|F:\\|/mnt/data|sandbox:/|fileciteturn|Pasted%20text|Zevas1993|ChrisBoyd" docs patent README.md PROJECT_SUMMARY.md --glob "*.md"
```

## GitNexus Requirements

AGENTS.md requires GitNexus-assisted safety:

- Use GitNexus context/query for unfamiliar code.
- Run impact analysis before editing symbols.
- Run `gitnexus_detect_changes()` before committing.

Equivalent tool actions in this session:

- `mcp__gitnexus__.context`
- `mcp__gitnexus__.impact`
- `mcp__gitnexus__.detect_changes`

Because the GitNexus index is from 2026-05-06 and the current tree includes many later untracked files, use GitNexus as orientation and verify against disk. After classification and before final commit series, rerun:

```powershell
npx gitnexus analyze
```

Then run:

```text
mcp__gitnexus__.detect_changes(repo="NexusNet", scope="all")
```

## Files To Avoid Deleting

Do not delete these categories during cleanup:

- patent packet files
- canon docs
- post-book addendum and assimilation ledger
- tests matching untracked product modules
- runtime proof files until their evidentiary value is decided
- `.gitnexusignore` until reviewed

## Files Likely To Ignore Or Externalize

Candidates for ignore or external evidence storage:

- transient pytest cache directories
- temp runtime roots
- generated local scratch artifacts
- bulky proof outputs that can be reproduced
- private raw transcript exports if any are outside the generated canon
- local browser/profile capture artifacts

Do not add a broad ignore pattern that hides real source, docs, or patent evidence.

## Public/Private Boundary

Suggested boundary:

### Public Or Buyer-Shareable After Review

- `README.md`
- selected architecture docs
- patent packet after practitioner/shareability review
- sanitized source support chart
- product code and tests after cleanup
- release notes and supported setup docs

### Internal Source Evidence

- exhaustive complete canon book
- raw transcript-derived source maps
- long autonomous run logs
- superpowers plans with local path scan commands
- runtime proof details that expose workstation paths or temporary folders

### Never Public Without Explicit Review

- secrets
- raw private prompts or transcripts
- local profile/browser captures
- proprietary third-party code copied into evidence
- model weights or licensed materials not cleared for redistribution

## Reorganization Rules

1. Preserve history and evidence before moving files.
2. Make one subsystem move per commit.
3. Update links in the same commit as any doc move.
4. Keep patent source support chart valid.
5. Keep tests beside code changes.
6. Keep runtime proof policy separate from product code commits.
7. Do not rewrite history unless a committed privacy leak is confirmed and the user explicitly authorizes history cleanup.
8. Do not use `git reset --hard` or mass clean commands.

## First Safe Cleanup Pass

Recommended first pass:

1. Review `.gitnexusignore`.
2. Add or revise ignore rules for only known local scratch paths.
3. Add this audit doc, the patent dossier, and the reading walkthrough.
4. Run `git diff --check`.
5. Run focused markdown grep against the three new docs.
6. Do not stage unrelated dirty files yet.

## Bottom Line

NexusNet's Git state is fixable, but it needs a deliberate commit plan. The repo currently contains real product work and patent/canon evidence mixed with generated artifacts. The safe move is to preserve the evidence, classify the workspace, create shareability boundaries, and commit in subsystem-sized slices. The unsafe move is to clean or stage everything broadly.
