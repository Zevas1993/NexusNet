
from __future__ import annotations
from rank_bm25 import BM25Okapi

def tokenize(text: str):
    return [t for t in text.lower().split() if t.strip()]

class BM25Store:
    def __init__(self, corpus):
        self.corpus = [tokenize(c) for c in corpus]
        self.bm25 = BM25Okapi(self.corpus)
    def search(self, query: str, k: int = 10):
        toks = tokenize(query)
        scores = self.bm25.get_scores(toks)
        idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(i, scores[i]) for i in idx]
