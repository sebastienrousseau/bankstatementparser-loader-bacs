# Contributing to bankstatementparser-loader-bacs

Thank you for your interest in contributing to `bankstatementparser-loader-bacs`!

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all contributors.

## Development Workflow
1. Fork and clone the repository.
2. Install dependencies:
   ```bash
   poetry install --all-extras
   poetry run pre-commit install
   ```
3. Ensure all tests and quality gates pass:
   ```bash
   poetry run pytest
   poetry run ruff check .
   poetry run ruff format --check .
   poetry run mypy .
   poetry run interrogate -v
   python3 scripts/check_complexity.py
   ```
   The complexity gate holds every function under the per-function
   ceilings (cyclomatic 10, cognitive 15, Halstead 30, 60 lines; 500
   lines per file) against `scripts/complexity_baseline.json`, which
   may only shrink. Record an improvement with
   `python3 scripts/check_complexity.py --update`.
4. Submit a Pull Request targeting `main`.
