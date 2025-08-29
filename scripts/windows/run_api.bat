
@echo off
setlocal
if not exist .venv (
  python -m venv .venv
  call .venv\Scripts\activate
  pip install -U pip -r requirements-windows.txt
) else (
  call .venv\Scripts\activate
)
python -m apps.api.main
