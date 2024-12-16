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


def test_v_files_trash() -> None:
    """Check if there are files in .trash directory."""
    trash_files = []
    for vault_dir in V_DIRS:
        for path in vault_dir.rglob(".trash/*"):
            path_rel = path.relative_to(vault_dir.parent)
            trash_files.append(str(path_rel))
            logging.warning("%s: %s.", vault_dir.stem, path_rel)
    assert not trash_files, f"Found files in .trash directories: {trash_files}"
