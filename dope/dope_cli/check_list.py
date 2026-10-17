"""
Check-list related functions.
"""

import pathlib
import subprocess
from typing import Any

from dope.config import get_config


def process_check_list(args: dict[str, Any]) -> int:
    """
    Executing user's request to open the check list.
    """
    if args["check_list"]:
        cl_path = get_config().get("check-list")
        if cl_path is None:
            print("Check list not configured.")
        else:
            cl_path = pathlib.PosixPath(cl_path).expanduser()
            if not cl_path.exists():
                print(f"Check list doesn't exist: '{cl_path}'")
            else:
                app = "libreoffice"
                proc: subprocess.Popen[str] = subprocess.Popen(
                    [app, cl_path],
                    shell=False,
                    text=True,
                    start_new_session=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if proc.returncode:
                    print(f"Opening '{cl_path}' with '{app}' failed, returned {proc.returncode}")
                else:
                    print(f"Opening '{cl_path}' with '{app}' OK")
    return 0
