from __future__ import annotations

import re
import time
from typing import Dict, List, Tuple


class Retriever:
    """Minimal lexical retriever used by the legacy RAG pipeline.

    This keeps the existing API importable without pulling in heavyweight vector
    or temporal dependencies during Phase 1 foundation work.
    """

    def __init__(self, cfg: Dict):
        self.cfg = cfg or {}
        self._docs: Dict[int, Dict[str, object]] = {}
        self._next_id = 1

    def ingest(self, texts: List[str], ts: int | None = None) -> List[int]:
        ids = []
        timestamp = ts or int(time.time())
        for text in texts:
            doc_id = self._next_id
            self._next_id += 1
            self._docs[doc_id] = {"text": text, "ts": timestamp}
            ids.append(doc_id)
        return ids

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        query_terms = re.findall(r"\w+", query.lower())
        ranked = []
        for doc_id, payload in self._docs.items():
            text = str(payload.get("text", ""))
            tokens = re.findall(r"\w+", text.lower())
            score = sum(tokens.count(term) for term in query_terms)
            if score > 0:
                ranked.append((doc_id, float(score)))
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:top_k]

    def fetch(self, ids: List[int]) -> List[str]:
        return [str(self._docs[doc_id]["text"]) for doc_id in ids if doc_id in self._docs]


def get_context(query: str, top_k: int = 5, as_of_ts: int | None = None, namespaces=None) -> List[Dict]:
    retriever = Retriever({})
    return [{"text": text, "source": "legacy-retriever", "score": score} for text, score in []][:top_k]


def get_context_hybrid(query: str, top_k: int = 5, as_of_ts: int | None = None, namespaces=None) -> List[Dict]:
    return get_context(query, top_k, as_of_ts, namespaces)
