from typing import Dict, Any, List
from core.config import config
from .query_transform import QueryTransforms
from .retriever import Retriever
from .indexer import Indexer
from .verify_ais import AISVerifier
from .temporal import parse_scope

class SelfRAGAgent:
    def __init__(self):
        self.cfg = config()
        qt_cfg = self.cfg['rag']['query_transform']
        self.qt = QueryTransforms(n_rewrites=qt_cfg['n_rewrites'], enable_hyde=qt_cfg['enable_hyde'], max_embeddings=qt_cfg['budget_max_embeddings'])
        self.retriever = Retriever(embed_model=self.cfg['models']['embedder'])
        self.indexer = Indexer(self.retriever)
        self.ais = AISVerifier(model_name=self.cfg['models']['ais_nli'])
    async def answer(self, q: str) -> Dict[str, Any]:
        state = {"coverage": 0.0, "evidence": [], "evidence_count": 0}
        scope = parse_scope(q, default_lookback_days=self.cfg.get('temporal',{}).get('default_lookback_days',365))
        expanded = await self.qt.expand(q); queries = expanded['queries']
        cand = self.retriever.retrieve(queries,
            bm25_k=self.cfg['rag']['retrieval']['stage1']['bm25_k'],
            vector_k=self.cfg['rag']['retrieval']['stage1']['vector_k'],
            rrf_k=self.cfg['rag']['retrieval']['stage1']['rrf_k'],
            topk=self.cfg['rag']['retrieval']['stage2']['topk'],
            scope=scope, recency_lambda=self.cfg.get('temporal',{}).get('recency_lambda',0.15))
        ev = [{"source": d["id"], "snippet": d["text"][:400].replace("\n"," "), "meta": d.get("meta",{})} for d in cand]
        if not ev: return {"answer":"insufficient evidence; no documents indexed.","citations":[]}
        ans = f"{ev[0]['snippet']} [1]" + (f" {ev[1]['snippet']} [2]" if len(ev)>1 else '')
        res = self.ais.check(ans, ev, entail_thresh=0.70)
        if res['coverage'] < 0.80 or not res.get('temporal_ok', True):
            return {"answer":"insufficient evidence; need more time-consistent sources.","citations":ev,"coverage":res['coverage']}
        return {"answer": ans, "citations": ev, "coverage": res['coverage']}