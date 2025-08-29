
Write-Host "NexusNet Windows bootstrap"
python -m venv .venv
.\.venv\Scripts\pip install -U pip
if (Test-Path requirements-windows.txt) { .\.venv\Scripts\pip install -r requirements-windows.txt }
Write-Host "Done."
