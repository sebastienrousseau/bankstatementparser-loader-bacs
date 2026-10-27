# Changelog

All notable changes to `bankstatementparser-loader-bacs` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
