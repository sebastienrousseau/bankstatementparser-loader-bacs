# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""BACS Standard 18 / Faster Payments UK banking statement loader.

Parses UK BACS Standard 18 (106-character / 100-character fixed-width) files
into ``bankstatementparser.transaction_models.Transaction`` objects.
"""

from __future__ import annotations

from .loader import (
    BacsStatementParser,
    BacsSummary,
    load_bacs,
    load_bacs_file,
    summarize_bacs,
)

__version__ = "0.0.1"
__all__ = [
    "BacsStatementParser",
    "BacsSummary",
    "__version__",
    "load_bacs",
    "load_bacs_file",
    "summarize_bacs",
]
