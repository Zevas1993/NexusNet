from typing import List, Dict, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from .rankers import rrf_fuse, CrossEncoderReranker
from .temporal import in_scope, recency_boost
from core.config import config
from .late_interaction.colbert_adapter import ColBERTAdapter

class Retriever:
    def __init__(self, embed_model: str = "BAAI/bge-small-en-v1.5"):
        self.cfg = config()
        self.embed = SentenceTransformer(embed_model)
        self.docs: Dict[str, Dict] = {}
        self.doc_texts: List[str] = []
        self.doc_ids: List[str] = []
        self.embeds = None
        self.bm25 = None
        self.reranker = CrossEncoderReranker()
        li = self.cfg.get("late_interaction", {})
        self.colbert = None
        if li.get("enable", False) and li.get("backend","")=="colbert":
            self.colbert = ColBERTAdapter(
                index_dir = li.get("index_dir","runtime/state/colbert_index"),
                model_name = li.get("model","colbert-ir/colbertv2.0"),
                doc_maxlen = li.get("doc_maxlen",180),
                nbits = li.get("nbits",2),
                kmeans_niters = li.get("kmeans_niters",4),
                nprobe = li.get("nprobe",64),
            )

    def _rebuild(self):
        self.doc_texts = [d["text"] for d in self.docs.values()]
        self.doc_ids = list(self.docs.keys())
        if self.doc_texts:
            self.embeds = self.embed.encode(self.doc_texts, normalize_embeddings=True, show_progress_bar=False)
            tokenized = [t.split() for t in self.doc_texts]
            self.bm25 = BM25Okapi(tokenized)
            if self.colbert and self.colbert.ok:
                col_docs = [{"id": did, "text": self.docs[did]["text"]} for did in self.doc_ids]
                try: self.colbert.build_index(col_docs)
                except Exception: pass

    def add_documents(self, docs: List[Dict]):
        for d in docs:
            meta = {k: d.get(k) for k in ("valid_from","valid_to","observed_at")}
            self.docs[d["id"]] = {"id": d["id"], "text": d["text"], "meta": meta}
        self._rebuild()

    def _vec_search(self, q: str, k: int = 30) -> List[Tuple[str, float]]:
        if self.embeds is None: return []
        qv = self.embed.encode([q], normalize_embeddings=True)[0]
        sims = np.dot(self.embeds, qv); idx = np.argsort(-sims)[:k]
        return [(self.doc_ids[i], float(sims[i])) for i in idx]

    def _bm25_search(self, q: str, k: int = 30) -> List[Tuple[str, float]]:
        if not self.bm25: return []
        scores = self.bm25.get_scores(q.split()); idx = np.argsort(-scores)[:k]
        return [(self.doc_ids[i], float(scores[i])) for i in idx]

    def _colbert_search(self, q: str, k: int = 50) -> List[Tuple[str, float]]:
        if not self.colbert or not self.colbert.ok: return []
        return self.colbert.search(q, k=k)

    def retrieve(self, queries: List[str], bm25_k=30, vector_k=30, rrf_k=60, topk=8, scope=None, recency_lambda=0.15):
        runs = []
        for q in queries:
            runs.append(self._vec_search(q, vector_k))
            runs.append(self._bm25_search(q, bm25_k))
            cb = self._colbert_search(q, k=max(vector_k, bm25_k))
            if cb: runs.append(cb)
        fused = rrf_fuse(runs, k=rrf_k)
        cand = []
        for did, s in fused:
            meta = self.docs.get(did, {}).get("meta", {})
            if scope and not in_scope(meta, scope): continue
            prior = recency_boost(meta, scope, lam=recency_lambda if scope else 0.0)
            txt = self.docs.get(did, {}).get("text","")
            if not txt: continue
            cand.append({"id": did, "text": txt, "score": s * prior, "meta": meta})
        return self.reranker.rerank(queries[0], cand, topk=topk)