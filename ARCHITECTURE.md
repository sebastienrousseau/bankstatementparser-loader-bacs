<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# bankstatementparser-loader-bacs Architecture

A map of the codebase for new contributors and maintainers: how a
Standard 18 file becomes `Transaction` objects, and where to change
what.

## The pipeline

```text
Standard 18 payload (str, iterable of lines, or file)
        |  _parse_bacs_stream: one pass over the lines
        |    UHL1           -> _handle_uhl1_header (date, service user number)
        |    VOL1/HDR1/...  -> skipped
        |    detail record  -> _handle_detail_18 (one dict per payment)
        v
_BacsState (header fields + list of record dicts)
        |
        +--> load_bacs       -> list[Transaction] (source="bacs")
        +--> summarize_bacs  -> BacsSummary (counts and totals, no Transaction)
```

`load_bacs_file` reads a path as UTF-8 (undecodable bytes replaced) and
calls `load_bacs`. `BacsStatementParser`, the plugin the core finds
through the `bacs` and `std18` entry points, wraps the same functions
for the core's `parse()` (a pandas DataFrame), `to_transactions()` and
`get_summary()` (cached after the first read).

## Modules

| Area | Module | Responsibility |
| :--- | :--- | :--- |
| **Loader** | `bankstatementparser_loader_bacs/loader.py` | Line dispatch, field helpers, amount and date decoding, `load_bacs` / `load_bacs_file` / `summarize_bacs`, `BacsSummary`, `BacsStatementParser` |
| **Package entry** | `bankstatementparser_loader_bacs/__init__.py` | Re-exports the public API and defines `__version__` (single source of truth) |
| **Tests** | `tests/` | 100% line + branch coverage: unit and Hypothesis tests (`test_loader.py`), characterisation of `_handle_detail_18`, the golden fixture, non-ASCII digits, the documented column layout (`test_docs_accuracy.py`), examples, release notes and the shared suite conformance gate |
| **Fuzzing** | `fuzz/fuzz_load_bacs.py`, `fuzz/corpus/` | Atheris target for `load_bacs` and `summarize_bacs`, run by the CI `Fuzz` job |
| **Benchmarks** | `benches/bench_load_bacs.py` | Load and summary cost as a file grows; `--quick` runs in CI |
| **Examples** | `examples/` | Two runnable scripts: loading and summarising, and the parser plugin |
| **Manual** | `mkdocs.yml`, `docs/` | The MkDocs Material user manual and API reference, deployed to GitHub Pages |
| **Scripts** | `scripts/` | `verify_versions.py`, `release_notes.py`, `export_locked_requirements.py`, `check_complexity.py`, `check_suite_consistency.py`, `readme-check.sh` |

## How a detail record becomes a transaction

1. A line of at least 30 characters whose first six are digits is a
   detail record; shorter lines and unknown labels are skipped.
2. `_handle_detail_18` slices the fixed columns (destination sort code
   and account 1-14, transaction code 16-17, originating sort code and
   account 18-31, amount 36-46, names and reference 47-100, processing
   date 101-106). A field past the end of a short line takes a default:
   the code `99`, the originator already seen, a zero amount, the
   `UHL1` date.
3. The amount keeps only the ASCII digits of its field, in pence, and
   is negated for the debit codes `01`, `17`, `18` and `19`.
4. `load_bacs` turns each record dict into a `Transaction`, numbering
   them with `source_index`.

## Key design decisions

- **Decimal everywhere.** Pence are divided by `Decimal(100)`; `float`
  appears only in the DataFrame and summary dict the core's interface
  asks for.
- **Lenient input.** CRLF, blank lines, short lines and unparsable
  dates or amounts never raise; numeric fields count ASCII digits only,
  so a stray character cannot become a number.
- **One pass.** Both entry points share `_parse_bacs_stream`; the
  summary never builds `Transaction` objects.
- **Coverage enforced at 100%** line + branch and docstring, and every
  function within the suite's complexity ceilings.

## Extension points

- **A new label:** add it to the dispatch in `_parse_bacs_stream`.
- **The sign convention:** `_DEBIT_CODES`; update the README table and
  the tests with it.
- **A summary field:** extend `BacsSummary`, `summarize_bacs` and
  `BacsSummaryRecord`.
