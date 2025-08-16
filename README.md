# NexusNet — Unified Full (All Except Models)

This archive contains the **complete NexusNet framework** (no model weights):
- Non-linear **HiveMind** with **19 experts**
- **Hybrid RAG**: dense + BM25 + **ColBERT** + RRF + CrossEncoder rerank + AIS verify + Temporal
- **Agentic GraphRAG** controller (planner/executor)
- **Dual-path** CPU(GGUF)/GPU(Transformers) backends with **consensus**
- **TeacherGate** (OpenRouter + Requesty)
- **Hardware scan & autotune** (llama.cpp, Transformers, vLLM, ColBERT)
- **Federated Learning** with secure aggregation (pairwise masks) + DP accounting
- **Assimilation** → readiness gate → notify → DPO trainer
- **Connectors**: filesystem, web crawl, Git, Notion, Google Drive, Slack
- **Self-update sandbox** with ed25519 signature + hash check
- **Admin UI** for keys, model maps, hardware profile, FL, assimilation, RAG inspector

> Heavy assets (models, indexes) download/build on first use via scripts and HF.

## Quick start
Windows (native):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install\windows\install.ps1
```
Windows via WSL (recommended):
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

Open http://127.0.0.1:5173 (chat) and http://127.0.0.1:5173/admin (admin).