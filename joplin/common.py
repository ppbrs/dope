"""
Paths, constants, functions, data structures
that are common to both Joplin tests, Joplin CLI.
"""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import PosixPath
import re
# Third party imports
# Local application/library imports
import sqlite3

#
# Paths
#

DIR_LOCAL = PosixPath("~/.config/joplin-desktop/").expanduser()
assert DIR_LOCAL.exists() and DIR_LOCAL.is_dir()

FPATH_LOCAL_DB = PosixPath(DIR_LOCAL / "database.sqlite")
assert FPATH_LOCAL_DB.exists() and FPATH_LOCAL_DB.is_file()

DIR_LOCAL_RESOURCES = PosixPath(DIR_LOCAL / "resources")
assert DIR_LOCAL_RESOURCES.exists() and DIR_LOCAL_RESOURCES.is_dir()

DIR_LOCAL_EDITED_RESOURCES = PosixPath(DIR_LOCAL / "tmp" / "edited_resources")
# I'm not checking the existence of this directory because it's created by Joplin only
# when a resource is opened for editing.

#
# Types
#

JId32 = str  # Contains 32 symbols 0123456789abcdef.


@dataclass
class JItem:
    """Base class for notebooks, notes, resources, tags."""
    id32: JId32
    title: str


@dataclass
class JNotebook(JItem):
    """All useful data of a notebook."""
    id32_parent: JId32 | None
    """id32 of the containing notebook or None if this is one of the root notebooks."""


@dataclass
class JNote(JItem):
    """All useful data of a note."""
    body: str
    id32_parent: JId32  # id32 of the containing notebook


@dataclass
class JTag(JItem):
    """All useful data of a tag."""
    notes: list[JNote] = field(default_factory=lambda: [])
    id32_parent: JTag | None = field(default_factory=lambda: None)


TAG_WAIT = "$w8"
TAG_NEXT = "$nxt"
TAG_NOW = "$now"


@dataclass
class JResource(JItem):
    """All useful data of a notebook."""
    mime: str
    size: str
    notes: list[JNote]

    def __str__(self) -> str:
        res = (f"Resource(id32={self.id32}, title={self.title}, mime={self.mime}, "
               f"size={self.size}, notes=[")
        for note in self.notes:
            res += f"\"{note.title}\", "
        res += "])"
        return res


#
# Functions:
#

def get_db_local_notes() -> dict[JId32, JNote]:
    """
    Parses the local database and returns a dictionary
    with notes' IDs as keys and JNote objects as values.
    """
    notes = {}
    with sqlite3.connect(database=f"file:{FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        cur = db_conn.cursor()
        cur.execute("SELECT id, title, body, parent_id FROM notes")
        for id32, title, body, id32_parent in cur.fetchall():
            if id32 in notes:
                raise ValueError(f"Found a note with ID {id32} more than once.")
            notes[id32] = JNote(id32=id32, title=title, body=body, id32_parent=id32_parent)
    return notes


def get_db_local_notebooks() -> dict[JId32, JNotebook]:
    """
    Returns a dictionary with notebooks's id32 as key and JNotebook object as value.
    """
    notebooks = {}
    with sqlite3.connect(database=f"file:{FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        cur = db_conn.cursor()
        cur.execute("SELECT id, title, parent_id FROM folders")
        for id32, title, id32_parent in cur.fetchall():
            if not id32_parent:
                id32_parent = None
            notebooks[id32] = JNotebook(id32=id32, title=title, id32_parent=id32_parent)
    return notebooks


def _get_inline_id32s_in_notes() -> dict[JId32, list[JNote]]:
    """
    Find all "(:/id32)" in all notes.
    """
    notes: list[JNote] = list(get_db_local_notes().values())

    id32s: dict[JId32, list[JNote]] = {}  # Dictionary of inline ID32 occurences.
    id32_ptrn = re.compile(r"([0-9abcdef]{32}).*")
    for note in notes:
        # Instead of splitting body by \r\n, I split it by "(:/".
        # The reason is that there may be several occurences of the pattern in one line.
        for line in note.body.split("(:/"):
            if (mtch := id32_ptrn.match(line)):
                id32 = mtch.groups()[0]
                if id32 not in id32s:
                    id32s[id32] = [note]
                else:
                    id32s[id32].append(note)
    return id32s


def get_db_local_used_resources() -> dict[JId32, JResource]:
    """
    Return a dictionary with resources' IDs as keys and JResource objects as values.
    Only resources whose IDs are referenced in notes are returned.
    """
    id32s = _get_inline_id32s_in_notes()

    resources = {}
    with sqlite3.connect(database=f"file:{FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        cur = db_conn.cursor()
        cur.execute("SELECT id, title, mime, size FROM resources")
        for id32, title, mime, size in cur.fetchall():
            resources[id32] = JResource(id32=id32, title=title, mime=mime, size=size, notes=[])
            if id32 in id32s:
                resources[id32].notes = list(id32s[id32])

    return resources


def get_db_local_tags() -> dict[JId32, JTag]:
    """
    Return a dictionary with tags's IDs as keys and JTag objects as values.
    The information is taken from the local database.
    """
    tags: dict[JId32, JTag] = {}
    notes: dict[JId32, JNote] = get_db_local_notes()
    with sqlite3.connect(database=f"file:{FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        cur = db_conn.cursor()
        cur.execute("SELECT id, title, parent_id FROM tags")
        for id32, title, id32_parent in cur.fetchall():
            tags[id32] = JTag(id32=id32, title=title)
            if id32_parent != "":
                raise NotImplementedError
        cur.execute("SELECT note_id, tag_id FROM note_tags")
        for note_id32, tag_id32 in cur.fetchall():
            assert tag_id32 in tags
            if note_id32 in notes:
                tags[tag_id32].notes.append(notes[note_id32])
    return tags


def validate_title(title: str, tag: bool = False) -> None:
    """
    Check the title of a note or a notebook.
    """
    # Prohibited patterns and reasons why they are prohibited:
    prohibited_patterns: list[tuple[re.Pattern, str]] = [
        # Heading, trailing and multiple spaces:
        (re.compile(r".*\s{2,}.*"), "Multiple spaces."),
        (re.compile(r"^\s.*"), "Heading space."),
        (re.compile(r".*\s$"), "Trailing space."),

        # Slashes are generally forbidden because titles are intended to be used as file names:
        (re.compile(r".*/.*"), "Slash."),
        (re.compile(r".*\\.*"), "Backslash."),

        # Heading special symbols.
        (re.compile(r"^\~.*"), "Heading special symbol."),
        (re.compile(r"^\`.*"), "Heading special symbol."),
        (re.compile(r"^\%.*"), "Heading special symbol."),
        (re.compile(r"^\^.*"), "Heading special symbol."),

        # Titles for tasks are normally 4 digits, then a colon, then a space
        (re.compile(r"^\d\d\d\d^:.*"), "No colon after the index."),
        (re.compile(r"\d{1,3}\D*"), "1, 2,or 3 heading digits."),
        (re.compile(r"\d{5,}\D*"), "1, 2,or 3 heading digits."),
    ]
    if not tag:
        prohibited_patterns += [
            (re.compile(r"^\#.*"), "Heading special symbol."),
            (re.compile(r"^\@.*"), "Heading special symbol."),
            (re.compile(r"^\$.*"), "Heading special symbol."),
            (re.compile(r"^\&.*"), "Heading special symbol."),
        ]

    for pattern, reason in prohibited_patterns:
        if pattern.fullmatch(title) is not None:
            assert pattern.fullmatch(title) is None, \
                f"Title check failed: {reason} Title: `{title}`."

    # Make sure that there are no 0-31 (ASCII control characters).
    # While it is legal under Linux/Unix file systems to create files
    # with control characters in the filename, it might be a nightmare
    # for the users to deal with such files.
    for char in title:
        assert ord(char) >= 32, f"ASCII control character in the title: `{title}`."
