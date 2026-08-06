# ============================================================
# Makefile — NEAT Flappy Bird
# Usage:
#   make run        → launch the pygame visualizer
#   make headless   → run headless training (500 generations)
#   make test       → run pytest suite
#   make check      → lint + format check + type check + tests
# ============================================================

.PHONY: run headless test check fmt install

# ---------- Running ----------

run:
	python main.py

headless:
	python main.py --headless --generations 500

# ---------- Testing ----------

test:
	pytest tests/ -v

# ---------- Quality ----------

check: fmt-check lint typecheck test

fmt:
	black .

fmt-check:
	black --check .

lint:
	ruff check .

typecheck:
	mypy neat/ game/

# ---------- Install ----------

install:
	pip install -e ".[dev]"
	pre-commit install
