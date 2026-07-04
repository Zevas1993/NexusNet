"""Wave-4: a real byte-level BPE subword tokenizer (upgrade from the placeholder ByteTokenizer).

Trains merges from a corpus by greedily merging the most frequent adjacent pair (Sennrich et al.;
GPT-2 byte-level BPE). Byte-level start => no out-of-vocab ever; lossless round-trip. Deterministic.
This is the tokenizer a birthed model would carry.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


class BPETokenizer:
    """Byte-level Byte-Pair-Encoding tokenizer with train / encode / decode / save / load."""

    def __init__(self) -> None:
        # base vocab: 256 byte tokens; merges map (a, b) -> new_id in learned order
        self.merges: dict[tuple[int, int], int] = {}
        self.vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    @staticmethod
    def _pairs(ids: list[int]) -> Counter:
        return Counter(zip(ids, ids[1:]))

    @staticmethod
    def _merge(ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
        out: list[int] = []
        i = 0
        while i < len(ids):
            if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
                out.append(new_id)
                i += 2
            else:
                out.append(ids[i])
                i += 1
        return out

    def train(self, text: str, *, vocab_size: int = 512) -> "BPETokenizer":
        """Learn merges until the vocab reaches `vocab_size` (>= 256)."""
        if vocab_size < 256:
            raise ValueError("vocab_size must be >= 256 (byte base vocab)")
        ids = list(text.encode("utf-8"))
        num_merges = vocab_size - 256
        for m in range(num_merges):
            pairs = self._pairs(ids)
            if not pairs:
                break
            best = max(pairs, key=lambda p: (pairs[p], -p[0], -p[1]))  # freq, tie-break deterministic
            if pairs[best] < 2:
                break
            new_id = 256 + m
            ids = self._merge(ids, best, new_id)
            self.merges[best] = new_id
            self.vocab[new_id] = self.vocab[best[0]] + self.vocab[best[1]]
        return self

    def encode(self, text: str) -> list[int]:
        ids = list(text.encode("utf-8"))
        # apply merges in the order they were learned (lowest new_id first)
        for pair, new_id in sorted(self.merges.items(), key=lambda kv: kv[1]):
            ids = self._merge(ids, pair, new_id)
        return ids

    def decode(self, ids: list[int]) -> str:
        data = b"".join(self.vocab[i] for i in ids)
        return data.decode("utf-8", errors="replace")

    def save(self, path: str) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {"merges": [[a, b, nid] for (a, b), nid in self.merges.items()]}
        p.write_text(json.dumps(payload), encoding="utf-8")
        return str(p)

    @classmethod
    def load(cls, path: str) -> "BPETokenizer":
        tok = cls()
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        for a, b, nid in sorted(payload["merges"], key=lambda r: r[2]):
            tok.merges[(a, b)] = nid
            tok.vocab[nid] = tok.vocab[a] + tok.vocab[b]
        return tok
