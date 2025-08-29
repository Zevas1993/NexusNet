#!/usr/bin/env bash
source .venv/bin/activate || true
python -m uvicorn app.main:app --port 8000 --host 0.0.0.0
