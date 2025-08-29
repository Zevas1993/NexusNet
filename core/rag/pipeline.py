
from __future__ import annotations
from typing import Dict, Any, List
import yaml
from .retriever import Retriever
from .rerank_pairwise import pairwise_rerank
from nexusnet.temporal.retriever import TemporalRetriever
from .rerank import Reranker
from .verify_ais import AISVerifier

class RAGPipeline:
    def __init__(self, cfg_path: str = "runtime/config/rag.yaml"):
        with open(cfg_path,"r",encoding="utf-8") as f: self.cfg = yaml.safe_load(f)
        self.retriever = Retriever(self.cfg)
        self.reranker = None; self.verifier = None
        # Temporal retriever (optional)
        self.temporal = None
        tp = self.cfg.get('temporal', {})
        if tp.get('enabled', False):
            try:
                self.temporal = TemporalRetriever(db_path=tp.get('db_path','runtime/temporal/tkg.sqlite'))
            except Exception:
                self.temporal = None

        self.colbert = None
        cb = self.cfg.get("colbert",{})
        if cb.get("enabled", False):
            try:
                from .late_interaction.colbert_adapter import ColBERTAdapter
                self.colbert = ColBERTAdapter(cb.get("index_dir","runtime/rag/colbert"))
            except Exception:
                self.colbert = None
    
        if self.cfg.get("use_cross_encoder", True):
            try: self.reranker = Reranker(self.cfg["cross_encoder"])
            except Exception: self.reranker = None
        if self.cfg.get("use_ais_verify", True):
            try: self.verifier = AISVerifier(self.cfg["ais_nli_model"])
            except Exception: self.verifier = None

    def ingest(self, texts: List[str]): return self.retriever.ingest(texts, ts=None)

    def retrieve(self, query: str, k: int | None = None) -> list[str]:
        k = k or self.cfg.get("top_k", 8)
        ids = [i for i,_ in self.retriever.search(query, top_k=k)]
        chunks = self.retriever.fetch(ids)
        # ColBERT (optional)
        if self.colbert:
            try:
                chunks = self.colbert.rerank(query, chunks, top_k=k)
            except Exception:
                pass
        # Temporal (optional): enrich with as-of facts
        if self.temporal:
            try:
                tp = self.cfg.get('temporal', {})
                as_of = tp.get('as_of','auto')
                if as_of == 'auto':
                    import datetime as _dt
                    as_of = _dt.date.today().isoformat()
                facts = self.temporal.retrieve_as_of(query, as_of, limit=max(5, k or 10))
                fact_txts = [f"TKG: {f['subject']} {f['predicate']} {f['object']} (start={f['start']}, end={f['end']}, src={f['source']}, conf={f['confidence']:.2f})" for f in facts]
                # extend chunks as soft evidence
                chunks = (chunks or []) + fact_txts
            except Exception:
                pass
        if self.reranker:
            pair_scores = self.reranker.rerank(query, chunks, top_k=k)
            chunks = [chunks[i] for i,_s in pair_scores]
        if self.verifier:
            mask, _ = self.verifier.entailed_mask(query, chunks, threshold=0.5)
            chunks = [c for c,m in zip(chunks, mask) if m]
        pr = self.cfg.get('pairwise_rerank',{}).get('enabled', False)
        if pr and chunks:
            chunks = pairwise_rerank(query, chunks)
        return chunks

    def augment(self, query: str) -> str:
        ctx = self.retrieve(query)
        if not ctx: return query
        ctx_block = "\n\n".join(f"[CTX {i+1}] {c}" for i,c in enumerate(ctx))
        return f"Use the following context to answer accurately.\n\n{ctx_block}\n\nUser: {query}\nAnswer:"
