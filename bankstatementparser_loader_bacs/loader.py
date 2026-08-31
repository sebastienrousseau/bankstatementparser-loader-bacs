# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Core UK BACS Standard 18 & Faster Payments Statement Loader."""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from bankstatementparser.base_parser import BankStatementParser
from bankstatementparser.transaction_models import Transaction

SOURCE = "bacs"

# Known BACS transaction codes
# Debits: 01 (Direct Debit), 17 (Direct Debit regular), 18 (Direct Debit representation), 19 (Direct Debit final)
_DEBIT_CODES = {"01", "17", "18", "19"}


def _decode_bacs_amount(raw_pence: str, is_debit: bool) -> Decimal:
    """Convert raw 11-digit pence string to signed Decimal."""
    clean = "".join(ch for ch in raw_pence if ch.isdigit())
    if not clean:
        return Decimal("0.00")
    pence = Decimal(clean)
    amt = pence / Decimal("100")
    return -amt if is_debit else amt


def _parse_julian_or_gregorian_date(raw: str) -> date | None:
    """Parse BACS date formatted as YYDDD (Julian) or DDMMYY / YYMMDD."""
    clean = raw.strip()
    if len(clean) == 5 and clean.isdigit():
        year = 2000 + int(clean[:2])
        day_of_year = int(clean[2:])
        if not (1 <= day_of_year <= 366):
            return None
        res = date.fromordinal(date(year, 1, 1).toordinal() + day_of_year - 1)
        return res if res.year == year else None
    if len(clean) == 6 and clean.isdigit():
        for fmt in ("%d%m%y", "%y%m%d"):
            try:
                return datetime.strptime(clean, fmt).date()
            except ValueError:
                continue
    return None


@dataclass(frozen=True)
class BacsSummary:
    """Summary metrics and headers for a BACS Standard 18 submission."""

    service_user_number: str | None
    originating_sort_code: str | None
    originating_account: str | None
    currency: str
    submission_date: date | None
    transaction_count: int
    total_credit: Decimal
    total_debit: Decimal


@dataclass
class _BacsState:
    """Internal accumulator for parsed BACS records."""

    sun: str = ""
    orig_sort: str = ""
    orig_acct: str = ""
    currency: str = "GBP"
    sub_date: date | None = None
    records: list[dict[str, Any]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize records list."""
        if self.records is None:
            self.records = []


def _handle_uhl1_header(raw: str, state: _BacsState) -> None:
    """Parse User Header Label (UHL1)."""
    if len(raw) >= 11:
        raw_date = raw[4:10].strip()
        state.sub_date = _parse_julian_or_gregorian_date(raw_date)
    if len(raw) >= 17:
        state.sun = raw[10:16].strip()


def _handle_detail_18(raw: str, state: _BacsState) -> None:
    """Parse BACS Standard 18 transaction line."""
    dest_sort = raw[0:6].strip()
    dest_acct = raw[6:14].strip()
    tx_code = raw[15:17].strip() if len(raw) >= 17 else "99"
    orig_sort = raw[17:23].strip() if len(raw) >= 23 else state.orig_sort
    orig_acct = raw[23:31].strip() if len(raw) >= 31 else state.orig_acct

    if not state.orig_sort and orig_sort:
        state.orig_sort = orig_sort
    if not state.orig_acct and orig_acct:
        state.orig_acct = orig_acct

    raw_amt = raw[35:46].strip() if len(raw) >= 46 else ""
    is_debit = tx_code in _DEBIT_CODES
    amount = _decode_bacs_amount(raw_amt, is_debit)

    orig_name = raw[46:64].strip() if len(raw) >= 64 else ""
    ref = raw[64:82].strip() if len(raw) >= 82 else ""
    dest_name = raw[82:100].strip() if len(raw) >= 100 else ""
    proc_date_raw = raw[100:106].strip() if len(raw) >= 106 else ""
    proc_date = (
        _parse_julian_or_gregorian_date(proc_date_raw) or state.sub_date
    )

    description = (
        dest_name if is_debit else (orig_name or dest_name or "BACS Transfer")
    )
    if ref and ref not in description:
        description = f"{description} - {ref}".strip()

    state.records.append(
        {
            "destination_sort_code": dest_sort,
            "destination_account": dest_acct,
            "originating_sort_code": orig_sort,
            "originating_account": orig_acct,
            "account_id": f"{dest_sort}-{dest_acct}"
            if dest_sort and dest_acct
            else (orig_acct or "BACS"),
            "currency": state.currency,
            "amount": amount,
            "booking_date": proc_date,
            "value_date": proc_date,
            "description": description,
            "reference": ref or None,
            "tx_code": tx_code,
            "counterparty": orig_name if is_debit else dest_name,
        }
    )


def _parse_bacs_stream(lines: Iterable[str]) -> _BacsState:
    """Parse BACS stream lines into accumulated state."""
    state = _BacsState()

    for line in lines:
        raw = line.rstrip("\r\n")
        if not raw or len(raw) < 4:
            continue

        prefix = raw[:4].upper()
        if prefix == "UHL1":
            _handle_uhl1_header(raw, state)
        elif prefix in ("VOL1", "HDR1", "HDR2", "EOF1", "EOF2", "UTL1"):
            continue
        elif len(raw) >= 30 and raw[:6].isdigit():
            _handle_detail_18(raw, state)

    return state


def load_bacs(text_or_lines: str | Iterable[str]) -> list[Transaction]:
    """Parse BACS Standard 18 text into domain Transaction models.

    Args:
        text_or_lines: Raw BACS payload or line iterable.

    Returns:
        List of Transaction instances.
    """
    lines = (
        text_or_lines.splitlines()
        if isinstance(text_or_lines, str)
        else text_or_lines
    )
    state = _parse_bacs_stream(lines)
    transactions: list[Transaction] = []

    for idx, rec in enumerate(state.records):
        tx = Transaction(
            account_id=rec.get("account_id"),
            currency=rec.get("currency", "GBP"),
            amount=rec["amount"],
            booking_date=rec.get("booking_date"),
            value_date=rec.get("value_date"),
            description=rec.get("description"),
            reference=rec.get("reference"),
            category=f"bacs:{rec['tx_code']}" if rec.get("tx_code") else None,
            source=SOURCE,
            source_index=idx,
        )
        transactions.append(tx)

    return transactions


def load_bacs_file(path: str | os.PathLike[str]) -> list[Transaction]:
    """Read and parse a BACS statement file from disk.

    Args:
        path: Path to the BACS file.

    Returns:
        List of Transaction instances.
    """
    content = Path(path).read_text(encoding="utf-8", errors="replace")
    return load_bacs(content)


def summarize_bacs(text_or_lines: str | Iterable[str]) -> BacsSummary:
    """Generate financial metrics and headers summary for a BACS statement.

    Args:
        text_or_lines: Raw BACS payload or line iterable.

    Returns:
        A BacsSummary instance.
    """
    lines = (
        text_or_lines.splitlines()
        if isinstance(text_or_lines, str)
        else text_or_lines
    )
    state = _parse_bacs_stream(lines)

    total_credit = Decimal("0.00")
    total_debit = Decimal("0.00")

    for rec in state.records:
        amt = rec["amount"]
        if amt > 0:
            total_credit += amt
        else:
            total_debit += abs(amt)

    return BacsSummary(
        service_user_number=state.sun or None,
        originating_sort_code=state.orig_sort or None,
        originating_account=state.orig_acct or None,
        currency=state.currency,
        submission_date=state.sub_date,
        transaction_count=len(state.records),
        total_credit=total_credit,
        total_debit=total_debit,
    )


class BacsStatementParser(BankStatementParser):
    """BankStatementParser plugin implementation for UK BACS Standard 18 files."""

    def __init__(self, file_name: str | Path, **kwargs: Any) -> None:
        """Initialize the BACS statement parser.

        Args:
            file_name: Path to the BACS statement file.
            **kwargs: Extra options passed to base parser.
        """
        super().__init__(file_name, **kwargs)
        self._summary_cache: BacsSummary | None = None

    def parse(self) -> pd.DataFrame:
        """Parse the BACS file into a pandas DataFrame.

        Returns:
            A pandas DataFrame containing standardized statement transactions.
        """
        txs = self.to_transactions()
        if not txs:
            return pd.DataFrame(
                columns=[
                    "date",
                    "description",
                    "amount",
                    "currency",
                    "account_id",
                    "reference",
                    "source",
                ]
            )

        records = [
            {
                "date": tx.booking_date.isoformat() if tx.booking_date else "",
                "description": tx.description or "",
                "amount": float(tx.amount),
                "currency": tx.currency,
                "account_id": tx.account_id,
                "reference": tx.reference,
                "source": tx.source,
            }
            for tx in txs
        ]
        return pd.DataFrame(records)

    def to_transactions(self) -> list[Transaction]:
        """Parse the BACS file into a list of Transaction models.

        Returns:
            List of parsed Transaction instances.
        """
        return load_bacs_file(self.file_name)

    def get_summary(self) -> dict[str, Any]:
        """Get summary metadata and balance metrics for the BACS file.

        Returns:
            Dictionary with statement statistics.
        """
        if self._summary_cache is None:
            content = Path(self.file_name).read_text(
                encoding="utf-8", errors="replace"
            )
            self._summary_cache = summarize_bacs(content)

        s = self._summary_cache
        return {
            "service_user_number": s.service_user_number,
            "originating_sort_code": s.originating_sort_code,
            "originating_account": s.originating_account,
            "currency": s.currency,
            "submission_date": (
                s.submission_date.isoformat() if s.submission_date else None
            ),
            "transaction_count": s.transaction_count,
            "total_credit": float(s.total_credit),
            "total_debit": float(s.total_debit),
        }
