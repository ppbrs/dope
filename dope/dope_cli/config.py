"""
Processing user requests in the dope command-line tool
that are related to dope configuration
"""

import os
import subprocess
from typing import Any

from dope.config import get_config_path


def process_config_arguments(args: dict[str, Any]) -> int:
    """Process arguments related to configuration."""
    assert "config_editor" in args
    config_editor = args["config_editor"]
    if config_editor is not None:
        assert isinstance(config_editor, list)
        assert len(config_editor) == 1
        assert isinstance(config_editor[0], str)

        process = subprocess.Popen(
            [config_editor[0], get_config_path()],
            stdout=open(os.devnull, "wb"),
            stderr=open(os.devnull, "wb"),
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    return 0
