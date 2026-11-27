# Changelog

All notable changes to `bankstatementparser-loader-bacs` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.35] - 2026-11-26

The first release on PyPI. Versions 0.0.20 to 0.0.34 were never
released: the package joins the bankstatementparser suite, which ships
one version across every package, at 0.0.35.

### Added

- `.github/workflows/release.yml`: a `v*` tag builds the sdist and
  wheel, publishes them to PyPI by trusted publishing, attaches them to
  a GitHub release and writes its notes with `scripts/release_notes.py`
  from the highlights in `.github/releases/<tag>.md`.
- `.github/workflows/pr.yml` (PR Gate) and
  `.github/workflows/suite-consistency.yml`, a daily check that every
  suite package on PyPI agrees on one version
  (`scripts/check_suite_consistency.py`).
- `scripts/verify_versions.py` and the suite's shared
  `tests/test_suite_conformance.py` and `tests/test_release_notes.py`.
- `.github/dependabot.yml`: weekly pip and GitHub Actions updates.
- `scripts/check_complexity.py`, the suite's complexity gate, with
  `scripts/complexity_baseline.json`: per-function ceilings
  (cyclomatic 10, cognitive 15, Halstead 30, 60 lines; 500 lines per
  file), run in CI's lint job. Functions already over a ceiling are
  baselined and may not get worse.
- `.github/workflows/codeql.yml`: CodeQL as an advanced setup for
  Python and GitHub Actions, on pushes and pull requests to `main`
  and weekly.

### Changed

- Requires `bankstatementparser >= 0.0.34` (was `>= 0.0.18`).
- The coverage gate measures branches (`--cov-branch`). Six branches in
  `loader.py` that no test took are now covered; coverage is 100% with
  branches counted.
- Dev dependency floor `pytest >= 9.0.3`, the release that fixes
  PYSEC-2026-1845; `tomli` (Python < 3.11) and `packaging` declared for
  the conformance test.
- GitHub Actions: `actions/checkout` v7, `actions/setup-python` v7.
- `_handle_detail_18` is split into small helpers so every function
  is under the complexity ceilings. Output is unchanged, pinned by
  characterisation tests.

### Fixed

- `get_summary()` returns `BacsSummaryRecord`, a `SummaryRecord` subtype carrying the
  same keys as before (the service user number, sort code and account, submission date, transaction count and credit and debit totals), so the override matches the core parser's
  `SummaryRecord` contract and `mypy` passes against bankstatementparser 0.0.29.

## [0.0.19] - 2026-09-01

### Added

- Initial production release of `bankstatementparser-loader-bacs`: UK BACS Standard 18 / Faster Payments Loader.
- 100% statement and branch test coverage.
- High-concurrency throughput testing (>10,000 TPS) with sub-second response times.
- Strict type hints (`mypy --strict`) and ruff linting.
- Integration with the core `bankstatementparser` ecosystem.
