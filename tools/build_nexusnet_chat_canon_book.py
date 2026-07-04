from __future__ import annotations

import json
import os
import re
import textwrap
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CAPTURE_ROOT = Path("runtime/artifacts/chatgpt-project-captures/playwright_api_capture_2026-04-28")
OUTPUT_PATH = Path("docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md")


@dataclass
class MessageRecord:
    conv_index: int
    conv_title: str
    conv_id: str
    seq: int
    ref: str
    role: str
    create_time: str
    content_type: str
    model_slug: str
    node_id: str
    parent: str
    children: int
    text: str


DECISION_MARKERS = [
    "final decision",
    "decision:",
    "[final decision]",
    "locked",
    "canon",
    "canonical",
    "accepted",
    "approved",
    "decided",
    "became",
    "must",
    "should",
    "explicitly",
    "not merely",
    "not just",
    "not to be",
    "rejected",
    "ruled out",
]

UNRESOLVED_MARKERS = [
    "unresolved",
    "deferred",
    "not settled",
    "not fully settled",
    "not yet",
    "missing",
    "gap",
    "open question",
    "question:",
    "risk",
    "concern",
    "needs more",
    "left unresolved",
    "not implemented",
    "unknown",
]

ARTIFACT_MARKERS = [
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    "GET /",
    "POST /",
    "config/",
    "nexusnet/",
    "nexus/",
    "ops/",
    "tests/",
    "runtime/",
    "MemoryNode",
    "NexusBrain",
]

CONCEPT_TERMS = [
    "NexusBrain",
    "brain-first",
    "neural core",
    "neural network core",
    "Assistant Orchestrators Hive",
    "AO",
    "expert capsule",
    "19 expert",
    "Mini-NexusNet",
    "Mixtral",
    "Devstral",
    "MoE",
    "Router",
    "Cortex",
    "Neural Bus",
    "non-linear",
    "nonlinear",
    "chat scaling",
    "scaling",
    "context",
    "1M",
    "2M",
    "RoPE",
    "YaRN",
    "MemoryNode",
    "multi-plane",
    "multi plane",
    "mind map",
    "hypergraph",
    "conceptual",
    "temporal",
    "emotional",
    "procedural",
    "imaginal",
    "social",
    "ethical",
    "metacognitive",
    "goal",
    "spatial",
    "predictive",
    "Recursive Neural Dreaming",
    "recursive dreaming",
    "dreaming",
    "DreamAO",
    "dream_tournament",
    "replay buffer",
    "self-improvement",
    "SelfTrainingAO",
    "MaintenanceAO",
    "CritiqueAO",
    "Consequence",
    "EBT",
    "teacher",
    "distillation",
    "RL",
    "TRL",
    "Verl",
    "RAGEN",
    "SkyRL",
    "NeMo-RL",
    "MCP",
    "A2A",
    "AG-UI",
    "security",
    "privacy",
    "federated",
    "VisualOps",
    "dashboard",
    "UI panel",
    "visualizer",
    "FARA",
    "DeepEyes",
    "LFM2",
    "Qwen",
    "R-Zero",
    "Graphiti",
    "MemOS",
    "runtime",
    "hardware",
    "safe mode",
    "GPU",
    "VRAM",
    "packaging",
    "API",
    "evaluation",
    "eval",
    "benchmark",
    "provenance",
    "license",
]

ASPECTS = [
    {
        "title": "Brain-First Identity And Neural-Core Boundary",
        "terms": ["NexusBrain", "brain-first", "neural core", "neural network core", "not merely", "not just"],
        "explain": "Covers every place the chats define NexusNet as the cognition authority rather than a wrapper, app shell, or tool orchestration layer.",
    },
    {
        "title": "Mixtral, Devstral, MoE, Router, Mini-NexusNets, And Expert Assimilation",
        "terms": ["Mixtral", "Devstral", "MoE", "Router", "Mini-NexusNet", "ExpertBlockAdapter", "expert adaptation"],
        "explain": "Covers the accepted hybrid MoE direction, specialist expert insertion, automated block adaptation, and staged training implications.",
    },
    {
        "title": "Cortex, Neural Bus, Shared Hive Mind, And Non-Linear Scaling",
        "terms": ["Cortex", "Neural Bus", "hive", "non-linear", "nonlinear", "chat scaling", "scaling", "parallel"],
        "explain": "Covers the peer-level Cortex, inter-expert message passing, sparse expert activation, horizontal scaling, and non-linear chat/conversation scaling.",
    },
    {
        "title": "Long Context, Effective Context, RoPE, YaRN, And Conversation Consolidation",
        "terms": ["context", "1M", "2M", "RoPE", "YaRN", "long-context", "conversation", "summary", "retrieval"],
        "explain": "Covers raw context extension, effective context, memory-backed assembly, and the distinction between accepting long input and actually using it.",
    },
    {
        "title": "Multi-Plane Mind Map, MemoryNode, Hypergraph, And Cross-Plane Cognition",
        "terms": ["MemoryNode", "multi-plane", "multi plane", "mind map", "hypergraph", "conceptual", "temporal", "emotional", "procedural", "imaginal", "social", "ethical", "metacognitive", "goal", "spatial", "predictive"],
        "explain": "Covers the multi-tuple mind map, plane-specific embeddings, graph relations, cross-plane message passing, and config-driven plane growth.",
    },
    {
        "title": "Recursive Neural Dreaming, Recursive Learning, Replay, And Self-Improvement",
        "terms": ["Recursive Neural Dreaming", "recursive dreaming", "dreaming", "DreamAO", "replay buffer", "dream_tournament", "self-improvement", "SelfTrainingAO", "MaintenanceAO", "Neural Sleep"],
        "explain": "Covers Cortex-directed individualized dreams, collaborative/competitive dream modes, replay buffers, and gated learning from dream artifacts.",
    },
    {
        "title": "Expert Capsules, Assistant Orchestrators, Council, Critique, And Consequence",
        "terms": ["expert capsule", "19 expert", "Assistant Orchestrators Hive", "AO", "council", "CritiqueAO", "Critique", "Consequence", "Meta Reasoner"],
        "explain": "Covers the expert roster, AO coordination, council/advisory behavior, critique, consequence feedback, and meta-reasoning.",
    },
    {
        "title": "EBT Routing, Decision Traces, Evaluations, Benchmarks, And Provenance",
        "terms": ["EBT", "routing", "trace", "evaluation", "eval", "benchmark", "provenance", "score", "confidence"],
        "explain": "Covers route scoring, trace-first evidence, confidence/risk metadata, benchmark linkage, and provenance-driven readiness.",
    },
    {
        "title": "Teachers, Distillation, RL, Training, And Native Growth",
        "terms": ["teacher", "distillation", "RL", "TRL", "Verl", "RAGEN", "SkyRL", "NeMo-RL", "reward", "training", "native"],
        "explain": "Covers teachers as temporary capability providers, distillation, RL libraries, reward design, native growth, and promotion gates.",
    },
    {
        "title": "Tools, MCP, A2A, AG-UI, Security, Identity, Consent, And Audit",
        "terms": ["MCP", "A2A", "AG-UI", "tool", "security", "identity", "consent", "audit", "sandbox", "permission"],
        "explain": "Covers protocol integration as governed capability rather than cognition, with identity, sandboxing, permissions, and audit.",
    },
    {
        "title": "VisualOps, Operator UI Panels, Visualizer, Diagrams, And Explainability",
        "terms": ["VisualOps", "dashboard", "UI panel", "visualizer", "diagram", "explainability", "3D", "VR", "Dreamspace"],
        "explain": "Covers operator panels, live inspection, neural visualizer, replay/compare workflows, and diagram correctness.",
    },
    {
        "title": "Runtime, Hardware, Local-First Operation, Safe Mode, And Packaging",
        "terms": ["runtime", "hardware", "GPU", "VRAM", "safe mode", "local", "packaging", "API", "deployment", "installer"],
        "explain": "Covers hardware-aware startup, local-first operation, runtime profiles, safe mode, product shell, APIs, and packaging.",
    },
    {
        "title": "Multimodal, GUI/Computer Use, FARA, DeepEyes, LFM2, Qwen, And Vision",
        "terms": ["multimodal", "vision", "audio", "FARA", "DeepEyes", "LFM2", "Qwen", "UI-TARS", "computer use", "GUI"],
        "explain": "Covers multimodal model candidates, GUI interaction, visual/computer-use research, and safety boundaries.",
    },
    {
        "title": "Federation, Privacy, Meta-Evolution, Governance, And Compliance",
        "terms": ["federated", "privacy", "meta-evolution", "governance", "compliance", "GDPR", "HIPAA", "audit", "consent"],
        "explain": "Covers shared learning, privacy, collective improvement, governance, and compliance boundaries.",
    },
    {
        "title": "Research Assimilation And Candidate Registry",
        "terms": ["Graphiti", "MemOS", "R-Zero", "Flash-DMD", "Bloom", "Agent0", "Nemotron", "Anyscale", "candidate", "license"],
        "explain": "Covers research papers, frameworks, candidate libraries, registry posture, and what remains research-only.",
    },
]


def ascii_clean(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2192": "->",
        "\u2713": "[yes]",
        "\u2705": "[yes]",
        "\u26a0": "[warn]",
        "\ufe0f": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return value


def redact(value: str) -> str:
    value = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<email>", value)
    value = re.sub(r"\b[A-Za-z]:\\[^\s\]\)\"'<>|]+(?:\\[^\s\]\)\"'<>|]+)*", "<local_path>", value)
    home_name = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if home_name:
        value = value.replace(home_name, "<user>")
    return value


def clean_text(value: str) -> str:
    value = ascii_clean(value)
    value = redact(value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def inline(value: str, limit: int = 420) -> str:
    value = clean_text(value)
    value = re.sub(r"\s+", " ", value)
    value = value.replace("|", "\\|")
    if len(value) > limit:
        return value[: limit - 3].rstrip() + "..."
    return value


def slug(value: str) -> str:
    value = ascii_clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def iso_time(ts: Any) -> str:
    if ts is None:
        return ""
    try:
        return datetime.fromtimestamp(float(ts), timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"
    except Exception:
        return ""


def content_to_text(content: dict[str, Any] | None) -> tuple[str, str]:
    if not content:
        return "", ""
    content_type = str(content.get("content_type") or "")
    parts = content.get("parts")
    chunks: list[str] = []
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                if "text" in part:
                    chunks.append(str(part["text"]))
                elif "content" in part:
                    chunks.append(str(part["content"]))
                else:
                    chunks.append(json.dumps(part, ensure_ascii=True, sort_keys=True)[:2000])
            else:
                chunks.append(str(part))
    elif parts is not None:
        chunks.append(str(parts))
    elif "text" in content:
        chunks.append(str(content["text"]))
    return content_type, clean_text("\n".join(chunks))


def load_capture_index() -> dict[str, Any]:
    with (CAPTURE_ROOT / "capture_index.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_messages() -> tuple[list[dict[str, Any]], list[MessageRecord]]:
    index = load_capture_index()
    conversations = index["conversations"]
    all_records: list[MessageRecord] = []
    for conv in conversations:
        raw_path = CAPTURE_ROOT / conv["raw_json"]
        with raw_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        mapping = raw.get("mapping", {})
        raw_messages: list[tuple[float, str, dict[str, Any], dict[str, Any]]] = []
        for node_id, node in mapping.items():
            message = node.get("message")
            if not message:
                continue
            create = message.get("create_time")
            sort_time = float(create) if isinstance(create, (int, float)) else -1.0
            raw_messages.append((sort_time, node_id, node, message))
        raw_messages.sort(key=lambda item: (item[0], item[1]))

        seq = 0
        for _, node_id, node, message in raw_messages:
            seq += 1
            content_type, text = content_to_text(message.get("content"))
            meta = message.get("metadata") or {}
            role = ((message.get("author") or {}).get("role") or "").strip() or "unknown"
            all_records.append(
                MessageRecord(
                    conv_index=int(conv["index"]),
                    conv_title=str(conv["title"]),
                    conv_id=str(conv["id"]),
                    seq=seq,
                    ref=f"C{int(conv['index']):02d}M{seq:04d}",
                    role=role,
                    create_time=iso_time(message.get("create_time")),
                    content_type=content_type,
                    model_slug=str(meta.get("model_slug") or ""),
                    node_id=node_id,
                    parent=str(node.get("parent") or ""),
                    children=len(node.get("children") or []),
                    text=text,
                )
            )
    return conversations, all_records


def message_source_path(record: MessageRecord) -> str:
    safe_title = slug(record.conv_title).replace("-", "_")
    return f"capture/all_message_nodes/{record.conv_index:02d}_{safe_title}_{record.conv_id}.md"


def find_lines(text: str, markers: list[str], limit_per_message: int = 8) -> list[str]:
    if not text:
        return []
    lowered_markers = [marker.lower() for marker in markers]
    found: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if len(line) < 4:
            continue
        lower = line.lower()
        if any(marker in lower for marker in lowered_markers):
            found.append(inline(line, 520))
            if len(found) >= limit_per_message:
                break
    if found:
        return found
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
    for sentence in sentences:
        lower = sentence.lower()
        if any(marker in lower for marker in lowered_markers):
            found.append(inline(sentence, 520))
            if len(found) >= min(3, limit_per_message):
                break
    return found


def extract_headings(text: str) -> list[str]:
    headings = []
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(inline(f"{match.group(1)} {match.group(2)}", 220))
    return headings


def concept_matches(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term_in_text(term, text)]


def term_in_text(term: str, text: str) -> bool:
    if len(term) <= 3 and re.fullmatch(r"[A-Za-z0-9]+", term):
        return re.search(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", text, re.IGNORECASE) is not None
    return term.lower() in text.lower()


def snippet_for_terms(text: str, terms: list[str], limit: int = 520) -> str:
    compact = re.sub(r"\s+", " ", clean_text(text))
    lower = compact.lower()
    positions = [lower.find(term.lower()) for term in terms if lower.find(term.lower()) >= 0]
    if not positions:
        return inline(compact, limit)
    start = max(0, min(positions) - 120)
    end = min(len(compact), min(positions) + limit)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return inline(prefix + compact[start:end] + suffix, limit)


def write_table(lines: list[str], headers: list[str], rows: list[list[str]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")


def build_book() -> dict[str, Any]:
    conversations, records = load_messages()
    records_by_conv: dict[int, list[MessageRecord]] = defaultdict(list)
    for record in records:
        records_by_conv[record.conv_index].append(record)

    concept_index: dict[str, list[MessageRecord]] = {term: [] for term in CONCEPT_TERMS}
    for record in records:
        for term in CONCEPT_TERMS:
            if term_in_text(term, record.text):
                concept_index[term].append(record)

    lines: list[str] = []
    lines.append("# NexusNet Complete Chat Canon Book And Source Index")
    lines.append("")
    lines.append("Date compiled: 2026-04-28")
    lines.append("")
    lines.append(
        "This book is a generated, source-linked companion to the compact canon. It reads the complete raw ChatGPT project API exports for the 39 captured NexusNet conversations and accounts for every message node. It is designed as a navigable index and explanatory map, not a replacement for the raw transcript files."
    )
    lines.append("")
    lines.append("## How To Read This Book")
    lines.append("")
    lines.append("- `CxxMyyyy` references identify a specific captured conversation and message-node order, for example `C01M0005`.")
    lines.append("- Every chapter has source references back to the raw export set. The raw exports remain the full verbatim record.")
    lines.append("- Excerpts are privacy-redacted and shortened where needed. They are used for navigation and explanation, not as the only evidence.")
    lines.append("- The source ledgers include every captured message node so omissions are visible.")
    lines.append("- The one known inaccessible project chat remains excluded until ChatGPT exposes it or an export is provided.")
    lines.append("")

    lines.append("## Master Table Of Contents")
    lines.append("")
    toc_items = [
        "Source Coverage",
        "Conversation Index",
        "Concept Index",
        "Decision And Canon Marker Index",
        "Unresolved And Risk Marker Index",
        "Artifact And Interface Index",
        "Aspect Chapters",
        "Conversation Source Chapters",
        "Known Gaps",
    ]
    for item in toc_items:
        lines.append(f"- [{item}](#{slug(item)})")
    lines.append("")

    lines.append("## Source Coverage")
    lines.append("")
    role_counts = Counter(record.role for record in records)
    write_table(
        lines,
        ["Metric", "Value"],
        [
            ["Captured conversations", str(len(conversations))],
            ["Captured message nodes", str(len(records))],
            ["User nodes", str(role_counts.get("user", 0))],
            ["Assistant nodes", str(role_counts.get("assistant", 0))],
            ["Tool nodes", str(sum(count for role, count in role_counts.items() if role not in {"user", "assistant", "system"}))],
            ["System nodes", str(role_counts.get("system", 0))],
            ["Known inaccessible chat", "`Training LLM with ChatGPT`"],
        ],
    )

    lines.append("## Conversation Index")
    lines.append("")
    conv_rows = []
    for conv in conversations:
        conv_records = records_by_conv[int(conv["index"])]
        conv_rows.append(
            [
                str(conv["index"]),
                inline(str(conv["title"]), 90),
                f"`{conv['id']}`",
                str(len(conv_records)),
                str(sum(1 for record in conv_records if record.role == "user")),
                str(sum(1 for record in conv_records if record.role == "assistant")),
            ]
        )
    write_table(lines, ["No.", "Conversation", "ID", "Nodes", "User", "Assistant"], conv_rows)

    lines.append("## Concept Index")
    lines.append("")
    lines.append("This index counts messages that mention each concept at least once and lists the first source references. It is intentionally broad so small but important recurring ideas are not hidden inside summaries.")
    lines.append("")
    concept_rows = []
    for term in sorted(CONCEPT_TERMS, key=lambda term: (-len(concept_index[term]), term.lower())):
        refs = concept_index[term]
        if not refs:
            continue
        convs = sorted({record.conv_index for record in refs})
        first_refs = ", ".join(record.ref for record in refs[:25])
        if len(refs) > 25:
            first_refs += f", +{len(refs) - 25} more"
        concept_rows.append([f"`{term}`", str(len(refs)), ", ".join(f"C{idx:02d}" for idx in convs), first_refs])
    write_table(lines, ["Concept", "Messages", "Conversations", "First References"], concept_rows)

    def marker_section(title: str, markers: list[str], max_lines_per_conv: int | None = None) -> None:
        lines.append(f"## {title}")
        lines.append("")
        total = 0
        for conv in conversations:
            conv_records = records_by_conv[int(conv["index"])]
            hits: list[tuple[MessageRecord, list[str]]] = []
            for record in conv_records:
                snippets = find_lines(record.text, markers)
                if snippets:
                    hits.append((record, snippets))
            if not hits:
                continue
            lines.append(f"### C{int(conv['index']):02d}. {inline(str(conv['title']), 120)}")
            lines.append("")
            emitted = 0
            for record, snippets in hits:
                for snippet in snippets:
                    lines.append(f"- `{record.ref}` {record.role} {record.create_time}: {snippet}")
                    total += 1
                    emitted += 1
                    if max_lines_per_conv is not None and emitted >= max_lines_per_conv:
                        remaining = sum(len(s) for _, s in hits) - emitted
                        if remaining > 0:
                            lines.append(f"- Additional markers in this chat are present in the source ledger: {remaining}.")
                        break
                if max_lines_per_conv is not None and emitted >= max_lines_per_conv:
                    break
            lines.append("")
        lines.append(f"Marker entries emitted: {total}.")
        lines.append("")

    marker_section("Decision And Canon Marker Index", DECISION_MARKERS)
    marker_section("Unresolved And Risk Marker Index", UNRESOLVED_MARKERS)
    marker_section("Artifact And Interface Index", ARTIFACT_MARKERS)

    lines.append("## Aspect Chapters")
    lines.append("")
    for aspect_number, aspect in enumerate(ASPECTS, start=1):
        terms = aspect["terms"]
        lines.append(f"### Aspect {aspect_number}. {aspect['title']}")
        lines.append("")
        lines.append(aspect["explain"])
        lines.append("")
        matched = [record for record in records if concept_matches(record.text, terms)]
        conv_counts = Counter(record.conv_index for record in matched)
        lines.append(f"- Source messages: {len(matched)}")
        lines.append(f"- Source conversations: {len(conv_counts)}")
        if conv_counts:
            top = ", ".join(f"C{idx:02d} ({count})" for idx, count in conv_counts.most_common(12))
            lines.append(f"- Most active conversations: {top}")
        lines.append("")
        lines.append("#### Detailed Source Evidence")
        lines.append("")
        for record in matched[:500]:
            snippet = snippet_for_terms(record.text, terms)
            lines.append(f"- `{record.ref}` C{record.conv_index:02d} {record.role} {record.create_time}: {snippet}")
        if len(matched) > 500:
            lines.append(f"- Additional source messages for this aspect: {len(matched) - 500}. See the conversation source chapters for the complete node ledger.")
        lines.append("")

    lines.append("## Conversation Source Chapters")
    lines.append("")
    lines.append("Each conversation chapter includes every captured message node in source order, plus extracted headings, user-request ledger, decision markers, unresolved markers, artifact/interface markers, and concept counts.")
    lines.append("")

    for conv in conversations:
        conv_index = int(conv["index"])
        conv_records = records_by_conv[conv_index]
        lines.append(f"### C{conv_index:02d}. {inline(str(conv['title']), 140)}")
        lines.append("")
        write_table(
            lines,
            ["Field", "Value"],
            [
                ["Conversation ID", f"`{conv['id']}`"],
                ["Message nodes", str(len(conv_records))],
                ["Active path messages from capture index", str(conv.get("active_path_messages", ""))],
                ["All mapping messages from capture index", str(conv.get("all_mapping_messages", ""))],
                ["Create time", str(conv.get("create_time", ""))],
                ["Update time", str(conv.get("update_time", ""))],
                ["Source raw JSON", f"`capture/raw_json/{Path(conv['raw_json']).name}`"],
                ["Source all-message export", f"`capture/all_message_nodes/{Path(conv['all_message_nodes']).name}`"],
            ],
        )

        lines.append("#### Conversation Concept Counts")
        lines.append("")
        conv_concepts = []
        for term in CONCEPT_TERMS:
            count = sum(1 for record in conv_records if term_in_text(term, record.text))
            if count:
                conv_concepts.append((term, count))
        concept_summary = ", ".join(f"{term} ({count})" for term, count in sorted(conv_concepts, key=lambda item: (-item[1], item[0].lower()))[:40])
        lines.append(concept_summary or "No tracked concept terms found.")
        lines.append("")

        lines.append("#### User Request Ledger")
        lines.append("")
        for record in conv_records:
            if record.role == "user":
                lines.append(f"- `{record.ref}` {record.create_time}: {inline(record.text, 800)}")
        lines.append("")

        headings = []
        for record in conv_records:
            for heading in extract_headings(record.text):
                headings.append((record, heading))
        lines.append("#### Heading And Structure Ledger")
        lines.append("")
        if headings:
            for record, heading in headings[:300]:
                lines.append(f"- `{record.ref}` {heading}")
            if len(headings) > 300:
                lines.append(f"- Additional headings in this chat: {len(headings) - 300}.")
        else:
            lines.append("- No markdown headings extracted.")
        lines.append("")

        for title, markers in [
            ("Decision/Canon Markers", DECISION_MARKERS),
            ("Unresolved/Risk Markers", UNRESOLVED_MARKERS),
            ("Artifacts/Interfaces/Files", ARTIFACT_MARKERS),
        ]:
            lines.append(f"#### {title}")
            lines.append("")
            found_any = False
            for record in conv_records:
                snippets = find_lines(record.text, markers)
                for snippet in snippets:
                    found_any = True
                    lines.append(f"- `{record.ref}` {record.role} {record.create_time}: {snippet}")
            if not found_any:
                lines.append("- None extracted by marker scan.")
            lines.append("")

        lines.append("#### Complete Source Node Ledger")
        lines.append("")
        write_table(
            lines,
            ["Ref", "Role", "Time", "Type", "Children", "Detail"],
            [
                [
                    f"`{record.ref}`",
                    record.role,
                    record.create_time,
                    record.content_type,
                    str(record.children),
                    inline(record.text or "[empty]", 520),
                ]
                for record in conv_records
            ],
        )

    lines.append("## Known Gaps")
    lines.append("")
    lines.append("- `Training LLM with ChatGPT` remains inaccessible/bugged in the capture set.")
    lines.append("- Assistant messages whose API content was represented as non-text/code placeholders may require direct raw JSON inspection if exact code bodies are needed.")
    lines.append("- This book uses redacted and shortened excerpts for safety and navigability; the raw export files remain the full source record.")
    lines.append("- Some concept terms intentionally overmatch so the index errs toward inclusion. Use source references to confirm exact meaning.")
    lines.append("")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "output": str(OUTPUT_PATH),
        "conversations": len(conversations),
        "messages": len(records),
        "bytes": OUTPUT_PATH.stat().st_size,
        "lines": len(lines),
    }


if __name__ == "__main__":
    summary = build_book()
    print(json.dumps(summary, indent=2, sort_keys=True))
