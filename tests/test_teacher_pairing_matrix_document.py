from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md"
ADDENDUM = ROOT / "docs" / "NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"
LEDGER = ROOT / "docs" / "NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md"


def test_teacher_pairing_matrix_covers_o_ao_and_expert_layers():
    text = DOC.read_text(encoding="utf-8")

    required_sections = [
        "# NexusNet Teacher Pairing Matrix - 2026-05-04",
        "## Pairing Grammar",
        "## O-Level Teacher Pairings",
        "## AO-Level Teacher Pairings",
        "## Expert-Level Teacher Pairings",
        "## Promotion And Retirement Rules",
    ]

    for section in required_sections:
        assert section in text

    for o_name in [
        "Root NexusBrain O",
        "Governance O",
        "Execution O",
        "Research O",
        "Runtime O",
        "Dream Evolution O",
        "Federation O",
    ]:
        assert o_name in text

    for ao_name in [
        "PlanningAO",
        "GovernanceAO",
        "CodingAO",
        "RuntimeAO",
        "EvalsAO",
        "MemoryAO",
        "DreamAO",
        "FederationAO",
        "SelfTrainingAO",
    ]:
        assert ao_name in text

    for expert_name in [
        "Coder Expert",
        "Strategist Expert",
        "Analyst Expert",
        "Researcher Expert",
        "Critique Expert",
        "Conversationalist Expert",
        "Toolsmith Expert",
        "Security Expert",
        "Memory Weaver Expert",
        "Meta Reasoner Expert",
        "Router Expert",
        "Linguist Expert",
        "Vision Expert",
        "Audio Expert",
        "Simulation Expert",
        "Builder Expert",
        "Instructor Expert",
        "Intent Mapper Expert",
        "Critic Historian Expert",
    ]:
        assert expert_name in text

    for phrase in [
        "open-source, open-weight, or otherwise distillation-approved",
        "dual-teacher contrast",
        "Critique Expert",
        "LFM2",
        "temporary child",
        "archive-not-delete",
    ]:
        assert phrase in text


def test_teacher_pairing_matrix_is_added_to_post_book_canon():
    addendum = ADDENDUM.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")

    required_phrases = [
        "PB-2026-05-04-092",
        "Subsystem Teacher Pairing Matrix",
        "O-level teacher pairings",
        "AO-level teacher pairings",
        "expert-level teacher pairings",
        "docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md",
    ]

    for phrase in required_phrases:
        assert phrase in addendum
        assert phrase in ledger


def test_teacher_pairing_matrix_records_current_model_refresh_and_blocked_placeholders():
    text = DOC.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")

    required_phrases = [
        "PB-2026-05-04-093",
        "Teacher Roster Current-Model Refresh",
        "Kimi K2.6",
        "DeepSeek-V4-Pro",
        "DeepSeek-V4-Flash",
        "Mistral Medium 3.5",
        "Devstral Small 2",
        "NexusNet-Intent-BERT-v0",
        "NexusNet-Historian-v0",
        "Code LLaMA-Secure is blocked",
        "Magistral Small 1.2 is deprecated",
        "DeepSeek-V2-Lite is fallback-only",
        "LFM2 remains a license-gated efficiency coach",
    ]

    for phrase in required_phrases:
        assert phrase in text

    for phrase in [
        "PB-2026-05-04-093",
        "Teacher Roster Current-Model Refresh",
        "docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md",
    ]:
        assert phrase in addendum
        assert phrase in ledger

    forbidden_active_rows = [
        "| Research O | Qwen3-30B-A3B | Kimi K2.5",
        "| ResearchAO | Research O | Qwen3-30B-A3B | Kimi K2.5",
        "| Researcher Expert | Qwen3-30B-A3B | Kimi K2.5",
        "Magistral Small 1.2 |",
        "| Code LLaMA-Secure |",
        "| Intent-BERT |",
        "| LLaMA-Historian-tuned |",
    ]
    for phrase in forbidden_active_rows:
        assert phrase not in text
