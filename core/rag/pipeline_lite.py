
from __future__ import annotations
import os, glob
from .lite import LiteRAG

def load_docs(corpus_dir: str) -> list[str]:
    docs = []
    for p in glob.glob(os.path.join(corpus_dir, "**", "*.txt"), recursive=True):
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                docs.append(f.read())
        except Exception:
            pass
    return docs

def augment_prompt(prompt: str, corpus_dir: str, k: int = 3) -> str:
    docs = load_docs(corpus_dir)
    if not docs:
        return prompt
    rag = LiteRAG(docs)
    hits = rag.search(prompt, k=k)
    ctx = "\n\n".join(hits)
    return f"[CONTEXT]\n{ctx}\n\n[QUERY]\n{prompt}"
