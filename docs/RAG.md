
# RAG (Temporal GraphRAG v2)

- `POST /temporal/ingest` → store docs with timestamps & domain.
- `POST /temporal/query` → hybrid retrieval (BM25-like + entailment).
- Temporal KG edges auto-created (sentence adjacency).

**SchemaForge:** minimal schema autogen per domain (implicit in DuckDB tables).
**AIS Verifier:** lexical entailment gate `_entailment_gate` to reduce mismatch.
