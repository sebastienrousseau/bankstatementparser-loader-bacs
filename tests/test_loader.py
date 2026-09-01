# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Tests for UK BACS Standard 18 & Faster Payments Statement Loader."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from bankstatementparser_loader_bacs import (
    BacsStatementParser,
    BacsSummary,
    __version__,
    load_bacs,
    load_bacs_file,
    summarize_bacs,
)
from bankstatementparser_loader_bacs.loader import (
    _decode_bacs_amount,
    _parse_bacs_stream,
    _parse_julian_or_gregorian_date,
)


def _sample_bacs_18_text() -> str:
    """Return a standard BACS Standard 18 text file."""
    # VOL1 & HDR1
    vol = "VOL1123456" + " " * 70
    hdr = "HDR1BACS18    12345600010001000100 26015 26015 000000" + " " * 20
    uhl = "UHL1 26015999999    0000000001 DAILY " + " " * 40

    # Record 1: Credit 99 (Salary payment: 2500.00 GBP = 250000 pence)
    # Positions: Dest Sort (6), Dest Acct (8), Dest Type (1), Tx Code (2), Orig Sort (6), Orig Acct (8), Free (4), Amount (11), Orig Name (18), Ref (18), Dest Name (18), Date (6)
    rec1 = (
        "200000"
        "12345678"
        "0"
        "99"
        "400000"
        "87654321"
        "    "
        "00000250000"
        "ACME CORP LTD     "
        "JANUARY SALARY    "
        "JOHN DOE          "
        "26015 "
    )

    # Record 2: Debit 17 (Direct Debit collection: 45.50 GBP = 4550 pence)
    rec2 = (
        "200000"
        "88776655"
        "0"
        "17"
        "400000"
        "87654321"
        "    "
        "00000004550"
        "ACME CORP LTD     "
        "ELECTRICITY BILL  "
        "JANE SMITH        "
        "150126"
    )

    eof = "EOF1BACS18" + " " * 70
    utl = "UTL1000000045500000025000000000010000001" + " " * 40

    return "\n".join([vol, hdr, uhl, rec1, rec2, eof, utl])


def test_version() -> None:
    """Verifies that version is exposed and semantic."""
    assert __version__ == "0.0.19"


def test_load_bacs_stream() -> None:
    """Tests parsing BACS 18 records into transactions."""
    text = _sample_bacs_18_text()
    txs = load_bacs(text)

    assert len(txs) == 2

    t1 = txs[0]
    assert t1.account_id == "200000-12345678"
    assert t1.amount == Decimal("2500.00")
    assert t1.currency == "GBP"
    assert t1.booking_date == date(2026, 1, 15)
    assert "ACME CORP LTD" in (t1.description or "")
    assert t1.reference == "JANUARY SALARY"
    assert t1.category == "bacs:99"
    assert t1.source == "bacs"
    assert t1.source_index == 0

    t2 = txs[1]
    assert t2.account_id == "200000-88776655"
    assert t2.amount == Decimal("-45.50")
    assert t2.currency == "GBP"
    assert t2.booking_date == date(2026, 1, 15)
    assert "JANE SMITH" in (t2.description or "")
    assert t2.reference == "ELECTRICITY BILL"
    assert t2.category == "bacs:17"
    assert t2.source_index == 1


def test_summarize_bacs() -> None:
    """Tests summary extraction for BACS file."""
    text = _sample_bacs_18_text()
    summary = summarize_bacs(text)

    assert isinstance(summary, BacsSummary)
    assert summary.service_user_number == "999999"
    assert summary.originating_sort_code == "400000"
    assert summary.originating_account == "87654321"
    assert summary.currency == "GBP"
    assert summary.submission_date == date(2026, 1, 15)
    assert summary.transaction_count == 2
    assert summary.total_credit == Decimal("2500.00")
    assert summary.total_debit == Decimal("45.50")


def test_bacs_statement_parser_class(tmp_path: Path) -> None:
    """Tests BacsStatementParser BankStatementParser protocol implementation."""
    sample_file = tmp_path / "statement.bacs"
    sample_file.write_text(_sample_bacs_18_text(), encoding="utf-8")

    parser = BacsStatementParser(sample_file)
    df = parser.parse()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "amount" in df.columns
    assert "date" in df.columns
    assert "account_id" in df.columns

    summary = parser.get_summary()
    assert summary["service_user_number"] == "999999"
    assert summary["originating_sort_code"] == "400000"
    assert summary["transaction_count"] == 2
    assert summary["total_credit"] == 2500.00
    assert summary["total_debit"] == 45.50


def test_bacs_statement_parser_empty(tmp_path: Path) -> None:
    """Tests parser on empty file."""
    empty_file = tmp_path / "empty.bacs"
    empty_file.write_text("", encoding="utf-8")

    parser = BacsStatementParser(empty_file)
    df = parser.parse()
    assert len(df) == 0
    assert "amount" in df.columns

    summary = parser.get_summary()
    assert summary["transaction_count"] == 0
    assert summary["service_user_number"] is None


def test_date_parser_edge_cases() -> None:
    """Tests Julian and Gregorian date parsing."""
    assert _parse_julian_or_gregorian_date("26001") == date(2026, 1, 1)
    assert _parse_julian_or_gregorian_date("26032") == date(2026, 2, 1)
    assert _parse_julian_or_gregorian_date("26999") is None
    assert _parse_julian_or_gregorian_date("010226") == date(2026, 2, 1)
    assert _parse_julian_or_gregorian_date("991226") == date(1999, 12, 26)
    assert _parse_julian_or_gregorian_date("999999") is None
    assert _parse_julian_or_gregorian_date("invalid") is None
    assert _parse_julian_or_gregorian_date("") is None


def test_amount_decoder_edge_cases() -> None:
    """Tests BACS amount decoder edge cases."""
    assert _decode_bacs_amount("", is_debit=False) == Decimal("0.00")
    assert _decode_bacs_amount("   ", is_debit=False) == Decimal("0.00")
    assert _decode_bacs_amount("100", is_debit=False) == Decimal("1.00")
    assert _decode_bacs_amount("100", is_debit=True) == Decimal("-1.00")


def test_short_and_blank_lines_ignored() -> None:
    """Tests that blank lines and lines shorter than 4 chars are skipped."""
    lines = ["", "   ", "VOL", "XYZ"]
    state = _parse_bacs_stream(lines)
    assert len(state.records) == 0


def test_load_bacs_file(tmp_path: Path) -> None:
    """Tests load_bacs_file helper."""
    f = tmp_path / "test.bacs"
    f.write_text(_sample_bacs_18_text(), encoding="utf-8")
    txs = load_bacs_file(f)
    assert len(txs) == 2


@given(
    amount_int=st.integers(min_value=0, max_value=999999999),
    is_debit=st.booleans(),
)
def test_fuzz_bacs_amount(amount_int: int, is_debit: bool) -> None:
    """Property-based fuzzing of BACS amount decoder."""
    raw = f"{amount_int:011d}"
    val = _decode_bacs_amount(raw, is_debit)
    assert isinstance(val, Decimal)
