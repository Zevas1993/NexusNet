"""End-goal push: birth a real language model on REAL text (not synthetic grammar)."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import build_real_corpus, make_token_windows, run_real_birth
from nexusnet.hive.net import BPETokenizer


def test_real_corpus_is_real_english_prose():
    corpus = build_real_corpus(max_chars=20000)
    assert len(corpus) > 5000
    # real English from the docs, with markdown/code stripped
    assert "```" not in corpus
    assert sum(corpus.lower().count(w) for w in (" the ", " and ", " is ", " of ")) > 20


def test_token_windows_shape():
    ids = list(range(500))                            # plenty of tokens for windowing
    x, y = make_token_windows(ids, seq_len=16, step=8)
    assert x.shape[0] > 0 and x.shape[1] == 16 and y.shape == x.shape
    assert (y[:, :-1] == x[:, 1:]).all()              # next-token alignment


def test_real_birth_learns_real_text(tmp_path):
    m = run_real_birth(out_dir=str(tmp_path / "rb"), max_chars=30000, vocab_size=512,
                       seq_len=32, d_model=64, num_layers=2, steps=150, batch_size=16,
                       log_every=50, seed=0)
    # real training on real data measurably reduces perplexity
    assert m["learned"] is True
    assert m["final_perplexity"] < m["initial_perplexity"]
    assert m["final_perplexity"] < m["initial_perplexity"] * 0.6
    assert m["params"] > 0 and m["tokens"] > 1000
    assert isinstance(m["sample_generation"], str) and len(m["sample_generation"]) > 0
    # the born artifact + tokenizer were saved (a real reloadable model)
    import os
    assert os.path.exists(m["checkpoint"])
    assert os.path.exists(str(tmp_path / "rb" / "bpe.json"))


def test_born_real_model_reloads_and_generates(tmp_path):
    m = run_real_birth(out_dir=str(tmp_path / "rb2"), max_chars=20000, vocab_size=384,
                       seq_len=24, d_model=48, num_layers=2, steps=80, batch_size=12, seed=1)
    from nexusnet.hive.net import NexusNetLM
    tok = BPETokenizer.load(str(tmp_path / "rb2" / "bpe.json"))
    # the born model is full-feature (carries all wrapper native features) -> reload must match
    model = NexusNetLM(vocab_size=tok.vocab_size, d_model=48, n_heads=4, n_kv_heads=2,
                       num_experts=6, top_k=2, d_hidden=96, num_layers=2, full_features=True)
    model.load_state_dict(torch.load(m["checkpoint"], map_location="cpu"))
    out = model.generate(tok.encode("the")[:4] or [1], max_new_tokens=12, greedy=True)
    assert tok.decode(out)                              # the reloaded born model generates text


def test_real_birth_model_absorbs_full_wrapper_features(tmp_path):
    # the born model must have ALL the wrapper's native features (canon: absorb the wrapper)
    m = run_real_birth(out_dir=str(tmp_path / "rb3"), max_chars=15000, vocab_size=320,
                       seq_len=20, d_model=48, num_layers=2, steps=60, batch_size=12, seed=0)
    absorb = m["wrapper_absorption"]
    assert absorb["wrapper_fully_absorbed"] is True
    assert absorb["native_parity"] == 1.0
    assert absorb["native_features_missing"] == []
    assert absorb["supersedes_wrapper"] is True
