"""
This module contains tests for general files in Obsidian vaults.
"""

import logging
import pathlib

import pytest

from .common import RESERVED_SYMBOLS, vault_dirs


@pytest.mark.vault_test(True)
@vault_dirs
def test_v_files_titles(vault_dir: pathlib.PosixPath) -> None:
    """Check if there are inappropriate symbols in file names."""
    logger = logging.getLogger(__name__)
    err_count = 0
    for path in vault_dir.rglob("*"):
        for symbol in RESERVED_SYMBOLS:
            if symbol in path.name:
                err_msg = f"Symbol `{symbol}` in `{path.name}` ({path})."
                logger.error(err_msg)
                err_count += 1
    if err_count:
        raise AssertionError("Reserved symbols detected in file names. See error log for details.")


@pytest.mark.vault_test(True)
@vault_dirs
def test_v_files_trash(vault_dir: pathlib.PosixPath) -> None:
    """
    Check .trash directory.

    .trash directory may exist
    .trash directory may contain only a .keep file
    """
    logger = logging.getLogger(__name__)
    trash_dir = vault_dir / ".trash"
    if trash_dir.exists():
        assert trash_dir.is_dir()
        trash_files = []
        for path in trash_dir.rglob("*"):
            if path.name != ".keep":
                path_rel = path.relative_to(vault_dir.parent)
                trash_files.append(str(path_rel))
                logger.warning("%s: %s.", vault_dir.stem, path_rel)
        assert not trash_files, (
            f"Found {len(trash_files)} files in .trash directories: {trash_files}"
        )
    else:
        logger.warning("trash directory does not exist: '%s'", trash_dir)


@pytest.mark.vault_test(True)
@vault_dirs
def test_v_files_inbox(vault_dir: pathlib.PosixPath) -> None:
    """
    Check inboxes.

    _inbox directory should exist.
    _inbox directory should contain only a .keep file.
    """
    inbox_files = []
    inbox_dir = vault_dir / "_inbox"
    assert inbox_dir.exists(), f"'{inbox_dir.relative_to(vault_dir.parent)}' not found."
    assert inbox_dir.is_dir(), f"'{inbox_dir.relative_to(vault_dir.parent)}' is not a directory."
    inbox_keep = inbox_dir / ".keep"
    assert inbox_keep.exists(), f"'{inbox_keep.relative_to(vault_dir.parent)}' not found."
    assert inbox_keep.is_file(), f"'{inbox_keep.relative_to(vault_dir.parent)}' is not a file."
    for path in vault_dir.rglob("_inbox/*"):
        if path.name != ".keep":
            path_rel = path.relative_to(vault_dir.parent)
            inbox_files.append(str(path_rel))
            logging.warning("%s: %s.", vault_dir.stem, path_rel)
    assert not inbox_files, f"Found files in inboxes: {inbox_files}"
