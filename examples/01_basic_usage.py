# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Basic usage example for bankstatementparser-loader-bacs."""

from bankstatementparser_loader_bacs import load_bacs, summarize_bacs

SAMPLE = """VOL1000001
HDR1A00000100000100010001000000
UHL1 260019999999    0000000001
20000012345678009920000187654321000000000123456ORIGINATOR NAME   REF-1001          DESTINATION NAME  26001
EOF1A00000100000100010001000000"""


def main() -> None:
    print("Loading statement...")
    txns = load_bacs(SAMPLE)
    for tx in txns:
        print(
            f"  Transaction: {tx.booking_date} | {tx.amount} {tx.currency} | {tx.description}"
        )

    summary = summarize_bacs(SAMPLE)
    print(f"Summary generated successfully: {summary}")


if __name__ == "__main__":
    main()
