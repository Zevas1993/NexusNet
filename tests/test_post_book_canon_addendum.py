from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "docs" / "NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"
LEDGER = ROOT / "docs" / "NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md"


def test_hierarchical_hive_moe_articulation_is_canonized_with_nexusnet_corrections():
    addendum = ADDENDUM.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")

    required_phrases = [
        "PB-2026-05-04-091",
        "Corrected Hierarchical Hive MoE Articulation",
        "hive-wide connected substrate",
        "mandatory sanitized federated learning",
        "Recursive Neural Dreaming as a universal protocol",
        "sandbox/eval/governance/checkpoint",
        "child-retention",
        "parent-retirement",
        "runtime substrate ledgers",
        "backend/quantization evidence",
        "licensing-safe teacher source rule",
        "open-source, open-weight, or otherwise distillation-approved",
        "DeepSeek",
        "no anti-distillation",
    ]

    for phrase in required_phrases:
        assert phrase in addendum

    assert "PB-2026-05-04-091" in ledger
    assert "license-approved/open-weight/permissive-only teacher sources" in ledger

