"""
This module tests correctness of the local database againt by GTD workflow.
GTD stands for Getting Things Done.
"""
# Standard library imports
# Third party imports
# Local application/library imports
from joplin.common import JNote, JTag, JId32, TAG_NOW, TAG_NEXT, TAG_WAIT


def test_gtd_wait(db_local_notes: dict[JId32, JNote],
                  db_local_tags: dict[JId32, JTag]) -> None:
    """
    Each note with the "$w8" tag must have a line containing a "@w8" mark describing what
    I am waiting for and how long should I wait.
    Each note containing a line with "@w8" must be tagged with "$w8".
    """

    jtag_w8: JTag = \
        [x for x in db_local_tags.values() if x.title == TAG_WAIT][0]

    for jnote in jtag_w8.notes:
        lines = jnote.body.split("\n")
        desciption_found = False
        for line in lines:
            if "@w8" in line:
                desciption_found = True
        assert desciption_found, f"No @w8 mark found in note \"{jnote.title}.\""

    for jnote in db_local_notes.values():
        lines = jnote.body.split("\n")
        for line in lines:
            if "@w8" in line:
                tagged = False
                for jnote_tagged in jtag_w8.notes:
                    if jnote.id32 == jnote_tagged.id32:
                        tagged = True
                        break
                assert tagged, f"Note with @w8 description not tagged with $w8: \"{jnote.title}.\""


def test_gtd_next(db_local_notes: dict[JId32, JNote],
                  db_local_tags: dict[JId32, JTag]) -> None:
    """
    Each note with the "$nxt" tag must have a line containing a "@nxt" mark describing
    what is my next action and what is the deadline.
    Each note containing a line with "@nxt" must be tagged with "$nxt".
    """

    jtag_nxt: JTag = \
        [x for x in db_local_tags.values() if x.title == TAG_NEXT][0]

    for jnote in jtag_nxt.notes:
        lines = jnote.body.split("\n")
        desciption_found = False
        for line in lines:
            if "@nxt" in line:
                desciption_found = True
        assert desciption_found, f"No @nxt mark found in note \"{jnote.title}.\""

    for jnote in db_local_notes.values():
        lines = jnote.body.split("\n")
        for line in lines:
            if "@nxt" in line:
                tagged = False
                # logger.warning(f"Found @nxt in {jnote}")
                for jnote_tagged in jtag_nxt.notes:
                    if jnote.id32 == jnote_tagged.id32:
                        tagged = True
                        break
                assert tagged, f"Note with @nxt mark not tagged with $nxt: \"{jnote.title}.\""


def test_gtd_now(db_local_notes: dict[JId32, JNote],
                 db_local_tags: dict[JId32, JTag]) -> None:
    """
    Each note with the "$now" tag must have a line containing a "@now" mark describing
    what I am currently doing and what is the deadline.
    Each note containing a line "@now" must be tagged with "$now".
    """

    jtag_now: JTag = \
        [x for x in db_local_tags.values() if x.title == TAG_NOW][0]

    for jnote in db_local_notes.values():
        lines = jnote.body.split("\n")
        for line in lines:
            if "@now" in line:
                tagged = False
                for jnote_tagged in jtag_now.notes:
                    if jnote.id32 == jnote_tagged.id32:
                        tagged = True
                        break
                assert tagged, f"Note with @now mark not tagged with $now: \"{jnote.title}.\""


def test_gtd_tags(db_local_tags: dict[JId32, JTag]) -> None:
    """
    Check that the essential GTD tags exist.
    """
    gtd_tags = [
        TAG_NOW,
        TAG_NEXT,
        TAG_WAIT,
        "$week",
        "$month",
        "$day",
        "$later",
    ]
    for gtd_tag in gtd_tags:
        assert gtd_tag in [x.title for x in db_local_tags.values()], \
            f"Tag `{gtd_tag}` not found."


def test_gtd_forbidden_marks(db_local_notes: dict[JId32, JNote]) -> None:
    """
    Check that the marks from the list are not used in notes.
    """
    forbidden_marks = ["$nxt", "$now", "$w8", "@ntx"]

    for jnote in db_local_notes.values():
        lines = jnote.body.split("\n")
        for line in lines:
            for mark in forbidden_marks:
                assert mark not in line, \
                    f"The forbidden mark `{mark}` is used in: \"{jnote.title}.\""
