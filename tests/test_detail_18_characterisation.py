# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Characterisation tests for ``_handle_detail_18``.

They pin the exact record each Standard 18 line produces today, at every
length threshold the parser checks, so a restructure of the function
cannot change its output unnoticed. The expected values are what the
code returned when the tests were written, not a specification.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from bankstatementparser_loader_bacs.loader import (
    _BacsState,
    _handle_detail_18,
)


def _line(
    dest_sort: str = "112233",
    dest_acct: str = "12345678",
    code: str = "99",
    orig_sort: str = "654321",
    orig_acct: str = "87654321",
    amt: str = "00000250000",
    orig_name: str = "ACME LTD",
    ref: str = "INV 42",
    dest_name: str = "JANE DOE",
    proc: str = " 26020",
) -> str:
    """Build a Standard 18 detail line from its fields."""
    return (
        dest_sort.ljust(6)
        + dest_acct.ljust(8)
        + "0"
        + code.ljust(2)
        + orig_sort.ljust(6)
        + orig_acct.ljust(8)
        + "0000"
        + amt.rjust(11)
        + orig_name.ljust(18)
        + ref.ljust(18)
        + dest_name.ljust(18)
        + proc.ljust(6)
    )


_FULL = _line()

_CASES: dict[str, tuple[str, dict[str, Any]]] = {
    "full_credit": (_FULL, {}),
    "full_debit": (_line(code="17"), {}),
    "len16": (_FULL[:16], {}),
    "len30": (_FULL[:30], {}),
    "len31": (_FULL[:31], {}),
    "len45": (_FULL[:45], {}),
    "len46": (_FULL[:46], {}),
    "len64": (_FULL[:64], {}),
    "len82": (_FULL[:82], {}),
    "len100": (_FULL[:100], {}),
    "no_names_credit": (_line(orig_name="", dest_name=""), {}),
    "dest_name_only_credit": (_line(orig_name=""), {}),
    "ref_in_description": (_line(orig_name="PAY INV 42"), {}),
    "no_ref": (_line(ref=""), {}),
    "no_dest_sort": (_line(dest_sort=""), {}),
    "no_dest_acct": (_line(dest_acct=""), {}),
    "no_dest_no_orig_acct": (_line(dest_sort="", orig_acct=""), {}),
    "bad_proc_date": (_line(proc="XXXXXX"), {"sub_date": date(2026, 1, 15)}),
    "state_has_orig": (
        _FULL,
        {"orig_sort": "000001", "orig_acct": "00000002"},
    ),
    "short_with_state": (
        _FULL[:20],
        {
            "orig_sort": "000001",
            "orig_acct": "00000002",
            "sub_date": date(2026, 1, 15),
        },
    ),
    "debit_code_01_short_name": (_line(code="01", dest_name=""), {}),
}

# The record the full credit line yields; every case below is
# this record with the fields it lists replaced.
_BASE: dict[str, Any] = {
    "destination_sort_code": "112233",
    "destination_account": "12345678",
    "originating_sort_code": "654321",
    "originating_account": "87654321",
    "account_id": "112233-12345678",
    "currency": "GBP",
    "amount": Decimal("2500"),
    "booking_date": date(2026, 1, 20),
    "value_date": date(2026, 1, 20),
    "description": "ACME LTD - INV 42",
    "reference": "INV 42",
    "tx_code": "99",
    "counterparty": "JANE DOE",
}

# Per case: the fields that differ from _BASE, then the state's
# (orig_sort, orig_acct) afterwards.
_EXPECTED: dict[str, Any] = {
    "full_credit": ({}, ("654321", "87654321")),
    "full_debit": (
        {
            "amount": Decimal("-2500"),
            "description": "JANE DOE - INV 42",
            "tx_code": "17",
            "counterparty": "ACME LTD",
        },
        ("654321", "87654321"),
    ),
    "len16": (
        {
            "originating_sort_code": "",
            "originating_account": "",
            "amount": Decimal("0.00"),
            "booking_date": None,
            "value_date": None,
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("", ""),
    ),
    "len30": (
        {
            "originating_account": "",
            "amount": Decimal("0.00"),
            "booking_date": None,
            "value_date": None,
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("654321", ""),
    ),
    "len31": (
        {
            "amount": Decimal("0.00"),
            "booking_date": None,
            "value_date": None,
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("654321", "87654321"),
    ),
    "len45": (
        {
            "amount": Decimal("0.00"),
            "booking_date": None,
            "value_date": None,
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("654321", "87654321"),
    ),
    "len46": (
        {
            "booking_date": None,
            "value_date": None,
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("654321", "87654321"),
    ),
    "len64": (
        {
            "booking_date": None,
            "value_date": None,
            "description": "ACME LTD",
            "reference": None,
            "counterparty": "",
        },
        ("654321", "87654321"),
    ),
    "len82": (
        {"booking_date": None, "value_date": None, "counterparty": ""},
        ("654321", "87654321"),
    ),
    "len100": (
        {"booking_date": None, "value_date": None},
        ("654321", "87654321"),
    ),
    "no_names_credit": (
        {"description": "BACS Transfer - INV 42", "counterparty": ""},
        ("654321", "87654321"),
    ),
    "dest_name_only_credit": (
        {"description": "JANE DOE - INV 42"},
        ("654321", "87654321"),
    ),
    "ref_in_description": (
        {"description": "PAY INV 42"},
        ("654321", "87654321"),
    ),
    "no_ref": (
        {"description": "ACME LTD", "reference": None},
        ("654321", "87654321"),
    ),
    "no_dest_sort": (
        {"destination_sort_code": "", "account_id": "87654321"},
        ("654321", "87654321"),
    ),
    "no_dest_acct": (
        {"destination_account": "", "account_id": "87654321"},
        ("654321", "87654321"),
    ),
    "no_dest_no_orig_acct": (
        {
            "destination_sort_code": "",
            "originating_account": "",
            "account_id": "BACS",
        },
        ("654321", ""),
    ),
    "bad_proc_date": (
        {"booking_date": date(2026, 1, 15), "value_date": date(2026, 1, 15)},
        ("654321", "87654321"),
    ),
    "state_has_orig": ({}, ("000001", "00000002")),
    "short_with_state": (
        {
            "originating_sort_code": "000001",
            "originating_account": "00000002",
            "amount": Decimal("0.00"),
            "booking_date": date(2026, 1, 15),
            "value_date": date(2026, 1, 15),
            "description": "BACS Transfer",
            "reference": None,
            "counterparty": "",
        },
        ("000001", "00000002"),
    ),
    "debit_code_01_short_name": (
        {
            "amount": Decimal("-2500"),
            "description": "- INV 42",
            "tx_code": "01",
            "counterparty": "ACME LTD",
        },
        ("654321", "87654321"),
    ),
}


@pytest.mark.parametrize("name", sorted(_CASES))
def test_detail_18_record_is_unchanged(name: str) -> None:
    """Each line yields exactly the record, and state, pinned for it."""
    raw, initial = _CASES[name]
    state = _BacsState(**initial)
    _handle_detail_18(raw, state)
    changed, orig = _EXPECTED[name]
    expected = [{**_BASE, **changed}]
    # repr, not ==, so key order, a Decimal's exponent and a value's
    # type count too.
    assert repr(state.records) == repr(expected)
    assert (state.orig_sort, state.orig_acct) == orig
