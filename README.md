# NexusNet — Unified Full (All Except Models)

**Full stack**: Non-linear HiveMind with 19 experts • Hybrid RAG (dense + BM25 + ColBERT + RRF + Cross-Encoder + AIS + Temporal) • Dual-path CPU/GPU consensus • TeacherGate (OpenRouter/Requesty) • Hardware scan & autotune • Assimilation→DPO trainer • Federated learning (SECAGG-like) • Connectors • Self-update sandbox • Admin UI • Installers & Docker.  

> Models & large indexes are **not** included; they pull/build on demand.

## Quick start
Windows (native):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install\windows\install.ps1
```
Windows via WSL (preferred for ColBERT):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install\windows\install_wsl.ps1
```
Linux:
```bash
chmod +x install/linux/install.sh && ./install/linux/install.sh
```
Docker:
```bash
docker compose up --build
```
Open **http://127.0.0.1:5173** (chat) and **/admin**.

## First-run
1. **/admin → Keys**: set any API keys you'll use (OpenRouter/Requesty).
2. **/admin → Apply Autotune**: tunes threads/ctx/8-bit/vLLM/ColBERT based on your hardware.
3. Optional: pull models now:
```bash
python scripts/models/download.py --only all
```
4. Index data by POSTing docs to `/rag/index` or using connectors then indexing.

## Repo layout
- `apps/` — FastAPI app (`/chat`, `/rag/*`, `/admin/*`)
- `core/` — orchestrator, experts, RAG, models, safety, ops, FL, update, HW
- `connectors/` — fs, web, git, notion, gdrive, slack
- `runtime/config/` — edit **experts.yaml**, **hivemind.yaml**, **rag.yaml**, **assimilation.yaml**, **training_criteria.yaml**
- `runtime/state/` — audit, indexes, shards (gitignored)
- `scripts/models/` — model map & downloader
- `install/`, `docker/` — installers & container build

## Admin endpoints
- `/admin/experts`, `/admin/models` (get/post), `/admin/hivemind` (get/post)
- `/admin/hardware`, `/admin/fl`, `/admin/keys` (get/post), `/admin/apply_autotune`

## Notes
- **Windows + ColBERT**: prefer WSL/Docker for easier compilation
- **GPU memory**: automatically reduces batch size if CUDA OOM
- **CPU consensus**: falls back when GPU unavailable
- **Federated**: simulates multiple "agents" training on local shards
- **Assimilation**: transforms raw docs → structured training pairs → DPO
- **TeacherGate**: routes between OpenRouter vs. Requesty based on cost/latency
- **HiveMind**: each expert votes, final answer uses weighted consensus

---
*NexusNet is a research framework. Not for production without proper security review.*