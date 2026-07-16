# ==========================================
# Lucy Makefile
# ==========================================

PYTHON ?= python3
VENV := env
BIN := $(VENV)/bin

.PHONY: help
help:
	@echo
	@echo "Lucy Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv          Create virtual environment"
	@echo "  make install       Install package in editable mode"
	@echo "  make dev           Full development setup"
	@echo ""
	@echo "Development:"
	@echo "  make run           Run Lucy"
	@echo "  make clean         Remove caches"
	@echo "  make freeze        Generate requirements.txt"
	@echo ""
	@echo "Quality:"
	@echo "  make fmt           Format code (black)"
	@echo "  make lint          Run ruff"
	@echo "  make test          Run pytest"
	@echo ""
	@echo "Release:"
	@echo "  make build         Build package"
	@echo "  make check         Validate package"
	@echo "  make publish-test  Upload to TestPyPI"
	@echo "  make publish       Upload to PyPI"
	@echo ""

# -----------------------------------------------------

venv:
	$(PYTHON) -m venv $(VENV)

install:
	$(BIN)/pip install -U pip build twine
	$(BIN)/pip install -e .

dev: venv install

run:
	$(BIN)/lucy

freeze:
	$(BIN)/pip freeze > requirements.txt

clean:
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# -----------------------------------------------------
# Optional (if installed)

fmt:
	$(BIN)/black .

lint:
	$(BIN)/ruff check .

test:
	$(BIN)/pytest

# -----------------------------------------------------

build:
	$(BIN)/python -m build

check:
	$(BIN)/twine check dist/*

publish-test:
	$(BIN)/twine upload --repository testpypi dist/*

publish:
	$(BIN)/twine upload dist/*