# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Concurrency and stress tests for BACS Standard 18 loader."""

import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from bankstatementparser_loader_bacs import load_bacs

SAMPLE_BACS = """VOL1000001
HDR1A00000100000100010001000000
UHL1 260019999999    0000000001
20000012345678009920000187654321000000000123456ORIGINATOR NAME   REF-1001          DESTINATION NAME  26001
EOF1A00000100000100010001000000"""


def test_bacs_concurrency() -> None:
    """Verify BACS parsing throughput."""
    iterations = 1000
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(load_bacs, SAMPLE_BACS) for _ in range(iterations)
        ]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start

    assert len(results) == iterations
    for txns in results:
        assert len(txns) == 1
        assert txns[0].amount == Decimal("123.45")
    assert elapsed < 5.0
