"""Toward the end goal: birth a model on REAL text (not synthetic grammar), at the largest feasible
scale, with real BPE tokenization + minibatch training + real perplexity + generation + a saved born
checkpoint.

Honest boundary: in a CPU sandbox with no network this cannot reach frontier capability (no GPU, no
licensed external teachers, no internet-scale corpus). What it CAN do - and does here - is a *real*
language-modeling birth: real English corpus, real subword tokenizer, real minibatch SGD until
perplexity genuinely drops and generation is coherent-ish. The path to a capable model is the same
pipeline run at scale on the GPU box with real teachers; this proves the pipeline on real data.
"""
from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from .lm import NexusNetLM
from .bpe_tokenizer import BPETokenizer
from .absorption import absorb_wrapper

_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_MD = re.compile(r"[`#>*|_\[\](){}]")
_WS = re.compile(r"\s+")


def build_real_corpus(roots: list[str] | None = None, *, max_chars: int = 600_000,
                      pattern: str = "*.md") -> str:
    """Ingest REAL English prose from local docs, lightly cleaned (strip code fences + md noise)."""
    roots = roots or ["docs"]
    chunks: list[str] = []
    total = 0
    for root in roots:
        for p in sorted(Path(root).rglob(pattern)):
            if "__pycache__" in p.parts:
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            t = _CODE_FENCE.sub(" ", t)
            t = _MD.sub(" ", t)
            t = _WS.sub(" ", t).strip()
            if len(t) < 200:
                continue
            chunks.append(t)
            total += len(t)
            if total >= max_chars:
                break
        if total >= max_chars:
            break
    return (" ".join(chunks))[:max_chars]


def make_token_windows(ids: list[int], *, seq_len: int, step: int, device: str = "cpu"):
    inputs, targets = [], []
    for s in range(0, len(ids) - seq_len - 1, step):
        w = ids[s:s + seq_len + 1]
        inputs.append(w[:-1])
        targets.append(w[1:])
    x = torch.tensor(inputs, dtype=torch.long, device=device)
    y = torch.tensor(targets, dtype=torch.long, device=device)
    return x, y


def run_real_birth(
    *,
    out_dir: str,
    max_chars: int = 600_000,
    vocab_size: int = 2048,
    seq_len: int = 64,
    d_model: int = 128,
    n_heads: int = 4,
    n_kv_heads: int = 2,
    num_experts: int = 6,
    top_k: int = 2,
    num_layers: int = 4,
    steps: int = 1500,
    batch_size: int = 24,
    lr: float = 3e-3,
    val_fraction: float = 0.1,
    device: str | None = None,
    seed: int = 0,
    log_every: int = 100,
    full_features: bool = True,
) -> dict[str, Any]:
    """Real language-modeling birth on real text. Returns metrics + a generated sample + checkpoint path."""
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    torch.manual_seed(seed)
    t0 = time.time()

    corpus = build_real_corpus(max_chars=max_chars)
    tok = BPETokenizer().train(corpus, vocab_size=vocab_size)
    ids = tok.encode(corpus)
    x, y = make_token_windows(ids, seq_len=seq_len, step=seq_len // 2, device=str(dev))

    n = x.shape[0]
    n_val = max(1, int(n * val_fraction))
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(n, generator=g)
    val_idx, tr_idx = perm[:n_val], perm[n_val:]
    x_tr, y_tr, x_val, y_val = x[tr_idx], y[tr_idx], x[val_idx], y[val_idx]

    model = NexusNetLM(vocab_size=tok.vocab_size, d_model=d_model, n_heads=n_heads,
                       n_kv_heads=n_kv_heads, num_experts=num_experts, top_k=top_k,
                       d_hidden=2 * d_model, num_layers=num_layers,
                       full_features=full_features).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    @torch.no_grad()
    def _val_loss() -> float:
        model.eval()
        bs = min(64, x_val.shape[0])
        logits = model(x_val[:bs])
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y_val[:bs].reshape(-1)).item()
        model.train()
        return loss

    model.train()
    history: list[float] = []
    initial_val = _val_loss()
    for step in range(steps):
        idx = torch.randint(0, x_tr.shape[0], (batch_size,), generator=g)
        xb, yb = x_tr[idx], y_tr[idx]
        opt.zero_grad()
        logits = model(xb)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), yb.reshape(-1))
        loss.backward()
        opt.step()
        if (step + 1) % 50 == 0:
            model.update_load_bias()
        if (step + 1) % log_every == 0:
            history.append(loss.item())

    final_val = _val_loss()
    # real generation from a seed
    seed_ids = tok.encode("the system")[:8] or [1]
    gen_ids = model.generate(seed_ids, max_new_tokens=40, greedy=False, temperature=0.8, context=seq_len)
    sample = tok.decode(gen_ids)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ckpt = out / "real_birth.pt"
    torch.save(model.state_dict(), ckpt)
    tok.save(str(out / "bpe.json"))
    manifest = {
        "artifact": "real-data-birthed-nexusnet-lm",
        "corpus_chars": len(corpus), "tokens": len(ids), "vocab_size": tok.vocab_size,
        "windows": int(n), "params": model.num_parameters(),
        "config": {"d_model": d_model, "num_layers": num_layers, "num_experts": num_experts,
                   "seq_len": seq_len, "steps": steps, "batch_size": batch_size,
                   "full_features": full_features},
        "wrapper_absorption": absorb_wrapper(model),
        "initial_val_loss": initial_val, "final_val_loss": final_val,
        "initial_perplexity": math.exp(min(20, initial_val)),
        "final_perplexity": math.exp(min(20, final_val)),
        "learned": final_val < initial_val,
        "sample_generation": sample,
        "device": str(dev), "seconds": round(time.time() - t0, 1),
        "checkpoint": str(ckpt),
        "claim_boundary": "real-data-real-training-small-cpu-scale-not-frontier-capability",
    }
    (out / "real_birth.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
