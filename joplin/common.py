"""
Paths, constants, functions, data structures
that are common to both Joplin tests, Joplin CLI.
"""

# Standard library imports
from dataclasses import dataclass
from pathlib import PosixPath
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

#
# Types
#

JId32 = str  # Contains 32 symbols 0123456789abcdef.


@dataclass
class JNote:
    """ All useful data of a notebook. """
    id32: JId32
    title: str
    body: str
    id32_parent: JId32  # id32 of the containing notebook

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
