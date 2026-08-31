# BACS Standard 18 / Faster Payments Loader for Bank Statement Parser

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0_OR_MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/sebastienrousseau/bankstatementparser-loader-bacs)

BACS Standard 18 (106-character / 100-character fixed width) and Faster Payments transmission file loader plugin for [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser).

---

## Features

- **BACS Standard 18 Parser**: Supports full UK BACS file structure (`VOL1`, `HDR1`, `UHL1`, Standard 18 details, `EOF1`, `UTL1`).
- **Direct Debit & Direct Credit**: Correctly decodes transaction codes (`99` Direct Credit, `01`/`17`/`18`/`19` Direct Debit) and calculates signed transaction amounts in GBP.
- **Julian & Gregorian Date Support**: Supports 5-digit Julian dates (`YYDDD`) and Gregorian formats (`DDMMYY`, `YYMMDD`).
- **Seamless Plugin Integration**: Dynamically registers under `bankstatementparser.loaders` entry points (`bacs`, `std18`).

---

## Installation

```bash
pip install bankstatementparser-loader-bacs
```

---

## Quickstart

```python
from bankstatementparser_loader_bacs import load_bacs_file, summarize_bacs

# 1. Parse BACS statement into standard Transaction models
transactions = load_bacs_file("statement.bacs")
for tx in transactions:
    print(f"{tx.booking_date} | {tx.description} | {tx.amount} {tx.currency}")

# 2. Get statement summary metrics
summary = summarize_bacs(open("statement.bacs").read())
print(f"SUN: {summary.service_user_number}")
print(f"Total Credit: {summary.total_credit} | Total Debit: {summary.total_debit}")
```

---

## License

Dual-licensed under Apache 2.0 and MIT.
