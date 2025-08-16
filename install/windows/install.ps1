$ErrorActionPreference = "Stop"
function Ensure-Python { if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Host "Installing Python..."; winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements } }
Ensure-Python; python -m venv .venv; .\.venv\Scripts\pip install --upgrade pip; .\.venv\Scripts\pip install -r requirements.txt
try { .\.venv\Scripts\pip install faiss-cpu colbert-ai } catch { Write-Warning "ColBERT deps failed" }
.\.venv\Scripts\python apps\bootstrap\first_run.py; Start-Process .\.venv\Scripts\python -ArgumentList "-m uvicorn apps.api.main:app --host 0.0.0.0 --port 5173"; Start-Sleep 3; Start-Process "http://127.0.0.1:5173"