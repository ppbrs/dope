"""
This module contains tests for Obsidian vaults.
"""

import logging
import pathlib

from dope.v_note import VNote

from .common import RESERVED_SYMBOLS
from .common import vault_dirs

_logger = logging.getLogger(__name__)


@vault_dirs
def test_v_notes_newline(vault_dir: pathlib.PosixPath) -> None:
    """Check if there are Windows-style new lines in the notes."""
    cnt_no_empty_line = 0  # The number of notes with no empty line in the end.

    for v_note in VNote.collect_iter(vault_dirs=[vault_dir], exclude_trash=True):
        for _, note_line in v_note.lines_iter(lazy=True, remove_newline=False):
            # pylint: disable-next=not-an-iterable
            # (This looks like a false positive).
            assert not note_line.endswith("\r\n"), "Unexpected Windows-style newline."
            if not note_line.endswith("\n"):
                cnt_no_empty_line += 1
    if cnt_no_empty_line:
        _logger.warning("%d notes don't have an empty line in the end.", cnt_no_empty_line)


@vault_dirs
def test_v_notes_titles(vault_dir: pathlib.PosixPath) -> None:
    """Check if there are inappropriate symbols in note titles."""
    for v_note in VNote.collect_iter(vault_dirs=[vault_dir], exclude_trash=True):
        title = v_note.note_path.stem
        for symbol in RESERVED_SYMBOLS:
            if symbol in title:
                logging.warning(
                    "%s: Symbol `%s` in `%s`.",
                    v_note.vault_dir.stem, symbol, v_note.note_path.relative_to(v_note.vault_dir))


@vault_dirs
def test_v_notes_inbox(vault_dir: pathlib.PosixPath) -> None:
    """Check if there are unprocessed notes in inboxes."""
    for v_note in VNote.collect_iter(vault_dirs=[vault_dir], exclude_trash=True):
        vault_inbox_path = v_note.vault_dir / "_inbox"
        if v_note.note_path.parent == vault_inbox_path:
            logging.error(
                "%s's inbox contains a note: `%s`.", v_note.vault_dir.stem, v_note.note_path.stem)
