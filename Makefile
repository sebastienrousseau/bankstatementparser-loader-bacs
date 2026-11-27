.PHONY: help install dev test lint format fuzz bench docs demo type-check security audit clean examples doc-coverage complexity check

PYTHON ?= python3
POETRY ?= poetry
PKG := bankstatementparser_loader_bacs

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(POETRY) install --only main

dev: ## Install all dependencies (including dev)
	$(POETRY) install

test: ## Run tests with the 100% line+branch coverage gate (from pyproject.toml)
	$(POETRY) run pytest tests/ -v

lint: ## Run ruff lint and format checks
	$(POETRY) run ruff check .
	$(POETRY) run ruff format --check .

format: ## Auto-format code (ruff fix + ruff format)
	$(POETRY) run ruff check --fix .
	$(POETRY) run ruff format .

type-check: ## Run mypy --strict on the package and tests
	$(POETRY) run mypy $(PKG) tests

security: ## Run bandit on the package
	$(POETRY) run bandit -r $(PKG) -c pyproject.toml

audit: ## pip-audit every locked requirement set
	for f in runtime ci docs fuzz build sbom; do \
		$(POETRY) run pip-audit --require-hashes --disable-pip -r requirements/$$f.txt || exit 1; \
	done

fuzz: ## Fuzz the BACS loader with Atheris for 60s (Linux x86_64, Python 3.12+)
	$(POETRY) install --with fuzz
	mkdir -p .fuzz-corpus
	$(POETRY) run python fuzz/fuzz_load_bacs.py .fuzz-corpus fuzz/corpus tests/fixtures -max_total_time=60

bench: ## Run the load benchmark (docs/BENCHMARKS.md)
	$(POETRY) run python benches/bench_load_bacs.py

examples: ## Verify example scripts run
	for f in examples/*.py; do $(POETRY) run python $$f || exit 1; done

doc-coverage: ## Enforce the 100% docstring coverage gate
	$(POETRY) run interrogate -c pyproject.toml $(PKG)

demo: ## Render the README demo GIF with VHS
	vhs .github/demo.tape

docs: ## Build the user manual (mkdocs --strict) into site/
	$(POETRY) install --with docs
	NO_MKDOCS_2_WARNING=1 $(POETRY) run mkdocs build --strict

# Per-function ceilings (cyclomatic 10, cognitive 15, Halstead 30,
# 60 lines; 500 lines per file) against scripts/complexity_baseline.json,
# which may only shrink. Record an improvement with
# `python3 scripts/check_complexity.py --update`.
complexity: ## Enforce the complexity baseline
	$(PYTHON) scripts/check_complexity.py

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .eggs/ site/ .fuzz-corpus/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/
	rm -rf coverage.xml .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

check: lint type-check complexity security test doc-coverage examples ## Run all local gates
