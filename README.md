# NexusNet — All-in-One Starter (Agentic + Temporal RAG + ColBERT Late-Interaction)

Includes:
- Agentic Self-RAG + AIS + Temporal Agent
- **ColBERT** late-interaction retriever (installed by default on Linux & Docker; Windows best-effort)
- Installers, Docker, service scripts, smoke test
- No model weights bundled

## Start
Windows (PowerShell):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install\windows\install.ps1
```
Linux:
```bash
chmod +x install/linux/install.sh
./install/linux/install.sh
```
Docker:
```bash
docker compose up --build
```
Open http://127.0.0.1:5173