# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Load a Standard 18 file and summarise it.

The sample has the shape of ``tests/fixtures/standard18.bacs``: the
labels, a UHL1 header with a Julian date (``26015`` is 15 January 2026),
a credit (transaction code 99) and two Direct Debits (17 and 01).
"""

from bankstatementparser_loader_bacs import load_bacs, summarize_bacs


def detail(
    dest: str, code: str, pence: int, ref: str, name: str, date: str = ""
) -> str:
    """One detail record: destination, code, originator, amount, names."""
    return (
        f"{dest}0{code}40000087654321    {pence:011d}"
        f"{'ACME CORP LTD':<18}{ref:<18}{name:<18}{date}"
    )


SAMPLE = "\n".join(
    [
        "VOL1000001",
        "HDR1A000001S  1000001000100010001 26015 26015 000000",
        "UHL1 26015123456    000000001 DAILY  000",
        detail("20000012345678", "99", 250000, "JANUARY SALARY", "JOHN DOE"),
        detail(
            "20000088776655",
            "17",
            4550,
            "ELECTRICITY BILL",
            "JANE SMITH",
            "160126",
        ),
        detail("30999911223344", "01", 12999, "INSURANCE 0042", "A N OTHER"),
        "EOF1A000001S  1000001000100010001 26015 26015 000000",
    ]
)


def main() -> None:
    """Print each transaction, then the file's summary."""
    for tx in load_bacs(SAMPLE):
        print(
            f"{tx.booking_date}  {tx.amount:>9} {tx.currency}  "
            f"{tx.account_id}  {tx.category}  {tx.description}"
        )

    summary = summarize_bacs(SAMPLE)
    print(
        f"\nService user {summary.service_user_number}, "
        f"submitted {summary.submission_date}: "
        f"{summary.transaction_count} transactions, "
        f"credits {summary.total_credit}, debits {summary.total_debit}"
    )


if __name__ == "__main__":
    main()
