# Comparison

Where bankstatementparser-loader-bacs fits for a Python user with a
BACS Standard 18 file. Nothing here is a measured ranking.

| Project | Reads Standard 18 | Output | Direct Debit sign | Writes Standard 18 |
| :--- | :--- | :--- | :--- | :--- |
| **bankstatementparser-loader-bacs** | Detail records (100 or 106 characters) and the `UHL1` header | `bankstatementparser` `Transaction` objects, a `BacsSummary`, or a DataFrame through the core's plugin interface | Negative for codes `01`, `17`, `18`, `19` | No |
| [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) 0.0.35 | No: its parsers are CAMT, pain.001, CSV, OFX/QFX, MT940, MT942, BAI2 and PDF | `Transaction` objects | Not applicable | No |
| Slicing the columns by hand | Whatever the code reads | Your own structure | Your own code | Your own code |

Evidence: `bankstatementparser/parsers/` in the core (no Standard 18
parser), and `bankstatementparser_loader_bacs/loader.py` here. On
2026-11-27 the PyPI names `bacs`, `pybacs`, `bacs-parser` and
`python-bacs` were checked for another Standard 18 reader: only `bacs`
exists, and it is an unrelated bundle-adjustment library for camera
systems.

## When each fits

- **bankstatementparser-loader-bacs**: you want Standard 18 payments as
  signed `Transaction` objects next to statements from other formats.
- **Slicing by hand**: you need fields this loader does not keep (the
  account type, the free-format field) or the `UTL1` totals checked,
  and you will maintain the column map yourself.

The wider family is listed in [The suite](suite.md).
