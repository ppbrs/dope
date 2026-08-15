"""
Executing user requests related to vaults.
"""

from __future__ import annotations

import enum
import logging
import os
import pathlib
import shlex
from typing import Any

from dope.config import get_vault_paths

_logger = logging.getLogger(__name__)


@enum.unique
class Ide(enum.Enum):
    """Enum for all supported IDEs."""

    CODE = enum.auto()

    @staticmethod
    def from_arg(arg: str) -> Ide:
        """Parse user argument for an IDE to one of supported IDEs."""
        match arg:
            case "code":
                return Ide.CODE
            case _:
                raise ValueError(f"Unknown IDE: {arg}.")

    def open_vault(self, vault_dir: pathlib.PosixPath) -> None:
        """Open a vault is this IDE."""
        match self:
            case Ide.CODE:
                code_dir = vault_dir / ".vscode"
                if code_dir.exists() and code_dir.is_dir():
                    os.system(f"cd {vault_dir} && code .")
                else:
                    _logger.error("Cannot open `%s` in `VS Code`.", vault_dir.name)


class VaultUtils:
    """An object of this class has everything that is needed to manage vaults."""

    # pylint: disable=too-few-public-methods

    @staticmethod
    def filter_vault_dirs(args: dict[str, Any]) -> list[pathlib.PosixPath]:
        """
        Parse the --vault argument and collect the requested vaults.
        """
        vault_filter: None | list[str] = args["vault"]
        if vault_filter is None:
            return list(get_vault_paths())
        vault_dirs = []
        for vault_dir in get_vault_paths():
            for vault_substr in vault_filter:
                if vault_substr in vault_dir.name:
                    vault_dirs.append(vault_dir)
        return vault_dirs

    @staticmethod
    def process(args: dict[str, Any]) -> int:
        """
        Executing user's requests related to vaults.
        """
        ret_val = 0

        if args["ide"] is not None:
            ret_val += VaultUtils._process_ide(args=args)

        if args["stat"]:
            ret_val += VaultUtils._process_stat(args=args)

        # Wrapper around Pytest that runs only tests that check vaults.
        # Invocation examples:
        #   d --test -v vault1
        #   d --test -v vault1 -- --collect-only -k sport
        if args["test"]:
            dope_root_dir = pathlib.PosixPath(__file__).parent.parent.parent
            cmd = f"cd {dope_root_dir}; pytest -m vault_test"
            vault_filter: None | list[str] = args["vault"]
            if vault_filter:
                cmd += f" --vault {' '.join(vault_filter)}"

            remainder = args["remainder"]
            if remainder and remainder[0] == "--":
                # Turning a list of arguments into a single, shell-safe string by automatically
                # adding quotes to any argument that contains spaces or special characters:
                cmd += " " + shlex.join(remainder[1:])
            _logger.debug("cmd: %s", cmd)
            os.system(cmd)

        return ret_val

    @staticmethod
    def _process_ide(args: dict[str, Any]) -> int:
        """
        --ide/-i option opens vaults with specified IDEs.
        """
        assert isinstance(args["ide"], list)
        ides_known = set(Ide)
        if not args["ide"]:
            ides = ides_known
        else:
            ides = set()
            for arg in args["ide"]:
                ides.add(Ide.from_arg(arg))
            assert ides
        _logger.info("IDEs (%d): %s.", len(ides), ", ".join(ide.name for ide in ides))

        # Open the vaults in the IDEs.
        for vault_dir in get_vault_paths(filter=args["vault"]):
            for ide in ides:
                ide.open_vault(vault_dir=vault_dir)
        return 0

    @staticmethod
    def _process_stat(args: dict[str, Any]) -> int:
        """Show vaults' statistics."""
        for vault_dir in get_vault_paths(filter=args["vault"]):
            print(f"{vault_dir.name} statistics:")

            # Getting directory size
            vault_dir_size = sum(file.stat().st_size for file in vault_dir.rglob("*"))
            vault_dir_size_mb = vault_dir_size / 1024 / 1024
            print(f"\t{round(vault_dir_size_mb, 1)} MB = {vault_dir_size} B")

            print()
        return 0
