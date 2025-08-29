#requires -Version 5.0
$ErrorActionPreference = "Stop"
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-windows.txt

# Create tiny model dir
New-Item -ItemType Directory -Force -Path models\tiny | Out-Null
# Example download (commented):
# Invoke-WebRequest -Uri "https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/resolve/main/ggml-model-f16.gguf" -OutFile "models\tiny\tinyllama.gguf"

# Smoke test
.\scripts\smoke.ps1
