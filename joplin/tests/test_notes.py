""" The module tests the contents of all notes in the local database."""
# Standard library imports
import logging
import os
# Third party imports
# Local application/library imports
import common  # pylint: disable=import-error


def test_notes_titles(db_local_notes: dict[common.JId32, common.JNote]):
    """
    Test titles of all notes for validity.
    """
    for title in [note.title for note in db_local_notes.values()]:
        common.validate_title(title)


def test_notes_being_edited(db_local_notes: dict[common.JId32, common.JNote], logger):
    """ Check if there aren't any notes that are being edited at the moment.

    Files that are being edited by external editors have names like this:
    edit-6e6598aad73a4abeb83285fabcd61e48.md
    """
    _, _, fnames = list(os.walk(common.DIR_LOCAL))[0]
    edited_notes = []
    for fname in fnames:

        if (fname.startswith("edit-") and fname.endswith(".md")
                and len(fname) == (4 + 1 + 32 + 1 + 2)):
            id32 = fname[5:-3]
            title = db_local_notes.get(id32).title
            logger.error(f"Note `{title}` is being edited. It should be closed.")
            edited_notes.append(title)
    assert len(edited_notes) == 0, "Some notes are opened for external editing."


def test_notes_symbols(db_local_notes: dict[common.JId32, common.JNote], logger: logging.Logger):
    """
    Check that restricted symbols are not used in note's body.
    """
    logger.info(f"{len(db_local_notes)=}")
    symbols = [
        # " ",  # No break space.
        " ",  # Hair space, or very thin space.
    ]
    line_cnt = 0
    for _, note in db_local_notes.items():
        for line in note.body.split("\n"):
            for symbol in symbols:
                if symbol in line:
                    logger.error(f"found {symbol} in {note.title}")
                    line_cnt += 1
                    break
    if line_cnt:
        logger.error(f"{line_cnt} lines have restricted symbols.")
