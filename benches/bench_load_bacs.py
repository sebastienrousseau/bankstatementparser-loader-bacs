#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.
"""What a BACS Standard 18 file costs to load, as the file grows.

A Standard 18 submission is one fixed-width line per payment between a
UHL1 header and the trailer labels. A payroll or Direct Debit run is
sized by the service user's customer base, not by the caller, so the
axis that moves in practice is the number of detail records in one
file: a few for a small firm, tens of thousands for a utility's
monthly collection.

Read ``us/txn``. Flat means linear, and a large collection run is fine.
Climbing means something rescans records it has already read.

``summarize_bacs`` is measured beside ``load_bacs``: it parses the same
records but builds no ``Transaction`` objects, so a caller that only
wants totals should pay less than one that wants every transaction.

Run::

    python benches/bench_load_bacs.py
    python benches/bench_load_bacs.py --json
    python benches/bench_load_bacs.py --quick     # what CI runs

Nothing here asserts a threshold: wall-clock is not comparable between
machines, and a flaky performance gate teaches people to ignore red. CI
runs ``--quick`` so a benchmark that has stopped running against the
current API fails the build instead of rotting into a file that reads
as verified and is not.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bankstatementparser_loader_bacs import (  # noqa: E402
    load_bacs,
    summarize_bacs,
)

HEADER = [
    "VOL1000001".ljust(80),
    "HDR1A000001S  1000001000100010001 26015 26015 000000".ljust(80),
    "UHL1 26015123456    000000001 DAILY  000".ljust(80),
]
TRAILER = [
    "EOF1A000001S  1000001000100010001 26015 26015 000000".ljust(80),
    "UTL1".ljust(80),
]
# Credits (99) and Direct Debit collections (17) alternate.
CODES = ("99", "17")


def detail(i: int) -> str:
    """One 106-character Standard 18 detail record."""
    return (
        f"{200000 + i % 1000:06d}{i % 10**8:08d}0{CODES[i % 2]}"
        f"40000087654321    {(i % 90000) + 100:011d}"
        f"{'ACME CORP LTD':<18}{f'REF{i:08d}':<18}"
        f"{f'CUSTOMER {i}':<18} 26015"
    )


def build(records: int) -> str:
    """A Standard 18 file with ``records`` detail records."""
    return "\n".join(HEADER + [detail(i) for i in range(records)] + TRAILER)


def _best(call: Callable[[], object], repeats: int) -> float:
    """Best-of timing after one untimed warm-up.

    The minimum is the least noisy estimator available; the mean follows
    whatever else the machine happens to be doing.
    """
    call()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        samples.append(time.perf_counter() - start)
    return min(samples)


def measure(records: int, repeats: int) -> dict[str, Any]:
    """Time ``load_bacs`` and ``summarize_bacs`` on one file size."""
    text = build(records)
    load = _best(lambda: load_bacs(text), repeats)
    summary = _best(lambda: summarize_bacs(text), repeats)
    transactions = len(load_bacs(text))
    if transactions != records or (
        summarize_bacs(text).transaction_count != records
    ):
        raise SystemExit(f"expected {records} records, read {transactions}")
    return {
        "transactions": transactions,
        "bytes": len(text),
        "load_ms": load * 1e3,
        "summary_ms": summary * 1e3,
        "us_per_txn": load * 1e6 / transactions,
        "summary_over_load": summary / load,
    }


def run(quick: bool) -> list[dict[str, Any]]:
    """Measure every file size; ``quick`` keeps to the small ones."""
    if quick:
        sizes, repeats = [10, 100], 3
    else:
        sizes, repeats = [10, 100, 1_000, 10_000, 50_000], 7
    return [measure(n, repeats) for n in sizes]


def render(rows: list[dict[str, Any]]) -> None:
    """Print the table and what it means."""
    print(
        f"{'records':>9}{'KiB':>9}{'load ms':>10}"
        f"{'summary ms':>12}{'us/txn':>9}"
    )
    for row in rows:
        print(
            f"{row['transactions']:>9}{row['bytes'] / 1024:>9.1f}"
            f"{row['load_ms']:>10.2f}{row['summary_ms']:>12.2f}"
            f"{row['us_per_txn']:>9.2f}"
        )
    drift = rows[-1]["us_per_txn"] / rows[0]["us_per_txn"]
    print(
        f"\n  us/txn at {rows[-1]['transactions']:,} records is "
        f"{drift:.2f}x the cost at {rows[0]['transactions']:,}. Flat is "
        f"linear; climbing means something rescans records it has "
        f"already read."
    )
    worst = max(r["summary_over_load"] for r in rows)
    print(
        f"\n  summarize_bacs costs up to {worst:.2f}x load_bacs. A ratio "
        f"near 1.00 would mean the summary pays for Transaction objects "
        f"it never returns."
    )


def main() -> int:
    """Parse the options, run, and print a table or JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--quick", action="store_true", help="small sizes, as CI runs"
    )
    args = parser.parse_args()

    rows = run(quick=args.quick)
    if args.json:
        json.dump(rows, sys.stdout, indent=1)
        print()
    else:
        render(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
