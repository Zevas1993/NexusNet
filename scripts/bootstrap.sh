#!/usr/bin/env bash
set -e
python3 -m venv .venv || true
source .venv/bin/activate
pip install --upgrade pip

# Base requirements (no paid APIs)
pip install -r requirements.txt

# Tiny models (local, $0 startup)
mkdir -p models/tiny
# Example: TinyLlama via transformers will auto-download on first use.
# For llama.cpp, provide a sample link commented; user can replace if needed.
# wget https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/resolve/main/ggml-model-f16.gguf -O models/tiny/tinyllama.gguf || true

# Smoke test
bash scripts/smoke.sh
