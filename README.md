
# NexusNet v0.5.1a (r22)

**One-stop, local-first NexusNet brain** (FastAPI + Web UI). $0 startup: use tiny local models, optional larger models via scripts.

## Quickstart

### Linux
```bash
git clone <your repo> && cd NexusNet
bash scripts/bootstrap.sh
bash scripts/start_api.sh
# UI: open http://localhost:8000/ui/index.html
```

### Windows (PowerShell)
```powershell
git clone <your repo>; cd NexusNet
.\scripts\bootstrap.ps1
.\scripts\start_api.ps1
# UI: open http://localhost:8000/ui/index.html
```

## Endpoints
- `GET /health`
- `POST /chat`
- `GET /admin/experts`, `POST /admin/toggle`, `GET /admin/config`
- `POST /temporal/ingest`, `POST /temporal/query`
- `POST /qes/telemetry`, `POST /qes/evolve`

## Config
See `runtime/config/*.yaml`:
- `inference.yaml` (backends + QES bridge)
- `experts.yaml` (19 capsules, toggles, teachers)
- `planes.yaml` (11 memory planes + budgeting ratios)
- `router.yaml` (keyword routing)
- `rag.yaml` (Temporal GraphRAG v2)
- `federated.yaml` (baseline secure agg)
- `qes_policy.yaml`

## RAG / Temporal KG
DuckDB-backed store (default). Hybrid retrieval: BM25-like and entailment gate. Endpoints under `/temporal/*`.

## Dreaming / Self-training
RND-R0 loop with critique. Writes assimilation packages in `data/dreams/`.

## Federated (baseline)
Run clients to upload masked vectors; coordinator aggregates to `data/federated/aggregate.json`.

## Safety & $0 startup
- Local-first hardware policy
- No paid APIs by default
- Optional vLLM HTTP client if you run one

## Notes r21 → r22
- Added Temporal GraphRAG v2 API + AIS gate
- Plane-aware routing hooks + memory budgeting
- QES policy → inference bridge
- Multiple chat session memory
- Tightened bootstrap + smoke tests
- Docs updated; CI added


### Docker
```bash
docker compose up --build
# then open http://localhost:8000/ui/index.html
```
