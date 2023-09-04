"""
Paths, constants, functions, data structures
that are common to both Joplin tests, Joplin CLI.
"""

# Standard library imports
from dataclasses import dataclass
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

#
# Types
#

JId32 = str  # Contains 32 symbols 0123456789abcdef.


@dataclass
class JItem:
    """Base class for notes, resources."""
    id32: JId32
    title: str


@dataclass
class JNote(JItem):
    """All useful data of a notebook."""
    body: str
    id32_parent: JId32  # id32 of the containing notebook


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


def _get_inline_id32s_in_notes() -> dict[JId32, list[JNote]]:
    """
    Find all "(:/id32)" in all notes.
    """
    notes: list[JNote] = get_db_local_notes().values()

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
