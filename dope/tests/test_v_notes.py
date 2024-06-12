"""
This module contains tests for Obsidian vaults.
"""

import logging

from dope.v_note import VNote

_logger = logging.getLogger(__name__)


def test_v_notes_newline() -> None:
    """Check if there are Windows-style new lines in the notes."""
    cnt_no_empty_line = 0  # The number of notes with no empty line in the end.

    for v_note in VNote.collect_iter(exclude_trash=True):
        for _, note_line in v_note.lines_iter(lazy=True, remove_newline=False):
            # pylint: disable-next=not-an-iterable
            # (This looks like a false positive).
            assert not note_line.endswith("\r\n"), "Unexpected Windows-style newline."
            if not note_line.endswith("\n"):
                cnt_no_empty_line += 1
    if cnt_no_empty_line:
        _logger.warning("%d notes don't have an empty line in the end.", cnt_no_empty_line)


def test_v_notes_titles() -> None:
    """Check if there are inappropriate symbols in note titles."""
    for v_note in VNote.collect_iter(exclude_trash=True):
        title = v_note.note_path.stem
        symbols = ["`", "[", "]"]
        for symbol in symbols:
            if symbol in title:
                logging.warning(
                    "%s: Symbol `%s` in `%s`.",
                    v_note.vault_dir.stem, symbol, v_note.note_path.relative_to(v_note.vault_dir))


def test_v_notes_inbox() -> None:
    """Check if there are unprocessed notes in inboxes."""
    for v_note in VNote.collect_iter(exclude_trash=True):
        vault_inbox_path = v_note.vault_dir / "_inbox"
        if v_note.note_path.parent == vault_inbox_path:
            logging.error(
                "%s's inbox contains a note: `%s`.", v_note.vault_dir.stem, v_note.note_path.stem)
