from __future__ import annotations
import pathlib
from typing import List, Dict, Tuple

class ColBERTAdapter:
    def __init__(self, index_dir: str, model_name: str = "colbert-ir/colbertv2.0",
                 doc_maxlen: int = 180, nbits: int = 2, kmeans_niters: int = 4, nprobe: int = 64):
        self.index_dir = pathlib.Path(index_dir)
        self.index_name = self.index_dir.name
        self.model_name = model_name
        self.doc_maxlen = doc_maxlen
        self.nbits = nbits
        self.kmeans_niters = kmeans_niters
        self.nprobe = nprobe
        self.ok = False
        try:
            from colbert import Indexer, Searcher, ColBERTConfig
            from colbert.infra import Run
            self.Indexer = Indexer; self.Searcher = Searcher; self.ColBERTConfig = ColBERTConfig; self.Run = Run
            self.ok = True
        except Exception as e:
            self.err = f"colbert-ai not available: {e}"
            self.ok = False

    def build_index(self, docs: List[Dict[str, str]]):
        if not self.ok:
            raise RuntimeError(getattr(self, "err", "colbert-ai not installed"))
        self.index_dir.mkdir(parents=True, exist_ok=True)
        collection_path = self.index_dir / "collection.tsv"
        with open(collection_path, "w", encoding="utf-8") as f:
            for d in docs:
                did = d["id"].replace("\t"," ").replace("\n"," ")
                txt = d["text"].replace("\t"," ").replace("\n"," ")
                f.write(f"{did}\t{txt}\n")
        cfg = self.ColBERTConfig(
            root=str(self.index_dir.parent),
            doc_maxlen=self.doc_maxlen,
            nbits=self.nbits,
            kmeans_niters=self.kmeans_niters
        )
        with self.Run().context():
            self.Indexer(cfg).index(
                name=self.index_name,
                collection=str(collection_path),
                overwrite=True,
                checkpoint=self.model_name
            )
        self.searcher = self.Searcher(index=str(self.index_dir))
        try: self.searcher.configure(nprobe=self.nprobe)
        except Exception: pass

    def search(self, query: str, k: int = 50) -> List[Tuple[str, float]]:
        if not self.ok: return []
        if not hasattr(self, "searcher"):
            try:
                self.searcher = self.Searcher(index=str(self.index_dir))
            except Exception:
                return []
        try:
            ranking = self.searcher.search(query, k=k)
            out = []
            for pid, score in zip(ranking["docid"], ranking["score"]):
                out.append((str(pid), float(score)))
            return out
        except Exception:
            return []