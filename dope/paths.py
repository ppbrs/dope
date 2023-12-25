"""
This file contains paths to database files and to vaults.
"""
from pathlib import PosixPath

#
# Joplin database and resources
#

J_DIR_LOCAL = PosixPath("~/.config/joplin-desktop/").expanduser()
assert J_DIR_LOCAL.exists() and J_DIR_LOCAL.is_dir()

J_PATH_LOCAL_DB = PosixPath(J_DIR_LOCAL / "database.sqlite")
assert J_PATH_LOCAL_DB.exists() and J_PATH_LOCAL_DB.is_file()

J_DIR_LOCAL_RESOURCES = PosixPath(J_DIR_LOCAL / "resources")
assert J_DIR_LOCAL_RESOURCES.exists() and J_DIR_LOCAL_RESOURCES.is_dir()

J_DIR_LOCAL_EDITED_RESOURCES = PosixPath(J_DIR_LOCAL / "tmp" / "edited_resources")
# I'm not checking the existence of this directory because it's created automaticaly by Joplin
# when a resource file is being opened for editing.

#
# Obsidian vaults
#

V_DIRS = [
    PosixPath("~/Dropbox/the-vault").expanduser(),
    PosixPath("~/projects/z").expanduser(),
    PosixPath("~/Dropbox/projects/fl").expanduser(),
]
for v_dir in V_DIRS:
    assert v_dir.exists() and v_dir.is_dir()
