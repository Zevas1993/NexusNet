
.PHONY: setup run api qes bench test lint docs
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && [ -f requirements.txt ] && pip install -r requirements.txt || true
api:
	python -m apps.api.main
qes:
	python scripts/qes/run_evolution.py --trials 8
test:
	pytest -q || true
lint:
	ruff check . || true
docs:
	mkdocs build || true
