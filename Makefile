PY=python

.PHONY: dev start test lint format

dev:
	$(PY) -m solitaire.main

start: dev

test:
	pytest -q

lint:
	ruff check . || true

format:
	black .
	ruff check . --fix

