from __future__ import annotations

from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    ByteTokenizer,
    NexusNetLM,
    make_corpus_windows,
    train_language_model,
    independence_milestones,
    birth_model,
    load_checkpoint,
)

CORPUS = "NexusNet is the brain. The brain learns, adapts, and grows into its own model. " * 12


def test_tokenizer_roundtrips_unicode():
    tok = ByteTokenizer()
    for s in ["hello", "NexusNet — the brain", "éèê café"]:
        assert tok.decode(tok.encode(s)) == s


def test_causal_attention_has_no_future_leakage():
    torch.manual_seed(0)
    lm = NexusNetLM(d_model=48, n_heads=4, n_kv_heads=2, num_experts=2, top_k=1, num_layers=2)
    lm.eval()
    base = torch.tensor([[10, 20, 30, 40, 50]])
    changed = base.clone()
    changed[0, -1] = 99                       # change ONLY the last token
    with torch.no_grad():
        a = lm(base)[0, 1]                     # logits at position 1 (before the change)
        b = lm(changed)[0, 1]
    assert torch.allclose(a, b, atol=1e-5)     # earlier positions cannot see the future


def test_language_model_trains_and_loss_drops():
    torch.manual_seed(0)
    x, y = make_corpus_windows(CORPUS, seq_len=24)
    lm = NexusNetLM(d_model=64, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, num_layers=2)
    m = train_language_model(lm, x, y, epochs=120, lr=3e-3)
    assert m["gradients_flowed"] is True
    assert m["final_loss"] < 0.3 * m["initial_loss"]
    assert m["next_token_accuracy"] > 0.6
    assert m["num_parameters"] > 100_000


def test_birthed_model_generates_learned_text():
    torch.manual_seed(0)
    x, y = make_corpus_windows(CORPUS, seq_len=24)
    # the canonical birth config (96-dim, 3 layers) learns the corpus well enough to reproduce it
    lm = NexusNetLM(d_model=96, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, num_layers=3)
    train_language_model(lm, x, y, epochs=150, lr=3e-3)
    tok = ByteTokenizer()
    out = tok.decode(lm.generate(tok.encode("NexusNet is the brain"), max_new_tokens=30, greedy=True))
    assert out.startswith("NexusNet is the brain")
    continuation = out[len("NexusNet is the brain"):]
    # it produced genuine learned content from the corpus (a full word it was trained on)
    assert any(word in continuation for word in ("brain", "learns", "adapts", "grows"))


def test_independence_milestone_gate_is_real():
    # high native accuracy clearly beating the teacher -> birth ready
    ready = independence_milestones(
        {"next_token_accuracy": 1.0, "initial_loss": 9.0, "final_loss": 0.05}
    )
    assert ready["birth_ready"] is True
    assert ready["dependency_ratio"] == 0.0
    # weak student -> gate BLOCKS the birth
    blocked = independence_milestones(
        {"next_token_accuracy": 0.2, "initial_loss": 9.0, "final_loss": 8.0}
    )
    assert blocked["birth_ready"] is False
    assert blocked["milestone_checks"]["native_generation"]["passed"] is False


def test_birth_pipeline_saves_and_reloads_identical_model(tmp_path: Path):
    res = birth_model(corpus=CORPUS, out_dir=str(tmp_path), seed=0, epochs=40, seq_len=24)
    manifest = res["manifest"]
    assert Path(manifest["checkpoint_path"]).exists()
    assert Path(manifest["manifest_path"]).exists()
    assert "birth_ready" in manifest and "independence_milestones" in manifest

    # the birthed checkpoint reloads to an identical model (same logits on the same input)
    reloaded = load_checkpoint(manifest["checkpoint_path"], config=manifest["config"])
    x, _ = make_corpus_windows(CORPUS, seq_len=24)
    res["model"].eval()
    with torch.no_grad():
        a = res["model"](x[:1])
        b = reloaded(x[:1])
    assert torch.allclose(a, b, atol=1e-5)


def test_initial_loss_is_sane_not_exploding():
    """Init CE must start near ln(vocab) (~5.56), proving healthy weight init (regression guard for the
    tied-embedding std=1.0 bug that made initial loss ~90)."""
    import math
    import torch.nn.functional as F
    torch.manual_seed(0)
    x, y = make_corpus_windows(CORPUS, seq_len=24)
    lm = NexusNetLM(d_model=96, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, num_layers=3)
    with torch.no_grad():
        init = F.cross_entropy(lm(x).reshape(-1, lm.head.out_features), y.reshape(-1)).item()
    ideal = math.log(259)
    assert init < ideal + 2.0          # ~5.56 ideal; must be in the same ballpark, not ~90
    assert lm.embed.weight.std().item() < 0.05    # GPT-style 0.02 init, not the default 1.0


def test_model_generalizes_on_structured_grammar_not_just_memorizes():
    """Held-out (val) accuracy must stay high and val loss must track train loss -> the model learned
    the grammar (generalization), it did not merely memorize the training windows."""
    from nexusnet.hive.net import make_structured_corpus, split_windows
    torch.manual_seed(0)
    corpus = make_structured_corpus(n_sentences=180, seed=0)
    x, y = make_corpus_windows(corpus, seq_len=24)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.2, seed=0)
    assert x_val.size(0) > 20                                   # a real held-out set
    lm = NexusNetLM(d_model=64, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, num_layers=2)
    m = train_language_model(lm, x_tr, y_tr, epochs=100, lr=3e-3, val_x=x_val, val_y=y_val)
    assert m["val_accuracy"] > 0.7                              # generalizes to unseen sentences
    assert m["val_loss"] < 2.0 * m["final_loss"] + 0.3         # val tracks train (not overfit)


def test_birth_uses_held_out_generalization_for_native_generation():
    from nexusnet.hive.net import independence_milestones
    # native_generation must come from VAL accuracy when present, not the (memorizable) train accuracy
    ms = independence_milestones(
        {"next_token_accuracy": 1.0, "val_accuracy": 0.4, "initial_loss": 9.0, "final_loss": 0.1}
    )
    assert ms["native_generation"] == 0.4
    assert ms["birth_ready"] is False                          # weak generalization blocks birth


def test_student_that_outperforms_teacher_is_promotable_without_being_perfect():
    """Canon TRP: promotion requires matching/beating the teacher, NOT reaching perfect accuracy.
    Regression guard for the over-strict dependency=teacher/native formula that demanded ~2x teacher."""
    from nexusnet.hive.net import independence_milestones
    # student clearly beats the teacher (0.85 vs 0.5) but is far from perfect -> still birth-ready
    beats = independence_milestones(
        {"val_accuracy": 0.85, "initial_loss": 9.0, "final_loss": 0.1}, teacher_baseline_accuracy=0.5
    )
    assert beats["outperforms_teacher"] is True
    assert beats["dependency_ratio"] == 0.0          # no longer depends on the teacher
    assert beats["birth_ready"] is True              # promotable WITHOUT being perfect

    # student below the teacher is blocked (must outperform first)
    below = independence_milestones(
        {"val_accuracy": 0.45, "initial_loss": 9.0, "final_loss": 0.1}, teacher_baseline_accuracy=0.5
    )
    assert below["outperforms_teacher"] is False
    assert below["birth_ready"] is False


def test_per_node_teacher_pairing_gates_experts_aos_and_orchestrators():
    """Canon: teacher pairing is per EXPERT, per AO, and per ORCHESTRATOR (plus core). Each node is
    judged against ITS OWN teacher; the system births only when every node beats its own teacher."""
    from nexusnet.hive.net import evaluate_node_promotions
    nodes = [
        {"node_id": "expert.coder", "node_type": "expert",
         "native_generation": 0.91, "teacher_baseline_accuracy": 0.82,
         "teacher_ids": ["qwen3-coder-next", "devstral-2"], "initial_loss": 9, "final_loss": 0.2},
        {"node_id": "expert.vision", "node_type": "expert",
         "native_generation": 0.74, "teacher_baseline_accuracy": 0.80,   # below ITS teacher
         "teacher_ids": ["qwen3-vl"], "initial_loss": 9, "final_loss": 0.5},
        {"node_id": "ao.math", "node_type": "assistant_orchestrator",
         "native_generation": 0.88, "teacher_baseline_accuracy": 0.79,
         "teacher_ids": ["deepseek-r1-distill-qwen-32b"], "initial_loss": 9, "final_loss": 0.3},
        {"node_id": "orchestrator.reasoning", "node_type": "orchestrator",
         "native_generation": 0.86, "teacher_baseline_accuracy": 0.83,
         "teacher_ids": ["mistral-small-4", "deepseek-v4-pro"], "initial_loss": 9, "final_loss": 0.3},
        {"node_id": "core.brain", "node_type": "core",
         "native_generation": 0.90, "teacher_baseline_accuracy": 0.85, "initial_loss": 9, "final_loss": 0.2},
    ]
    r = evaluate_node_promotions(nodes)
    # each node judged vs its OWN teacher baseline
    assert r["nodes"]["expert.coder"]["birth_ready"] is True       # 0.91 > 0.82
    assert r["nodes"]["expert.vision"]["birth_ready"] is False     # 0.74 < 0.80 (below its teacher)
    assert r["nodes"]["ao.math"]["birth_ready"] is True            # AO beats its teacher
    assert r["nodes"]["orchestrator.reasoning"]["birth_ready"] is True
    assert r["nodes"]["core.brain"]["birth_ready"] is True
    # node keeps its own teacher pairing on record
    assert r["nodes"]["expert.coder"]["teacher_ids"] == ["qwen3-coder-next", "devstral-2"]
    # system births only when ALL nodes (experts + AOs + orchestrators + core) beat their own teachers
    assert r["blocked"] == ["expert.vision"]
    assert r["system_birth_ready"] is False
    # by-type accounting covers every node class
    assert r["by_type"]["expert"]["total"] == 2 and r["by_type"]["expert"]["promoted"] == 1
    assert r["by_type"]["assistant_orchestrator"]["promoted"] == 1
    assert r["by_type"]["orchestrator"]["promoted"] == 1
    assert r["by_type"]["core"]["promoted"] == 1
