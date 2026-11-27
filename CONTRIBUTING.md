# Contributing to bankstatementparser-loader-bacs

Thank you for your interest in contributing to `bankstatementparser-loader-bacs`.

## Code of Conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
Report security issues privately, as [`SECURITY.md`](SECURITY.md)
describes, not in a public issue.

## Development Workflow

1. Fork and clone the repository.
2. Install the dependencies (Python 3.10 or later and Poetry):

   ```bash
   poetry install
   ```

3. Create a branch from `main`:

   ```bash
   git checkout -b feat/my-change
   ```

4. Make the change with its tests, then run every local gate:

   ```bash
   make check
   ```

   That runs `ruff` (lint and format), `mypy --strict`, the complexity
   baseline, `bandit`, `pytest` with the 100% line and branch coverage
   floor, `interrogate` at 100% docstring coverage and the examples.
   The complexity gate holds every function under the per-function
   ceilings (cyclomatic 10, cognitive 15, Halstead 30, 60 lines; 500
   lines per file) against `scripts/complexity_baseline.json`, which
   may only shrink. Record an improvement with
   `python3 scripts/check_complexity.py --update`.

5. If you change `pyproject.toml`'s dependencies, run `poetry lock` and
   regenerate the hashed exports, which CI compares with the lock:

   ```bash
   poetry run python scripts/export_locked_requirements.py --with dev --output requirements/ci.txt
   poetry run python scripts/export_locked_requirements.py --output requirements/runtime.txt
   poetry run python scripts/export_locked_requirements.py --with fuzz --output requirements/fuzz.txt
   poetry run python scripts/export_locked_requirements.py --with docs --output requirements/docs.txt
   ```

6. Sign and commit, then open a pull request against `main`.

## Commit Signing (Required)

Every commit on `main` is signed. Configure Git to sign with an SSH or
GPG key, and add a `Signed-off-by` line with `git commit -s`:

```bash
git config --global commit.gpgsign true
git commit -s -m "fix: describe the change"
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/): a
header of at most 50 characters, then a body saying what changed and
why.

```text
fix: read only ASCII digits in Standard 18 fields
docs: correct the record layout table
```
