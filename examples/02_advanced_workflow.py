# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Advanced batch processing example for bankstatementparser-loader-bacs."""

from decimal import Decimal

from bankstatementparser_loader_bacs import load_bacs

SAMPLE = """VOL1000001
HDR1A00000100000100010001000000
UHL1 260019999999    0000000001
20000012345678009920000187654321000000000123456ORIGINATOR NAME   REF-1001          DESTINATION NAME  26001
EOF1A00000100000100010001000000"""


def main() -> None:
    print("Batch processing 100 iterations...")
    total_volume = Decimal("0")
    for _ in range(100):
        txns = load_bacs(SAMPLE)
        for t in txns:
            total_volume += abs(t.amount)
    print(
        f"Processed 100 batch statements. Total absolute volume: {total_volume}"
    )


if __name__ == "__main__":
    main()
