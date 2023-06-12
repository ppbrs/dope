"""
Executing user requests to start programs.
"""
# Standard library imports
import os
from typing import Any
# Third party imports
# Local application/library imports


class JCliStart:
    """
    Executing user's request to start Joplin.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        self.ret_val = 0

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests to start programs.
        """
        if args["start_joplin"]:
            os.system("/opt/Joplin-2.12.19.AppImage &> /dev/null & disown")

        return self.ret_val
