# bankstatementparser-loader-bacs

**BACS Standard 18** is the UK's fixed-width file layout for Bacs
Direct Debit and Direct Credit submissions: labels (`VOL1`, `HDR1`,
`UHL1`, `EOF1`, `UTL1`) around one 100- or 106-character detail record
per payment.

**bankstatementparser-loader-bacs** turns a Standard 18 payload into a
flat list of
[`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser)
`Transaction` objects (`source="bacs"`) that the rest of a
deterministic pipeline can consume unchanged.

| Concern | How this loader handles it |
| :--- | :--- |
| Records | `UHL1` (processing date, service user number) and detail records; the other labels are skipped |
| Sort codes and accounts | Destination at columns 1-14, originating at 18-31; the transaction's `account_id` is `<sort code>-<account>` of the destination |
| Transaction codes | `01`, `17`, `18` and `19` are debits (negative); every other code is a credit; the code is kept as `category` `bacs:<code>` |
| Amounts | 11-digit pence to `Decimal` (never `float`) |
| Dates | `YYDDD` (Julian), `DDMMYY` or `YYMMDD`; a detail record without one takes the `UHL1` date |
| Errors | None raised for malformed text: a line that is not a record is skipped, a field that does not parse falls back |

## In this manual

- [Standard 18 support](format.md): the public API, the record layout,
  the field mapping and the sign convention.
- [The suite](suite.md): the `bankstatementparser` packages.
- [Comparison](COMPARISON.md) and [Benchmarks](BENCHMARKS.md).
- [Supported Python policy](POLICIES.md).
- [API reference](api.md): generated from the docstrings.
- [Changelog](changelog.md) and [Security policy](security.md).

The source, issues and releases live on
[GitHub](https://github.com/sebastienrousseau/bankstatementparser-loader-bacs);
the package is on
[PyPI](https://pypi.org/project/bankstatementparser-loader-bacs/).
