""" The module tests the contents of all notes in the local database."""
import logging
import os
import re

import pytest

from joplin.common import DIR_LOCAL, JId32, JNote, JResource, validate_title

from joplin.common import DIR_LOCAL, JId32, JNote, JResource, validate_title


@pytest.mark.skip
def test_notes_evernote_link(db_local_notes: dict[JId32, JNote],
                             logger: logging.Logger):
    """ Check if there are no obsolete evernote links.

    Example:
    evernote:///view/109847503/s583/085ab0a0-5f76-4763/085ab0a0-5f76-4763-b3eb-03e0fa24e35e/
    https://www.evernote.com/shard/s583/nl/109847503/5751a4d9-f9c4-4144-b67f-13aa6c9b77c3
    """
    evernote_lnk_res = [
        re.compile(r".*\(evernote:///view.*"),
        re.compile(r".*www\.evernote\.com.*"),
    ]
    link_cnt = 0
    for _, note in db_local_notes.items():
        for line_idx, line in enumerate(note.body.split("\n")):
            for re_ in evernote_lnk_res:
                if re_.match(line):
                    logger.warning("TITLE: %s, LINE %d: %s", note.title, line_idx, line)
                    link_cnt += 1
                    # break
    if link_cnt > 0:
        logger.error("Found %d evernote links", link_cnt)
        assert False


def test_notes_titles(db_local_notes: dict[JId32, JNote]) -> None:
    """
    Test titles of all notes for validity.
    """
    for title in [note.title for note in db_local_notes.values()]:
        validate_title(title)


def test_notes_being_edited(db_local_notes: dict[JId32, JNote], logger: logging.Logger) -> None:
    """ Check if there aren't any notes that are being edited at the moment.

    Files that are being edited by external editors have names like this:
    edit-6e6598aad73a4abeb83285fabcd61e48.md
    """
    _, _, fnames = list(os.walk(DIR_LOCAL))[0]
    edited_notes = []
    for fname in fnames:

        if (fname.startswith("edit-") and fname.endswith(".md")
                and len(fname) == (4 + 1 + 32 + 1 + 2)):
            id32 = fname[5:-3]
            title = db_local_notes[id32].title
            logger.error(f"Note `{title}` is being edited. It should be closed.")
            edited_notes.append(title)
    assert len(edited_notes) == 0, "Some notes are opened for external editing."


def test_notes_links(db_local_notes: dict[JId32, JNote],
                     db_local_used_resources: dict[JId32, JResource],
                     logger: logging.Logger) -> None:
    """
    Check that links to other notes or resources exist.

    Note link example:
    [!week 2023-15 ♥](:/c5aab03733f14748973dc7de8dd4a78f)
    """
    re_grp_title = r"[^\\]\[(.*)\]"
    re_grp_id32 = r"\(:/([0-9a-f]{32})\)"
    re_ptrn = re.compile(rf".*{re_grp_title}{re_grp_id32}.*")

    cnt_lnk = 0
    cnt_err = 0
    for _, note in db_local_notes.items():
        for line in note.body.split("\n"):
            if (mtch := re_ptrn.match(line)):
                cnt_lnk += 1
                title_lnk, id32_lnk = mtch.groups()
                if id32_lnk not in db_local_notes and id32_lnk not in db_local_used_resources:
                    logger.error("Link not found: ID32=`%s`, LEGEND=`%s`, in NOTE=`%s`.",
                                 id32_lnk, title_lnk, note.title)
                    cnt_err += 1
    logger.info(f"Found {cnt_lnk} links in notes.")
    assert cnt_err == 0, f"Found {cnt_err} error(s) in links."


def test_notes_symbols(db_local_notes: dict[JId32, JNote], logger: logging.Logger) -> None:
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
