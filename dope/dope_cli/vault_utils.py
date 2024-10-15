"""
Executing user requests related to vaults.
"""
from __future__ import annotations

import enum
import logging
import os
import pathlib
import time
from typing import Any

import psutil

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
    def filter_vault_dirs(cls, args: dict[str, Any]) -> list[pathlib.PosixPath]:
        """
        Parse the --vault argument and collect the requested vaults.
        """
        vault_filter: None | list[str] = args["vault"]
        if vault_filter is None:
            return list(V_DIRS)
        vault_dirs = []
        for vault_dir in V_DIRS:
            for vault_substr in vault_filter:
                if vault_substr in vault_dir.name:
                    vault_dirs.append(vault_dir)
        return vault_dirs

    @classmethod
    def process(cls, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to vaults.
        """
        cls._check_dropbox_daemon()
        ret_val = 0
        if args["ide"] is not None:
            ret_val = cls._process_ide(args=args)
        if args["stat"]:
            ret_val += cls._process_stat(args=args)
        return ret_val

    @classmethod
    def _process_ide(cls, args: dict[str, Any]) -> int:
        """
        --ide/-i option opens vaults with specified IDEs.
        """
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
        vault_dirs = cls.filter_vault_dirs(args=args)

        # Open the vaults in the IDEs.
        for vault_dir in vault_dirs:
            for ide in ides:
                ide.open_vault(vault_dir=vault_dir)
        return 0

    @classmethod
    def _check_dropbox_daemon(cls) -> None:
        """Regardless of User arguments, check that Dropbox daemon is running."""

        for proc in psutil.process_iter():
            try:
                name = proc.name()
                if name == "dropbox":
                    create_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(proc.create_time()))
                    _logger.info(
                        "Dropbox daemon: PID=%d, status=%s, created %s, cmd='%s'.",
                        proc.pid, proc.status(), create_time, " ".join(proc.cmdline()))
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        else:
            raise ValueError("Dropbox daemon is not running")

    @classmethod
    def _process_stat(cls, args: dict[str, Any]) -> int:
        """Show vaults' statistics."""
        for vault_dir in cls.filter_vault_dirs(args=args):
            print(f"{vault_dir.name} statistics:")

            # Getting directory size
            vault_dir_size = sum(file.stat().st_size for file in vault_dir.rglob('*'))
            vault_dir_size_mb = vault_dir_size / 1024 / 1024
            print(f"\t{round(vault_dir_size_mb, 1)} MB = {vault_dir_size} B")

            print()
        return 0


def test_vault_utils_filter_vault_dirs() -> None:
    """Check VaultUtils().filter_vault_dirs method."""
    assert VaultUtils().filter_vault_dirs(args={"vault": None}) == V_DIRS
    assert VaultUtils().filter_vault_dirs(args={"vault": ["z"]}) == [
        pathlib.PosixPath("~/projects/z").expanduser()]
    assert VaultUtils().filter_vault_dirs(args={"vault": ["v"]}) == [
        pathlib.PosixPath("~/Dropbox/the-vault").expanduser()]
    assert VaultUtils().filter_vault_dirs(args={"vault": ["z", "f"]}) == [
        pathlib.PosixPath("~/projects/z").expanduser(),
        pathlib.PosixPath("~/Dropbox/projects/fl").expanduser()]
