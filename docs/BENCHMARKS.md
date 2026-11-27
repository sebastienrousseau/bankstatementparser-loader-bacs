# Benchmarks

`benches/bench_load_bacs.py` measures what a Standard 18 file costs to
load as it grows in the one direction a submission grows in practice:
the number of detail records between the `UHL1` header and the
trailers. It times `load_bacs` and, beside it, `summarize_bacs`, which
parses the same records but builds no `Transaction` objects. Records
alternate between a credit (`99`) and a Direct Debit (`17`), each 106
characters with a processing date.

Each figure is the best of 7 runs after one untimed warm-up. Nothing
asserts a threshold: wall-clock is not comparable between machines. CI
runs `python benches/bench_load_bacs.py --quick` on every push so the
benchmark keeps running against the current API.

## Results

Run with `poetry run python benches/bench_load_bacs.py` on 2026-11-27:
Apple M1 Pro, macOS 27.2.1, CPython 3.12.16,
bankstatementparser-loader-bacs 0.0.36, bankstatementparser 0.0.35.

| Records | KiB | `load_bacs` ms | `summarize_bacs` ms | us per record |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 1.4 | 0.05 | 0.04 | 5.30 |
| 100 | 10.8 | 0.49 | 0.34 | 4.91 |
| 1000 | 104.9 | 4.92 | 3.31 | 4.92 |
| 10000 | 1045.3 | 54.47 | 34.08 | 5.45 |
| 50000 | 5225.0 | 308.66 | 178.56 | 6.17 |

The cost per record at 50,000 records is 1.16x the cost at 10, so
loading grows close to linearly with the file: no step rescans the
records already read. `summarize_bacs` costs at most 0.73x `load_bacs`;
the difference is the `Transaction` objects it does not build.

Reproduce with `python benches/bench_load_bacs.py` (add `--json` for
machine-readable output).
