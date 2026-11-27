# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""The documented Standard 18 record layout matches what the loader reads.

Every row of the layout table (``| `start-end` | Field | ... |``) in each
document below is checked against the parser: the documented columns of
one detail line are overwritten with a marker, and the field the row
names must come back as that marker. A row for a field the loader skips
must leave the parsed record unchanged. A row naming a field this test
does not know fails, so the table cannot drift from the code unchecked.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from bankstatementparser_loader_bacs.loader import _parse_bacs_stream

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = [ROOT / "README.md", ROOT / "docs" / "format.md"]

_ROW = re.compile(r"^\|\s*`(\d+)(?:-(\d+))?`\s*\|\s*([^|]+?)\s*\|", re.M)

# A credit detail line (code 99) with every field populated.
_BASE = "".join(
    [
        "112233",  # 1-6 destination sort code
        "12345678",  # 7-14 destination account
        "0",  # 15 destination account type
        "99",  # 16-17 transaction code
        "654321",  # 18-23 originating sort code
        "87654321",  # 24-31 originating account
        "0000",  # 32-35 free format
        "00000250000",  # 36-46 amount in pence
        "ACME LTD".ljust(18),  # 47-64 originator (service user) name
        "INV 42".ljust(18),  # 65-82 reference
        "JANE DOE".ljust(18),  # 83-100 destination account name
        "150126",  # 101-106 processing date
    ]
)

Record = dict[str, Any]
Check = tuple[Callable[[int], str], Callable[[Record, str], bool]]


def _digits(width: int) -> str:
    """A run of non-repeating digits ``width`` long."""
    return ("9876543210" * 3)[:width]


def _letters(width: int) -> str:
    """A run of capital letters ``width`` long."""
    return "QWERTYUIOPASDFGHJKLZ"[:width]


_CHECKS: dict[str, Check] = {
    "destination sort code": (
        _digits,
        lambda rec, m: rec["destination_sort_code"] == m,
    ),
    "destination account": (
        _digits,
        lambda rec, m: rec["destination_account"] == m,
    ),
    "transaction code": (
        lambda _w: "17",
        lambda rec, m: rec["tx_code"] == m,
    ),
    "originating sort code": (
        _digits,
        lambda rec, m: rec["originating_sort_code"] == m,
    ),
    "originating account": (
        _digits,
        lambda rec, m: rec["originating_account"] == m,
    ),
    "amount": (
        _digits,
        lambda rec, m: rec["amount"] == Decimal(m) / 100,
    ),
    "originator name": (
        _letters,
        lambda rec, m: rec["description"].startswith(m),
    ),
    "reference": (
        _letters,
        lambda rec, m: rec["reference"] == m,
    ),
    "destination name": (
        _letters,
        lambda rec, m: rec["counterparty"] == m,
    ),
    "processing date": (
        lambda _w: "311227",
        lambda rec, m: rec["booking_date"] == date(2027, 12, 31),
    ),
}

# Documented columns the loader reads past without using.
_SKIPPED = {"destination account type", "free format"}


def _parse(line: str) -> Record:
    """Parse one detail line and return its single record."""
    records = _parse_bacs_stream([line]).records
    assert len(records) == 1
    return records[0]


def _rows(document: Path) -> list[tuple[int, int, str]]:
    """The (start, end, field) rows of a document's layout table."""
    text = document.read_text(encoding="utf-8")
    return [
        (int(a), int(b or a), name.strip().lower())
        for a, b, name in _ROW.findall(text)
    ]


@pytest.mark.parametrize(
    "document", DOCUMENTS, ids=[str(p.relative_to(ROOT)) for p in DOCUMENTS]
)
def test_layout_table_matches_the_loader(document: Path) -> None:
    """Each documented column range carries the field it is named for."""
    if not document.exists():
        pytest.skip(f"{document.name} not present")
    rows = _rows(document)
    assert rows, f"{document.name} has no record layout table"
    baseline = _parse(_BASE)
    for start, end, field in rows:
        width = end - start + 1
        if field in _SKIPPED:
            marker = "7" * width
        else:
            assert field in _CHECKS, f"undocumented check for {field!r}"
            marker = _CHECKS[field][0](width)
            assert len(marker) == width, (field, marker)
        line = _BASE[: start - 1] + marker + _BASE[end:]
        record = _parse(line)
        if field in _SKIPPED:
            assert record == baseline, f"{field} at {start}-{end} is read"
        else:
            assert _CHECKS[field][1](record, marker), (
                f"{document.name}: {field!r} is not at columns {start}-{end}"
            )
