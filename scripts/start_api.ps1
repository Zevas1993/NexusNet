$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --port 8000 --host 0.0.0.0
