"""
Paths, constants, functions, data structures
that are common to both Joplin tests, Joplin CLI.
"""

# Standard library imports
from pathlib import PosixPath
# Third party imports
# Local application/library imports

DIR_LOCAL = PosixPath("~/.config/joplin-desktop/").expanduser()

FPATH_LOCAL_DB = PosixPath(DIR_LOCAL / "database.sqlite")
