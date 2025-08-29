import re, networkx as nx
from typing import Dict, Any
from core.rag.temporal import parse_scope
class AgenticGraphRAG:
    def __init__(self, retriever, ais, max_steps=5, coverage_threshold=0.8):
        self.retriever, self.ais = retriever, ais
        self.max_steps, self.cov_thr = max_steps, coverage_threshold
    async def run(self, q: str) -> Dict[str, Any]:
        scope = parse_scope(q)
        g = nx.DiGraph(); g.add_node(q, type='root')
        subqs=[q]
        combined_answer=""; evidence=[]
        for step in range(self.max_steps):
            new_subqs=[]
            for sub in subqs:
                cand = self.retriever.retrieve([sub], scope=scope)
                ev = [{"source": d["id"], "snippet": d["text"][:300], "meta": d.get("meta",{})} for d in cand]
                if not ev: continue
                answer = ev[0]["snippet"] + " [1]"
                check = self.ais.check(answer, ev)
                combined_answer += (" " if combined_answer else "") + answer
                evidence.extend(ev)
                for m in re.findall(r'"([^"]{6,80})"', ev[0]["snippet"]):
                    g.add_edge(sub, m); new_subqs.append(m)
            cov = self.ais.check(combined_answer, evidence).get('coverage',0.0)
            if cov >= self.cov_thr: break
            subqs = list(dict.fromkeys(new_subqs))[:4]
            if not subqs: break
        return {"answer": combined_answer, "citations": evidence, "graph_nodes": list(g.nodes)}
