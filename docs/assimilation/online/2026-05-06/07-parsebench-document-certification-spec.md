# ParseBench Document Certification Spec

Status: P1 online assimilation target. Research-only until dataset/license are verified.

## Source Evidence

- ParseBench paper: https://arxiv.org/abs/2604.08538
- LiteParse v2.0 release: https://www.llamaindex.ai/blog/liteparse-v2-0-runs-everywhere
- Source status: primary paper page with linked Hugging Face dataset and GitHub code.
- Reverified: 2026-05-31 via `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`.

## Finding

ParseBench argues that document parsing for agents must preserve semantic correctness, not just text similarity. Tables, charts, content faithfulness, semantic formatting, and visual grounding matter because downstream agents use parsed content for decisions. The 2026-05-31 reverify adds LiteParse v2.0 as a current parser-adapter candidate because its source describes a Rust rewrite with Node, Python, Rust, and WASM distribution paths and local/browser parsing options.

## NexusNet Assimilation Target

Add document-ingestion certification before KAC or memory promotion. Parsed tables, charts, scanned PDFs, and visually grounded claims should carry parser confidence, dimension-specific validation, and source-page lineage.

## Proposed NexusNet Components

- `DocumentParsePassport`: records parser, version, file type, page count, dimensions checked, and failure classes.
- `TableChartVerifier`: validates table structure, chart data extraction, and cell/value provenance.
- `VisualGroundingCheck`: ties extracted claims to page regions or rendered evidence.
- `KAC Parse Gate`: blocks promotion of low-confidence or uncertified extracted content.

## Promotion Gates

- Require page-level provenance for document-derived facts.
- Keep raw source references outside repo when they contain private documents.
- Add parser regression fixtures before importing new parser backends.
- Treat LiteParse as a backend candidate only after local install, malformed-document, citation-preservation, OCR, and permission-boundary tests pass.

## Risks

- Enterprise documents can carry private data; benchmark-derived fixtures must be sanitized.
- OCR confidence is not semantic correctness.
- Parser scorecards must not imply all documents are safe for autonomous action.
