
# RAG Backends

- **Lite (default)**: BM25 in-memory, no services, zero-cost.
- **Postgres + pgvector (optional)**: enable by installing `requirements-pg.txt` and pointing `DATABASE_URL`.
- **Graph backends (coming)**: Graphiti / Neo4j adapters will be optional installs.
