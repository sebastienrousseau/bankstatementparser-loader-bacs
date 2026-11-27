# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Standard 18 numeric fields are ASCII digits; nothing else counts.

``str.isdigit`` is also true for superscripts and for the digits of
other scripts, which ``Decimal`` and ``int`` refuse or read as numbers.
A stray ``"²"`` in an amount used to escape ``load_bacs`` as
``decimal.InvalidOperation``, and one in a date as ``ValueError``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from bankstatementparser_loader_bacs import load_bacs, summarize_bacs
from bankstatementparser_loader_bacs.loader import (
    _decode_bacs_amount,
    _parse_julian_or_gregorian_date,
)

_LINE = (
    "112233"
    "12345678"
    "0"
    "99"
    "654321"
    "87654321"
    "0000"
    "00000250000"
    + "ACME LTD".ljust(18)
    + "INV 42".ljust(18)
    + "JANE DOE".ljust(18)
    + "150126"
)


def _with(start: int, end: int, value: str) -> str:
    """``_LINE`` with columns ``start``-``end`` (1-based) replaced."""
    return _LINE[: start - 1] + value + _LINE[end:]


@pytest.mark.parametrize("amount", ["0000000025²", "¹" * 11])
def test_superscript_in_amount_is_not_a_digit(amount: str) -> None:
    """Only the ASCII digits of the amount field are read."""
    (tx,) = load_bacs(_with(36, 46, amount))
    assert tx.amount == Decimal(
        "".join(c for c in amount if c in "0123456789") or "0"
    ) / Decimal(100)


def test_other_script_digits_in_amount_are_not_read() -> None:
    """Arabic-Indic digits are not pence."""
    assert _decode_bacs_amount("١٢", False) == Decimal("0.00")


@pytest.mark.parametrize(
    "raw",
    [
        "2²015",
        "²6015",
        "26²15",
        "١٥٠١٢٦",
    ],
)
def test_non_ascii_date_is_not_a_date(raw: str) -> None:
    """A date field with a non-ASCII digit does not parse."""
    assert _parse_julian_or_gregorian_date(raw) is None


def test_bad_processing_date_falls_back_to_the_header() -> None:
    """The detail line keeps the UHL1 date when its own does not parse."""
    text = "UHL1 26015999999\n" + _with(101, 106, "2²015 ")
    (tx,) = load_bacs(text)
    assert tx.booking_date == date(2026, 1, 15)


def test_bad_header_date_leaves_no_submission_date() -> None:
    """A UHL1 date with a superscript digit is no date at all."""
    summary = summarize_bacs("UHL1 2\u00b2015999999 ")
    assert summary.submission_date is None
    assert summary.service_user_number == "999999"
