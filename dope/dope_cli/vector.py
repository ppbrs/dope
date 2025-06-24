"""
Executing user requests related to vector images.
"""
import logging
import subprocess as sp
from typing import Any

from dope.config import get_vault_paths

_logger = logging.getLogger(__name__)


class Vector:
    """Namespace for functions that generate vector images."""

    @staticmethod
    def process(args: dict[str, Any]) -> int:
        """
        Executing user's requests related to vector images.
        """
        if not args["vector"]:
            return 0

        vault_dirs = get_vault_paths(filter=args["vault"])
        for vault_dir in vault_dirs:
            for path in vault_dir.glob("**/*.toml"):
                _logger.info("Converting %s to SVG", path)
                conversion_proc = sp.run(
                    ["toml2svg", path],
                    check=False,
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT,
                    text=True,
                )
                if conversion_proc.returncode == 0:
                    _logger.info("OK")
                else:
                    _logger.error("FAIL")
                for line in conversion_proc.stdout.splitlines():
                   _logger.debug(line)


        return 0

