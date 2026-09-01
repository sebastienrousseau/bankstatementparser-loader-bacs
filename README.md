<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<p align="center">
  <img
    src="https://cloudcdn.pro/bankstatementparser/v1/logos/bankstatementparser.svg"
    alt="bankstatementparser-loader-bacs logo"
    width="120"
    height="120"
  />
</p>

<h1 align="center">bankstatementparser-loader-bacs</h1>

<p align="center">
  <b>UK BACS Standard 18 / Faster Payments 106-byte fixed-width loader plugin for bankstatementparser.</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/bankstatementparser-loader-bacs/"><img src="https://img.shields.io/pypi/v/bankstatementparser-loader-bacs?style=for-the-badge" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/bankstatementparser-loader-bacs/"><img src="https://img.shields.io/pypi/pyversions/bankstatementparser-loader-bacs.svg?style=for-the-badge" alt="Python versions" /></a>
  <a href="https://pypi.org/project/bankstatementparser-loader-bacs/"><img src="https://img.shields.io/pypi/dm/bankstatementparser-loader-bacs.svg?style=for-the-badge" alt="PyPI downloads" /></a>
  <a href="https://github.com/sebastienrousseau/bankstatementparser-loader-bacs/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/bankstatementparser-loader-bacs/ci.yml?branch=main&label=Tests&style=for-the-badge" alt="Tests" /></a>
  <a href="#license"><img src="https://img.shields.io/pypi/l/bankstatementparser-loader-bacs?style=for-the-badge" alt="License" /></a>
</p>

---

## Contents

- [What is bankstatementparser-loader-bacs?](#what-is-bankstatementparser-loader-bacs) — the problem it solves
- [Install](#install) — PyPI, virtualenv
- [Quick start](#quick-start) — parse BACS 18 files in three lines
- [Public API](#public-api) — `load_bacs`, `load_bacs_file`, `summarize_bacs`
- [BACS 18 Record Layout](#bacs-18-record-layout) — 106-byte column mapping
- [Transaction Codes](#transaction-codes) — credit, debit, and direct debit codes
- [Development](#development) — quality gates, tests
- [Ecosystem](#ecosystem) — modular package suite
- [Contributing](#contributing)
- [License](#license)

---

## What is bankstatementparser-loader-bacs?

**BACS Standard 18** is the UK banking standard 106-character fixed-width transmission format for direct debits, direct credits, and Faster Payments processing.

**bankstatementparser-loader-bacs** parses BACS Standard 18 streams and files into unified `bankstatementparser` `Transaction` objects and `pandas.DataFrame` structures.

| Concern | How this loader handles it |
| :--- | :--- |
| **Record Models** | Parses Header (VOL1/HDR1), User Header (UHL1), Standard 18 Data Records (106 bytes), and EOF trailers |
| **Sort Code & Account** | Extracts 6-digit origin/destination sort codes (`XX-XX-XX`) and 8-digit account numbers |
| **Transaction Codes** | Decodes BACS codes (`99`, `01`, `17`, `18`, `19`, `Z4`, etc.) and determines credit vs debit |
| **Amounts** | Converts 11-character minor units (pence) to exact `Decimal` (never `float`) |

---

## Install

| Channel | Command | Notes |
| :--- | :--- | :--- |
| PyPI | `pip install bankstatementparser-loader-bacs` | Pulls in `bankstatementparser >= 0.0.19` |
| Source | `git clone https://github.com/sebastienrousseau/bankstatementparser-loader-bacs && cd bankstatementparser-loader-bacs && poetry install` | For local development |

Requires Python 3.10 or later. Compatible with macOS, Linux, and Windows.

<details>
<summary>Using an isolated virtual environment (recommended)</summary>

```sh
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
python -m pip install -U bankstatementparser-loader-bacs
```

</details>

---


## Quick start

```python
from bankstatementparser_loader_bacs import load_bacs_file, summarize_bacs

# Parse BACS Standard 18 transmission file
transactions = load_bacs_file("bacs_transmission.dat")
for tx in transactions:
    print(f"{tx.booking_date} | {tx.description} | {tx.amount} {tx.currency}")

# Extract transmission batch summary
summary = summarize_bacs(open("bacs_transmission.dat").read())
print(f"Total Transactions: {summary.total_transactions}")
print(f"Total Credit: {summary.total_credit} | Total Debit: {summary.total_debit}")
```

---

## Public API

- `load_bacs(data: str | bytes) -> list[Transaction]`: Ingests BACS string or bytes.
- `load_bacs_file(file_path: str | Path) -> list[Transaction]`: Ingests local BACS file.
- `summarize_bacs(data: str | bytes) -> BacsSummary`: Computes batch totals, credit/debit totals, and transaction count.
- `BacsStatementParser`: Main parser class implementing `parse()` and `to_transactions()`.

---

## BACS 18 Record Layout (106 bytes)

| Columns | Field Name | Description |
| :--- | :--- | :--- |
| `1-6` | Originating Sort Code | Sender bank sort code |
| `7-14` | Originating Account | Sender bank account number |
| `15-18` | Account Type | Account descriptor |
| `19-20` | Transaction Code | 2-character BACS operation code (`99`, `01`, `17`, etc.) |
| `21-26` | Destination Sort Code | Beneficiary bank sort code |
| `27-34` | Destination Account | Beneficiary account number |
| `35-38` | Free Format / Type | Record sub-type |
| `39-49` | Amount | 11-digit unsigned integer amount in pence |
| `50-67` | Originator Name | Sender entity name |
| `68-85` | Reference | Payment narrative / reference |
| `86-103` | Destination Name | Beneficiary entity name |
| `104-106` | Processing Date | Julian date representation |

---

## Development

The project enforces strict code-quality gates: 100% test and branch coverage, strict type annotations (`mypy`), style linting (`ruff`), docstring coverage (`interrogate`), and security scanning (`bandit`).

```bash
# Run test suite with branch coverage enforcement
poetry run pytest

# Type checking and linting
poetry run mypy .
poetry run ruff check .
poetry run ruff format --check .

# Documentation and security gates
poetry run interrogate -v
poetry run bandit -r . -c pyproject.toml
```

---


## Ecosystem

`bankstatementparser` is part of a modular financial ecosystem. Optional companion packages provide specialized loaders, writers, AI agents, language servers, and transport protocol adapters:

| Package | GitHub Repository | PyPI | Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`bankstatementparser`** | [`sebastienrousseau/bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser.svg)](https://pypi.org/project/bankstatementparser/) | Core Engine | Unified parser for CAMT (052/053), PAIN.001, CSV, OFX, QFX, MT940, and PDF statements |
| **`bankstatementparser-mcp`** | [`sebastienrousseau/bankstatementparser-mcp`](https://github.com/sebastienrousseau/bankstatementparser-mcp) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-mcp.svg)](https://pypi.org/project/bankstatementparser-mcp/) | AI Protocol | Model Context Protocol (MCP) server exposing statement tools to LLMs & AI agents |
| **`bankstatementparser-lsp`** | [`sebastienrousseau/bankstatementparser-lsp`](https://github.com/sebastienrousseau/bankstatementparser-lsp) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-lsp.svg)](https://pypi.org/project/bankstatementparser-lsp/) | Developer Tooling | Language Server Protocol (LSP) with live SWIFT MT940 statement validation & diagnostics |
| **`bankstatementparser-transport-ebics`** | [`sebastienrousseau/bankstatementparser-transport-ebics`](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-transport-ebics.svg)](https://pypi.org/project/bankstatementparser-transport-ebics/) | Transport | Automated bank statement retrieval over EBICS 3.0 (`H005`) and 2.5 (`H004`) protocols |
| **`bankstatementparser-writer-xlsx`** | [`sebastienrousseau/bankstatementparser-writer-xlsx`](https://github.com/sebastienrousseau/bankstatementparser-writer-xlsx) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-xlsx.svg)](https://pypi.org/project/bankstatementparser-writer-xlsx/) | Output Writer | Formats and exports parsed banking transactions into styled Microsoft Excel (`.xlsx`) workbooks |
| **`bankstatementparser-writer-qif`** | [`sebastienrousseau/bankstatementparser-writer-qif`](https://github.com/sebastienrousseau/bankstatementparser-writer-qif) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-qif.svg)](https://pypi.org/project/bankstatementparser-writer-qif/) | Output Writer | Serializes transactions into standard Quicken Interchange Format (`.qif`) exchange files |
| **`bankstatementparser-writer-ofx`** | [`sebastienrousseau/bankstatementparser-writer-ofx`](https://github.com/sebastienrousseau/bankstatementparser-writer-ofx) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-ofx.svg)](https://pypi.org/project/bankstatementparser-writer-ofx/) | Output Writer | Serializes transactions into standard Open Financial Exchange (`.ofx`) XML/SGML files |
| **`bankstatementparser-writer-swift`** | [`sebastienrousseau/bankstatementparser-writer-swift`](https://github.com/sebastienrousseau/bankstatementparser-writer-swift) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-swift.svg)](https://pypi.org/project/bankstatementparser-writer-swift/) | Output Writer | Exports transactions to SWIFT MT940 customer statements and MT942 interim reports |
| **`bankstatementparser-loader-bai2`** | [`sebastienrousseau/bankstatementparser-loader-bai2`](https://github.com/sebastienrousseau/bankstatementparser-loader-bai2) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-bai2.svg)](https://pypi.org/project/bankstatementparser-loader-bai2/) | Input Loader | Parses BAI2 cash-management and account balance statements |
| **`bankstatementparser-loader-mt942`** | [`sebastienrousseau/bankstatementparser-loader-mt942`](https://github.com/sebastienrousseau/bankstatementparser-loader-mt942) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-mt942.svg)](https://pypi.org/project/bankstatementparser-loader-mt942/) | Input Loader | Parses SWIFT MT942 interim transaction reports with credit/debit summary reconciliation |
| **`bankstatementparser-loader-cfonb`** | [`sebastienrousseau/bankstatementparser-loader-cfonb`](https://github.com/sebastienrousseau/bankstatementparser-loader-cfonb) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-cfonb.svg)](https://pypi.org/project/bankstatementparser-loader-cfonb/) | Input Loader | Parses French CFONB 120 / AFB120 120-byte fixed-width banking statement files |
| **`bankstatementparser-loader-camt054`** | [`sebastienrousseau/bankstatementparser-loader-camt054`](https://github.com/sebastienrousseau/bankstatementparser-loader-camt054) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-camt054.svg)](https://pypi.org/project/bankstatementparser-loader-camt054/) | Input Loader | Ingests ISO 20022 CAMT.054 real-time debit/credit notification stream XML |
| **`bankstatementparser-loader-sepa`** | [`sebastienrousseau/bankstatementparser-loader-sepa`](https://github.com/sebastienrousseau/bankstatementparser-loader-sepa) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-sepa.svg)](https://pypi.org/project/bankstatementparser-loader-sepa/) | Input Loader | Ingests ISO 20022 SEPA PAIN.002 payment status reports and PAIN.008 direct debit mandates |
| **`bankstatementparser-loader-bacs`** | [`sebastienrousseau/bankstatementparser-loader-bacs`](https://github.com/sebastienrousseau/bankstatementparser-loader-bacs) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-bacs.svg)](https://pypi.org/project/bankstatementparser-loader-bacs/) | Input Loader | Parses UK BACS Standard 18 / Faster Payments 106-byte fixed-width transmission files |

---

## Contributing

Contributions are welcome! Please submit an issue or pull request on GitHub. Ensure that all quality gates pass and test coverage remains at 100%.

---

## License

This project is dual-licensed under the **Apache License 2.0** and the **MIT License**. See [LICENSE-APACHE](LICENSE-APACHE) and [LICENSE-MIT](LICENSE-MIT) for full details.

