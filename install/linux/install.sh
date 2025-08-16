#!/usr/bin/env bash
set -euo pipefail
command -v python3 >/dev/null || { echo "Install python3 first." >&2; exit 1; }
command -v git >/dev/null || { echo "Install git first." >&2; exit 1; }
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python apps/bootstrap/first_run.py
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 5173