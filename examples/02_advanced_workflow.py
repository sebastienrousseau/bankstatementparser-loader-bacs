# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Read a Standard 18 file through the core's parser plugin.

Installing the package registers ``BacsStatementParser`` under the
``bacs`` and ``std18`` names in the ``bankstatementparser.loaders``
entry-point group. This writes a small file, reads it with the plugin
as a pandas DataFrame and the summary dict, and reconciles the totals.
"""

import tempfile
from decimal import Decimal
from pathlib import Path

from bankstatementparser_loader_bacs import BacsStatementParser, load_bacs_file

LINES = [
    "UHL1 26015123456    000000001 DAILY  000",
    # destination sort code + account, account type, transaction code,
    # originating sort code + account, free format, amount in pence,
    # originator name, reference, destination name, processing date
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
    " 26015",
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
    "160126",
]


def main() -> None:
    """Parse with the plugin and check its totals against the records."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "submission.bacs"
        path.write_text("\n".join(LINES) + "\n", encoding="utf-8")

        parser = BacsStatementParser(str(path))
        print(parser.parse().to_string(index=False))

        summary = parser.get_summary()
        net = sum((tx.amount for tx in load_bacs_file(path)), Decimal(0))
        print(f"\nsummary: {summary}")
        credit = Decimal(str(summary["total_credit"]))
        debit = Decimal(str(summary["total_debit"]))
        if credit - debit != net:
            raise SystemExit(f"summary nets {credit - debit}, records {net}")
        print(f"net {net} GBP matches the summary")


if __name__ == "__main__":
    main()
