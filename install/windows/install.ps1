
$ErrorActionPreference = "Stop"
function Ensure-Winget { if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { Write-Error "winget not found. Install App Installer from Microsoft Store first." } }
function Ensure-App($id, $name) { if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { winget install --id $id -e --source winget --accept-source-agreements --accept-package-agreements } }
function Ensure-Python { if (-not (Get-Command python -ErrorAction SilentlyContinue)) { winget install --id Python.Python.3.11 -e --source winget --accept-source-agreements --accept-package-agreements } }
Ensure-Winget; Ensure-App "Git.Git" "git"; Ensure-Python
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
try { .\.venv\Scripts\pip install faiss-cpu colbert-ai } catch { Write-Warning "ColBERT optional deps failed; late-interaction will be disabled until installed." }
.\.venv\Scripts\python apps\bootstrap\first_run.py
Start-Process -NoNewWindow .\.venv\Scripts\python -ArgumentList " -m uvicorn apps.api.main:app --host 0.0.0.0 --port 5173"
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5173"