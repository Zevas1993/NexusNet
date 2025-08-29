
# ARCHITECTURE

- **API**: FastAPI `app/` with routers for chat/admin/temporal/qes.
- **Inference**: Selector across `transformers`, `llama.cpp`, `vLLM`, with local-first policy.
- **Experts (19)**: Config-driven toggles; router keyword mapping & trust scaffold.
- **Memory**: 11-plane `MemoryNode` storage, plane-aware token budgeting.
- **RAG**: DuckDB temporal store, BM25-like retrieval + lexical entailment gate.
- **Dreaming**: RND-R0 loop writes assimilation packages.
- **Federated**: Pairwise-mask baseline agg.
- **UI**: Simple chat + admin toggles in `ui/`.
