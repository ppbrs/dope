"""
This file contains paths to database files and to vaults.
"""
import os
from pathlib import PosixPath

#
# Obsidian vaults
#

V_DIRS: list[PosixPath] = [
    PosixPath("~/Dropbox/the-vault").expanduser(),
    PosixPath("~/projects/z").expanduser(),
    PosixPath("~/Dropbox/projects/fl").expanduser(),
]
for v_dir in V_DIRS:
    assert v_dir.exists() and v_dir.is_dir()

#
# Obsidian Application
#

OBSIDIAN_APP_PATH = PosixPath("/opt/Obsidian-1.5.3.AppImage")
assert OBSIDIAN_APP_PATH.exists() and OBSIDIAN_APP_PATH.is_file()

#
# Rover
#

ROVER_BASE_PATH = PosixPath(f"/run/user/{os.getuid()}/gvfs/")
