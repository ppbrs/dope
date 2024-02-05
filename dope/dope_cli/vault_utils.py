"""
Executing user requests related to vaults.
"""
from __future__ import annotations

import enum
import logging
import os
import pathlib
from typing import Any

from dope.paths import OBSIDIAN_APP_PATH, V_DIRS

_logger = logging.getLogger(__name__)


@enum.unique
class Ide(enum.Enum):
    """Enum for all supported IDEs."""
    SUBLIME_TEXT = enum.auto()
    VSCODE = enum.auto()
    OBSIDIAN = enum.auto()

    @classmethod
    def from_arg(cls, arg: str) -> Ide:
        """Parse user argument for an IDE to one of supported IDEs."""
        match arg:
            case "subl":
                return Ide.SUBLIME_TEXT
            case "code":
                return Ide.VSCODE
            case "obs":
                return Ide.OBSIDIAN
            case _:
                raise ValueError(f"Unknown IDE: {arg}.")

    def open_vault(self, vault_dir: pathlib.PosixPath) -> None:
        """Open a vault is this IDE."""
        match self:
            case Ide.VSCODE:
                code_dir = vault_dir / ".vscode"
                if code_dir.exists() and code_dir.is_dir():
                    os.system(f"cd {vault_dir} && code .")
                else:
                    _logger.error("Cannot open `%s` in `VS Code`.", vault_dir.name)
            case Ide.SUBLIME_TEXT:
                subl_prj = (vault_dir / vault_dir.name).with_suffix(".sublime-project")
                if subl_prj.exists() and subl_prj.is_file():
                    os.system(f"subl {subl_prj}")
                else:
                    _logger.error("Cannot open `%s` in `Sublime Text`.", vault_dir.name)
            case Ide.OBSIDIAN:
                _logger.warning("Opening a vault in Obsidian is not implemented yet.")
                os.system(f"{OBSIDIAN_APP_PATH} >/dev/null 2>&1 & disown")


class VaultUtils:
    """An object of this class has everything that is needed to manage vaults."""
    # pylint: disable=too-few-public-methods

    @classmethod
    def _filter_vault_dirs(cls, vaults: list[str] | None) -> list[pathlib.PosixPath]:
        """
        Parse the --vault argument and collect the requested vaults.
        """
        vault_dirs = []
        for vault_dir in V_DIRS:
            if vaults is None:
                vault_dirs.append(vault_dir)
            else:
                for vault in vaults:
                    if vault in vault_dir.name:
                        vault_dirs.append(vault_dir)
        _logger.info("VAULTs: %s.", ", ".join(v.name for v in vault_dirs))
        return vault_dirs

    @classmethod
    def process(cls, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to vaults.
        """
        # Find out which IDEs will be used.
        if args["ide"] is None:
            return 0
        ides_known = set(Ide)
        if args["ide"] == []:
            ides = ides_known
        else:
            ides = set()
            for arg in args["ide"]:
                ides.add(Ide.from_arg(arg))
        # ides_unknown = ides - ides_known
        # if ides_unknown:
        #     _logger.error("Unknown IDEs: %s.", ", ".join(list(ides_unknown)))
        # ides = ides & ides_known
        if not ides:
            _logger.error("No known IDEs provided.")
            return 1
        _logger.info("IDEs: %s", ides)
        _logger.info("IDEs: %s.", ", ".join(str(ide) for ide in ides))

        # Find out which vaults will be opened.
        vault_dirs = cls._filter_vault_dirs(args["vault"])

        # Open the vaults in the IDEs.
        for vault_dir in vault_dirs:
            for ide in ides:
                ide.open_vault(vault_dir=vault_dir)

        return 0
