# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Coverage-guided Atheris fuzz target for the BACS Standard 18 loader.

``load_bacs`` and ``summarize_bacs`` are the package's two entry points
for untrusted text. Neither documents an exception: a line that is not
a record is skipped, and a field that does not parse falls back (an
amount to its ASCII digits, a date to the UHL1 date or none). Any
exception escapes the target and libFuzzer records it as a crash.

Every transaction that loads must also be well formed: a finite amount,
``source == "bacs"`` and, when it has a category (a blank
transaction code leaves none), a ``bacs:<code>`` one; and the summary of
the same text must count the same transactions and net to the same
total.

Run (Linux x86_64, Python 3.12+, ``poetry install --with fuzz``)::

    python fuzz/fuzz_load_bacs.py fuzz/corpus -max_total_time=60
"""

from __future__ import annotations

import sys
from decimal import Decimal

import atheris

with atheris.instrument_imports():
    from bankstatementparser_loader_bacs import load_bacs, summarize_bacs


def test_one_input(data: bytes) -> None:
    """Load and summarise one fuzz input as BACS text."""
    text = atheris.FuzzedDataProvider(data).ConsumeUnicodeNoSurrogates(
        len(data)
    )
    transactions = load_bacs(text)
    net = Decimal(0)
    for txn in transactions:
        if not txn.amount.is_finite():
            raise AssertionError(f"non-finite amount {txn.amount!r}")
        category = txn.category or "bacs:"
        if txn.source != "bacs" or not category.startswith("bacs:"):
            raise AssertionError(f"mislabelled transaction {txn!r}")
        net += txn.amount
    summary = summarize_bacs(text)
    if summary.transaction_count != len(transactions):
        raise AssertionError("summary and load disagree on the count")
    if summary.total_credit - summary.total_debit != net:
        raise AssertionError("summary and load disagree on the total")


def main() -> None:
    """Hand the target to libFuzzer with the command-line options."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
