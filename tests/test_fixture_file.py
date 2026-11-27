# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Golden test for ``tests/fixtures/standard18.bacs``.

The fixture is a whole Standard 18 file (labels, a UHL1 with a Julian
date, a credit, two debits, trailers) that the README demo, the fuzz
seeds and the examples show; this pins what the loader reads from it.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from bankstatementparser_loader_bacs import (
    BacsStatementParser,
    load_bacs_file,
    summarize_bacs,
)

FIXTURE = Path(__file__).parent / "fixtures" / "standard18.bacs"


def test_transactions() -> None:
    """Every detail line becomes one signed transaction."""
    rows = [
        (t.booking_date, t.amount, t.account_id, t.category, t.reference)
        for t in load_bacs_file(FIXTURE)
    ]
    assert rows == [
        (
            date(2026, 1, 15),
            Decimal("2500.00"),
            "200000-12345678",
            "bacs:99",
            "JANUARY SALARY",
        ),
        (
            date(2026, 1, 16),
            Decimal("-45.50"),
            "200000-88776655",
            "bacs:17",
            "ELECTRICITY BILL",
        ),
        (
            date(2026, 1, 15),
            Decimal("-129.99"),
            "309999-11223344",
            "bacs:01",
            "INSURANCE 0042",
        ),
    ]


def test_summary() -> None:
    """The summary carries the UHL1 header and the totals."""
    summary = summarize_bacs(FIXTURE.read_text(encoding="utf-8"))
    assert summary.service_user_number == "123456"
    assert summary.originating_sort_code == "400000"
    assert summary.originating_account == "87654321"
    assert summary.submission_date == date(2026, 1, 15)
    assert summary.transaction_count == 3
    assert summary.total_credit == Decimal("2500.00")
    assert summary.total_debit == Decimal("175.49")


def test_parser_plugin() -> None:
    """The core's plugin interface reads the same file."""
    parser = BacsStatementParser(str(FIXTURE))
    assert list(parser.parse()["amount"]) == [2500.0, -45.5, -129.99]
    assert parser.get_summary()["transaction_count"] == 3
