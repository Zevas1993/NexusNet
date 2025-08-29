
#!/usr/bin/env python3
"""Build a ColBERT late-interaction index from the current RAG store.

Usage:
  python scripts/rag/build_colbert_index.py
"""
import os, yaml, sys
from core.rag.storage import Storage

def main():
    cfg_path = "runtime/config/rag.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    colbert_cfg = cfg.get("colbert", {})
    if not colbert_cfg.get("enabled", False):
        print("WARN: rag.yaml -> colbert.enabled is False. Index will still be (re)built on disk.")
    index_dir = colbert_cfg.get("index_dir", "runtime/rag/colbert")
    os.makedirs(index_dir, exist_ok=True)

    try:
        from core.rag.late_interaction.colbert_adapter import ColBERTAdapter
    except Exception as e:
        print("ERROR: ColBERT adapter not available. Ensure file core/rag/late_interaction/colbert_adapter.py exists and its deps are installed.")
        print("Detail:", e)
        sys.exit(2)

    store = Storage(cfg["storage"]["dir"])
    docs = [t for _, t, _ in store.all_docs()]
    if not docs:
        print("No documents in RAG store. Ingest data via /rag/ingest first.")
        sys.exit(1)

    adapter = ColBERTAdapter(index_dir=index_dir)
    # Try several common method names to build the index
    if hasattr(adapter, "build_index"):
        adapter.build_index(docs)
    elif hasattr(adapter, "build"):
        adapter.build(docs)
    else:
        # fallback: if adapter exposes add/corpus+save
        ok = False
        for m in ("add_corpus","add","ingest"):
            if hasattr(adapter, m):
                getattr(adapter, m)(docs)
                ok = True
                break
        if hasattr(adapter, "save"):
            adapter.save()
        if not ok:
            print("ERROR: Could not find a suitable build method on ColBERTAdapter.")
            sys.exit(3)
    print(f"ColBERT index built at: {index_dir}")

if __name__ == "__main__":
    main()
