
from __future__ import annotations
import os, duckdb, json, time, pathlib, pickle
from typing import List, Tuple
import numpy as np, faiss

class Storage:
    def __init__(self, root: str):
        self.root = root; os.makedirs(self.root, exist_ok=True)
        self.db_path = os.path.join(self.root, "index.duckdb")
        self.faiss_path = os.path.join(self.root, "faiss.index")
        self.bm25_path = os.path.join(self.root, "bm25.pkl")
        self.dim_path = os.path.join(self.root, "dim.json")
        self._init_db()

    def _init_db(self):
        con = duckdb.connect(self.db_path)
        con.execute("""CREATE TABLE IF NOT EXISTS docs(id BIGINT PRIMARY KEY, text TEXT, ts BIGINT);""")
        con.close()

    def _next_id(self) -> int:
        con = duckdb.connect(self.db_path)
        res = con.execute("SELECT COALESCE(MAX(id),0) FROM docs").fetchone()[0]; con.close()
        return int(res)+1

    def add_docs(self, texts: List[str], timestamps: List[int]) -> List[int]:
        ids=[]; con = duckdb.connect(self.db_path)
        for t, ts in zip(texts, timestamps):
            i = self._next_id(); con.execute("INSERT INTO docs (id,text,ts) VALUES (?,?,?)",[i,t,int(ts)]); ids.append(i)
        con.close(); return ids

    def all_docs(self) -> List[Tuple[int,str,int]]:
        con = duckdb.connect(self.db_path)
        rows = con.execute("SELECT id,text,ts FROM docs ORDER BY id").fetchall(); con.close()
        return rows

    def save_faiss(self, index, dim: int):
        faiss.write_index(index, self.faiss_path)
        with open(self.dim_path,"w",encoding="utf-8") as f: json.dump({"dim": dim}, f)

    def load_faiss(self):
        if not os.path.exists(self.faiss_path) or not os.path.exists(self.dim_path): return None, None
        with open(self.dim_path,"r",encoding="utf-8") as f: dim = json.load(f)["dim"]
        index = faiss.read_index(self.faiss_path); return index, dim

    def save_bm25(self, obj):
        with open(self.bm25_path,"wb") as f: pickle.dump(obj, f)

    def load_bm25(self):
        if not os.path.exists(self.bm25_path): return None
        with open(self.bm25_path,"rb") as f: return pickle.load(f)
