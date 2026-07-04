"""Wave-3: distillation bridge (torch), RL lane (GRPO + R-Zero), domain corpora, eval gates, infra."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetTransformer,
    NexusNetLM,
    make_sequence_dataset,
    train_model,
    kd_loss_torch,
    FrozenTeacher,
    train_with_distillation,
    train_grpo,
    r_zero_self_play,
    grpo_step,
    build_domain_corpus,
    domain_corpus_for_capsule,
    all_domain_corpora,
    measure_language_model,
    evaluate_capsule_gates,
    make_corpus_windows,
    split_windows,
    save_training_state,
    load_training_state,
    fit_lm,
)


def _clf(seed=0, **kw):
    torch.manual_seed(seed)
    cfg = dict(vocab_size=24, num_classes=3, d_model=48, n_heads=4, n_kv_heads=2,
               num_experts=6, top_k=2, d_hidden=96, max_steps=2, ebt_steps=1)
    cfg.update(kw)
    return NexusNetTransformer(**cfg)


# --- distillation bridge (real torch KD in the graph) ---

def test_kd_loss_is_differentiable_and_well_formed():
    s = torch.randn(8, 4, requires_grad=True)
    t = torch.randn(8, 4)
    y = torch.randint(0, 4, (8,))
    terms = kd_loss_torch(s, t, y, alpha=0.5, temperature=2.0)
    assert terms["loss"].requires_grad and float(terms["kd"]) >= 0.0
    terms["loss"].backward()
    assert s.grad.abs().sum() > 0


def test_frozen_teacher_has_no_grad_and_student_distills():
    X, y = make_sequence_dataset(n=300, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    teacher_model = _clf(seed=1)
    train_model(teacher_model, X, y, epochs=40, lr=3e-3)          # a competent-ish teacher
    teacher = FrozenTeacher(teacher_model)
    assert all(not p.requires_grad for p in teacher.parameters())
    student = _clf(seed=2)
    res = train_with_distillation(student, teacher, X, y, epochs=50, lr=3e-3)
    assert res["gradients_flowed"] is True
    assert res["final_loss"] < res["initial_loss"]
    assert "student_matches_teacher" in res


# --- RL lane: GRPO + R-Zero self-play (real policy gradients) ---

def test_grpo_improves_reward():
    X, y = make_sequence_dataset(n=200, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    model = _clf(seed=0)
    res = train_grpo(model, X, y, steps=40, lr=3e-3, group_size=8, seed=0)
    assert res["reward_improved"] is True
    assert res["final_reward"] > res["initial_reward"]


def test_grpo_step_updates_weights():
    X, y = make_sequence_dataset(n=64, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    model = _clf(seed=0)
    before = [p.detach().clone() for p in model.parameters()]
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    grpo_step(model, X, y, opt, group_size=6, generator=torch.Generator().manual_seed(0))
    changed = any(not torch.equal(b, p) for b, p in zip(before, model.parameters()))
    assert changed


def test_r_zero_self_play_runs_and_challenges_hard_items():
    X, y = make_sequence_dataset(n=200, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    model = _clf(seed=0)
    res = r_zero_self_play(model, X, y, rounds=4, steps_per_round=8, seed=0)
    assert len(res["round_rewards"]) == 4
    assert len(res["challenge_entropy"]) == 4
    assert "solver_improved" in res


# --- per-expert domain corpora ---

def test_domain_corpora_are_distinct_per_expert():
    vision = domain_corpus_for_capsule("vision", n_sentences=80, seed=0)
    assert "the " in vision and len(vision) > 0
    corpora = all_domain_corpora(n_sentences=30, seed=0)
    assert len(corpora) >= 60                                   # one per capsule (>=60 capsules)
    # different domains -> different corpora
    keys = list(corpora)
    assert corpora[keys[0]] != corpora[keys[1]]


def test_domain_corpus_uses_domain_vocabulary():
    corpus = build_domain_corpus("astrophysics cosmology stellar dynamics",
                                 ["star_formation", "galaxy_rotation"], n_sentences=60, seed=0)
    assert any(w in corpus for w in ("astrophysics", "cosmology", "stellar", "galaxy"))


# --- eval gates bound to a real held-out measurement ---

def test_eval_gates_measure_held_out_and_report_basis():
    corpus = domain_corpus_for_capsule("philosopher", n_sentences=200, seed=0)
    x, y = make_corpus_windows(corpus, seq_len=24)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.3, seed=0)
    torch.manual_seed(0)
    lm = NexusNetLM(d_model=64, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=128, num_layers=2)
    from nexusnet.hive.net import train_language_model
    train_language_model(lm, x_tr, y_tr, epochs=60, val_x=x_val, val_y=y_val)
    report = evaluate_capsule_gates("philosopher", lm, x_val, y_val,
                                    accuracy_threshold=0.0, perplexity_threshold=1e9)
    assert report["gates_total"] >= 1
    assert all(g["measurement_basis"] == "held_out_proxy" for g in report["gates"])
    assert report["all_gates_passed"] is True                   # trivial thresholds -> all pass
    m = measure_language_model(lm, x_val, y_val)
    assert m["val_loss"] > 0 and m["val_perplexity"] > 1.0


# --- scaled-training infra: resumable optimizer state ---

def test_fit_lm_checkpoint_resume(tmp_path):
    corpus = domain_corpus_for_capsule("physicist", n_sentences=120, seed=0)
    x, y = make_corpus_windows(corpus, seq_len=16)
    torch.manual_seed(0)
    lm = NexusNetLM(d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2)
    ckpt = str(tmp_path / "state.pt")
    r1 = fit_lm(lm, x, y, steps=20, lr=3e-3, device="cpu", checkpoint_path=ckpt)
    assert r1["final_step"] == 20 and r1["gradients_flowed"] is True
    # resume: a fresh model + optimizer continues from step 20
    torch.manual_seed(1)
    lm2 = NexusNetLM(d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                     d_hidden=96, num_layers=2)
    opt = torch.optim.Adam(lm2.parameters(), lr=3e-3)
    state = load_training_state(lm2, opt, path=ckpt)
    assert state["step"] == 20
    r2 = fit_lm(lm2, x, y, steps=10, lr=3e-3, device="cpu", resume_from=ckpt)
    assert r2["start_step"] == 20 and r2["final_step"] == 30 and r2["resumed"] is True
