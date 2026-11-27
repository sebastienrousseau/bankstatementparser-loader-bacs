# Examples for bankstatementparser-loader-bacs

Runnable scripts, each with an inline Standard 18 sample, so no data
files are needed. CI runs every one (`tests/test_regression_examples.py`
and the `Examples` job).

- `01_basic_usage.py`: `load_bacs` and `summarize_bacs` on a file with a
  UHL1 header, a credit and two Direct Debits.
- `02_advanced_workflow.py`: the core's `BacsStatementParser` plugin
  reading a file from disk as a DataFrame and a summary, with the totals
  reconciled against `load_bacs_file`.

```sh
python examples/01_basic_usage.py
```
