# Malus Clean-Room Codex Tool Design

Status: approved direction, pending implementation plan
Date: 2026-05-31
Scope: personal Codex plugin/tool for manifest intake, dependency reconstruction work packets, public-interface analysis, isolated build tasking, and audit/report output inspired by `https://malus.sh/`.

## 1. Purpose

Build a reusable Codex personal plugin named `malus-cleanroom` that lets the agent process dependency manifests and produce clean-room reconstruction packets for selected packages.

The tool should work as an agent aid rather than as a standalone legal service. It can identify packages, collect public documentation and API/interface evidence, generate analysis packets, create builder packets, track source exposure boundaries, and emit reports. It must not claim that a generated artifact is legally cleared, non-infringing, or free of obligations without external review.

The target workflow is:

```text
manifest input
  -> dependency detection
  -> package/license/interface metadata
  -> public-doc/API analysis packet
  -> isolated builder packet
  -> reconstruction task plan
  -> audit ledger and report
```

## 2. Product Shape

Recommended implementation approach: Codex personal plugin.

The plugin should provide a skill and local scripts that Codex can invoke across future sessions. The default plugin location follows the Codex plugin creator defaults:

```text
%USERPROFILE%/plugins/malus-cleanroom/
%USERPROFILE%/.agents/plugins/marketplace.json
```

The NexusNet repository is used only for this Superpowers design and planning trail unless the user separately asks for a repo-local integration.

## 3. User-Facing Commands

The plugin should expose a skill with these operating modes:

```text
intake-manifest
analyze-package
build-analysis-packet
build-builder-packet
quote-manifest
write-report
```

The scripts behind the skill should support:

```text
python scripts/malus_cleanroom.py intake <manifest_path> --out <run_dir>
python scripts/malus_cleanroom.py analyze <run_dir> --ecosystem npm
python scripts/malus_cleanroom.py packet <run_dir> --package <name>
python scripts/malus_cleanroom.py report <run_dir>
```

The implementation plan may rename the script, but the tool should remain callable through one stable entrypoint.

## 4. Supported Inputs

MVP manifest support:

- `package.json`
- `requirements.txt`
- `Cargo.toml`

Future ecosystem support:

- Maven `pom.xml`
- Gradle files
- Go modules
- NuGet project files
- RubyGems
- Composer

The parser should preserve original manifest content, compute a checksum, and write normalized dependency records.

## 5. Core Components

### 5.1 Manifest Parser

Responsibilities:

- detect manifest ecosystem,
- parse package names and requested versions,
- preserve dependency class where available,
- record file checksum,
- reject binary or unsupported files with a clear diagnostic,
- produce `dependencies.json`.

### 5.2 Package Metadata Resolver

Responsibilities:

- resolve package metadata from registry APIs where available,
- capture package homepage, repository URL, docs URL, license field, latest version, declared types/interfaces, and package size where feasible,
- handle offline mode with partial metadata,
- record every network-derived metadata source in the ledger.

The resolver must degrade cleanly when registry access is unavailable.

### 5.3 Public Interface Collector

Responsibilities:

- collect public documentation URLs, README text, API docs, type declarations, examples, and CLI help where available,
- avoid ingesting package source archives by default,
- record exactly which public inputs were read,
- label source categories as `docs`, `api`, `types`, `examples`, `metadata`, or `unknown`.

Source archive ingestion should remain blocked in MVP. If a later version supports source archives for owned code or reviewed exceptions, that must be a separate policy gate.

### 5.4 Analysis Packet Generator

Responsibilities:

- summarize the package purpose,
- list public API surface,
- list behavioral requirements inferred from documentation,
- list examples and edge cases from public docs,
- list compatibility targets,
- list tests the builder should create,
- include source-evidence citations by URL or file reference,
- exclude original package source code.

Output:

```text
analysis-packets/{package_name}/analysis.md
analysis-packets/{package_name}/public-interface.json
analysis-packets/{package_name}/evidence-ledger.jsonl
```

### 5.5 Builder Packet Generator

Responsibilities:

- transform the analysis packet into implementation tasks,
- include required API signatures and behavior specs,
- include suggested tests,
- include non-goals and unknowns,
- exclude raw analysis notes that are not needed for implementation,
- include a clean-room boundary statement.

Output:

```text
builder-packets/{package_name}/README.md
builder-packets/{package_name}/spec.json
builder-packets/{package_name}/test-plan.md
```

### 5.6 Isolation Ledger

Responsibilities:

- record input manifest hash,
- record metadata URLs and timestamps,
- record public-interface sources,
- record blocked source inputs,
- record generated packet hashes,
- record tool version,
- record warnings and policy decisions.

Output:

```text
ledger.jsonl
run-summary.json
```

### 5.7 Report Generator

Responsibilities:

- generate a concise terminal summary,
- write a Markdown report,
- show dependency count, package status, license metadata, source exposure status, packet paths, warnings, and next actions,
- present claims as evidence-backed status, not legal conclusions.

Output:

```text
MALUS_CLEANROOM_REPORT.md
```

## 6. Data Flow

```text
Manifest
  -> Manifest Parser
  -> Dependency Records
  -> Package Metadata Resolver
  -> Public Interface Collector
  -> Analysis Packet Generator
  -> Builder Packet Generator
  -> Isolation Ledger
  -> Report Generator
```

Each stage writes structured files into one run directory:

```text
runs/{timestamp}-{manifest-name}/
  manifest.original
  manifest.normalized.json
  dependencies.json
  package-metadata.json
  ledger.jsonl
  analysis-packets/
  builder-packets/
  MALUS_CLEANROOM_REPORT.md
```

## 7. Boundaries and Claims

The plugin may say:

- package metadata was detected,
- a license string was observed,
- public docs/API/type inputs were read,
- source archives were not ingested by the tool,
- an analysis packet or builder packet was generated,
- a report is ready for review.

The plugin must not say on its own:

- the output is legally cleared,
- attribution is unnecessary,
- copyleft obligations are eliminated,
- the package has been fully replaced,
- infringement is impossible,
- a generated implementation is production-ready without tests.

This keeps the tool useful while preserving a review trail and avoiding unsupported conclusions.

## 8. Error Handling

Expected error cases:

- unsupported manifest type,
- malformed manifest,
- package metadata unavailable,
- network unavailable,
- docs URL missing,
- source archive detected and blocked,
- run directory already exists,
- package name conflicts with filesystem-safe path,
- report requested before analysis is complete.

Errors should be explicit and non-destructive. Partial runs should leave a ledger entry explaining what completed and what failed.

## 9. Testing Strategy

MVP tests:

- parse `package.json` dependencies and devDependencies,
- parse `requirements.txt` pinned and unpinned dependencies,
- parse basic `Cargo.toml` dependencies,
- reject unsupported binary input,
- normalize package names into safe output paths,
- write a ledger entry for every stage,
- block source archive ingestion by default,
- generate analysis packet files from fixture metadata,
- generate builder packet files from fixture analysis,
- generate report with warnings and packet paths,
- support offline fixture mode for deterministic tests.

The tests should not depend on live network calls. Live registry resolution can have a separate smoke command.

## 10. Implementation Plan Questions

The next Superpowers planning step should answer:

1. Should the plugin be created with only `--with-skills --with-scripts --with-marketplace`, or should it also include MCP/app scaffolding?
2. Should the first script be pure Python standard library, or use helper dependencies for TOML parsing and registry calls?
3. Should package metadata be network-disabled by default unless the user passes `--live`?
4. What exact output schema should be frozen for `dependencies.json`, `package-metadata.json`, and `run-summary.json`?
5. Should generated reports use the Malus parody tone, or a neutral engineering/audit tone?

Default recommendation:

```text
Scaffold: skill + scripts + marketplace only
Runtime: Python standard library where possible
Network: fixture/offline default, opt-in live resolution
Schemas: JSON-first, Markdown report second
Tone: neutral report, optional parody skin later
```

## 11. Success Criteria

The first implemented version is successful when Codex can:

1. Invoke the `malus-cleanroom` skill.
2. Run a local script against a fixture `package.json`.
3. Detect dependencies.
4. Write normalized metadata.
5. Generate at least one analysis packet.
6. Generate at least one builder packet.
7. Write an isolation ledger.
8. Write `MALUS_CLEANROOM_REPORT.md`.
9. Validate the plugin manifest.
10. Present the plugin through the personal marketplace.

## 12. Approval State

The user approved the recommended Codex personal plugin approach on 2026-05-31.

Next step after this spec is reviewed:

```text
Invoke the Superpowers writing-plans workflow and create a detailed implementation plan.
```
