#!/usr/bin/env bash
set -e
source .venv/bin/activate || true
python -m uvicorn app.main:app --port 8001 --host 0.0.0.0 &
PID=$!
sleep 3
curl -fsS http://127.0.0.1:8001/health
curl -fsS -X POST http://127.0.0.1:8001/chat -H "Content-Type: application/json" \
  -d '{"session_id":"smoke","messages":[{"role":"user","content":"ping"}]}' | jq .reply || true
kill $PID || true
echo "Smoke OK"
