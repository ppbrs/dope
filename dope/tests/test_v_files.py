"""
This module contains tests for general files in Obsidian vaults.
"""

import logging

from dope.paths import V_DIRS

from .common import RESERVED_SYMBOLS

_logger = logging.getLogger(__name__)


def test_v_files_titles() -> None:
    """Check if there are inappropriate symbols in file names."""
    for vault_dir in V_DIRS:
        _logger.info("Checking files in vault '%s'", vault_dir.stem)
        for path in vault_dir.rglob("*"):
            for symbol in RESERVED_SYMBOLS:
                if symbol in path.name:
                    logging.warning(
                        "%s: Symbol `%s` in `%s` (%s).",
                        vault_dir.stem, symbol, path.name, path)
