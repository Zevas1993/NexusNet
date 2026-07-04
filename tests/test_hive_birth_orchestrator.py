"""Depth D1: rich domain corpora + real end-to-end hive birth orchestrator (composes the lanes)."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    build_rich_domain_corpus, build_domain_corpus, domain_corpus_for_capsule,
    birth_expert_node, birth_hive,
)


# --- richer corpus genuinely has multiple sentence forms ---

def test_rich_corpus_has_multiple_grammatical_forms():
    corpus = build_rich_domain_corpus("astrophysics stellar dynamics cosmology",
                                      ["star_formation"], n_sentences=120, seed=0)
    # the four forms leave distinct lexical signatures
    assert " is a " in corpus                       # definitional
    assert any(rel in corpus for rel in ("depends on", "contrasts with", "derives from"))  # relational
    assert "to " in corpus and " then " in corpus   # procedural
    assert "when the " in corpus                     # causal
    assert any(w in corpus for w in ("astrophysics", "stellar", "cosmology"))  # domain vocab


def test_rich_corpus_is_more_complex_than_flat_template():
    rich = build_rich_domain_corpus("physics energy mass", n_sentences=100, seed=0)
    flat = build_domain_corpus("physics energy mass", n_sentences=100, seed=0)
    # richer grammar -> more distinct sentence structures (more unique sentence prefixes)
    rich_prefixes = {s.strip()[:6] for s in rich.split(".") if s.strip()}
    flat_prefixes = {s.strip()[:6] for s in flat.split(".") if s.strip()}
    assert len(rich_prefixes) > len(flat_prefixes)
    assert domain_corpus_for_capsule("physicist", n_sentences=20, seed=0, rich=True) != \
        domain_corpus_for_capsule("physicist", n_sentences=20, seed=0, rich=False)


# --- single expert node births end-to-end, composing every lane ---

def test_birth_expert_node_composes_all_lanes_and_learns():
    node = birth_expert_node("philosopher", epochs=50, seq_len=20, n_sentences=180, seed=0,
                             teacher_baseline_accuracy=0.3, dream_warmup=True)
    # real training happened
    assert node["metrics"]["final_loss"] < node["metrics"]["initial_loss"]
    assert node["metrics"]["gradients_flowed"] is True
    # dream warmup actually ran a JEPA world-model that learned
    assert node["dream_warmup"]["world_model_learned"] is True
    assert node["dream_warmup"]["final_pred_err"] < node["dream_warmup"]["initial_pred_err"]
    # eval gates measured on held-out
    assert node["eval_gates"]["gates_total"] >= 1
    # milestone record is wired for TRP
    assert node["node_record"]["node_type"] == "expert"
    assert "native_generation" in node["node_record"]


def test_birth_expert_node_with_governed_routing():
    node = birth_expert_node("coder", epochs=30, seq_len=20, n_sentences=150, seed=1,
                             govern_allowed=[0, 1, 2, 3], dream_warmup=False)
    assert node["metrics"]["final_loss"] < node["metrics"]["initial_loss"]
    assert node["dream_warmup"] is None


# --- hive-level birth across a roster + TRP promotion ---

def test_birth_hive_runs_roster_and_decides_promotions():
    roster = ["philosopher", "physicist", "mathematician"]
    report = birth_hive(roster, epochs=35, seq_len=18, n_sentences=140, seed=0,
                        teacher_baselines={"philosopher": 0.2, "physicist": 0.2, "mathematician": 0.2},
                        dream_warmup=True)
    assert report["roster"] == roster
    assert set(report["experts"]) == set(roster)
    assert report["all_experts_learned"] is True            # every expert reduced its loss
    assert report["dream_warmups_converged"] >= 1
    # the hive-level TRP promotion ran over all expert nodes
    assert "system_birth_ready" in report
    assert set(report["promotions"]["nodes"]) == {f"expert.{k}" for k in roster}
    assert report["promotions"]["by_type"]["expert"]["total"] == 3


def test_birth_hive_blocks_promotion_when_teacher_baseline_unbeatable():
    # impossibly high teacher baseline -> no expert can surpass it -> not birth-ready
    report = birth_hive(["philosopher", "physicist"], epochs=20, seq_len=16, n_sentences=120, seed=0,
                        teacher_baselines={"philosopher": 0.999, "physicist": 0.999},
                        dream_warmup=False)
    assert report["system_birth_ready"] is False
    assert len(report["promotions"]["blocked"]) == 2
