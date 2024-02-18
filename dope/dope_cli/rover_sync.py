"""
Executing user requests related to synchronizing vaults with my smartphone.
"""
import logging
import subprocess as sp
from pathlib import PosixPath
from typing import Any

from dope.paths import ROVER_PATH, V_DIRS
from dope.term import Term

_logger = logging.getLogger(__name__)


class RoverSync:
    """A namespace for functions that perform synchronization of files between the vault
    and my smartphone."""
    # pylint: disable=too-few-public-methods

    @classmethod
    def process(cls, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to synchronizing vaults with my smartphone.
        """
        if args["rover"] is None:
            return 0

        assert ROVER_PATH.exists() and ROVER_PATH.is_dir(), \
            "The smartphone is not mounted."

        vault_dirs = cls._get_vault_dirs(args)
        _logger.info("VAULTs: %s.", ", ".join(v.name for v in vault_dirs))
        for bvdir in vault_dirs:
            vault_name = bvdir.name
            rvdir = ROVER_PATH / vault_name
            if not rvdir.exists():
                _logger.warning("`%s` is not on rover.", vault_name)
                continue

            rfiles, rdirs = cls._get_dirs_files(rvdir)
            _logger.debug("%d files / %d directories on `%s` rover.",
                          len(rfiles), len(rdirs), vault_name)

            bfiles, bdirs = cls._get_dirs_files(bvdir)
            _logger.debug("%d files / %d directories on `%s` base.",
                          len(bfiles), len(bdirs), vault_name)

            cls._process_dirs(args=args, rvdir=rvdir, rdirs=rdirs, bdirs=bdirs)
            cls._process_files(args=args, rvdir=rvdir, bvdir=bvdir, rfiles=rfiles, bfiles=bfiles)
        return 0

    @classmethod
    def _process_dirs(
        cls, args: dict[str, Any], rvdir: PosixPath, rdirs: set[PosixPath], bdirs: set[PosixPath]
    ) -> None:
        dir_diff_rb = rdirs - bdirs
        for dir_name in sorted(dir_diff_rb):
            if not (rvdir / dir_name).exists():
                # The directory may have already been deleted.
                continue
            msg = ("Directory " + Term.bold(str(dir_name)) + " is on ROVER but not on BASE.")
            print(msg)
            if args["rover"] == "wet":
                print("\tRemove from ROVER? y/N")
                if cls._input_yes_no():
                    abs_path = rvdir / dir_name
                    res = cls._run_command(cmd=f"rm -r \"{abs_path}\"", silent=False)
                    if res:
                        print("\tDone.")
                    if not res:
                        print("\tFAILED")

    @classmethod
    def _process_files(
        cls, args: dict[str, Any], rvdir: PosixPath, bvdir: PosixPath, rfiles: set[PosixPath], bfiles: set[PosixPath]
    ) -> None:
        fdiff_rb = rfiles - bfiles
        for fname in sorted(fdiff_rb):
            if not (rvdir / fname).exists():
                # The file may have already been deleted.
                continue
            msg = "File " + Term.bold(str(fname)) + " is on ROVER but not on BASE."
            print(msg)
            if args["rover"] == "wet":
                print("\tRemove from ROVER? y/N")
                if cls._input_yes_no():
                    abs_path = rvdir / fname
                    res = cls._run_command(cmd=f"rm \"{abs_path}\"", silent=False)
                    if res:
                        print("\tDone.")
                    if not res:
                        print("\tFAILED")

        fdiff_br = bfiles - rfiles
        for fname in sorted(fdiff_br):
            if not (bvdir / fname).exists():
                # The file may have already been deleted.
                continue
            msg = "File " + Term.bold(str(fname)) + " is on BASE but not on ROVER."
            print(msg)
            if args["rover"] == "wet":
                print("\tCopy to ROVER? y/N")
                if cls._input_yes_no():
                    src_fpath = bvdir / fname
                    assert "*" not in str(src_fpath)
                    assert "?" not in str(src_fpath)
                    assert "\"" not in str(src_fpath)

                    dst_dpath = (rvdir / fname).parent
                    assert "*" not in str(dst_dpath)
                    assert "?" not in str(dst_dpath)
                    assert "\"" not in str(dst_dpath)

                    logging.debug("$ gio mkdir -p \"%s\"", dst_dpath)
                    cls._run_command(cmd=f"gio mkdir -p \"{dst_dpath}\"", silent=True)

                    logging.debug("$ gio copy \"%s\" \"%s\"", src_fpath, dst_dpath)
                    res_copy = cls._run_command(cmd=f"gio copy \"{src_fpath}\" \"{dst_dpath}\"", silent=False)
                    if res_copy:
                        print("\tDone.")
                    if not res_copy:
                        print("\tFAILED")

    @classmethod
    def _get_vault_dirs(
        cls, args: dict[str, Any]
    ) -> list[PosixPath]:
        if args["vault"] is None:
            vault_dirs = list(V_DIRS)
        else:
            vault_dirs = []
            for vault_dir in V_DIRS:
                for vault in args["vault"]:
                    if vault in vault_dir.name:
                        vault_dirs.append(vault_dir)
        return vault_dirs

    @classmethod
    def _get_dirs_files(
        cls, vdir: PosixPath
    ) -> tuple[set[PosixPath], set[PosixPath]]:
        files = set()
        dirs = set()
        for rpath in vdir.rglob("*"):
            if ".git" in rpath.parts or ".trash" in rpath.parts:
                continue
            if rpath.is_file():
                rpath = rpath.relative_to(vdir)
                files.add(rpath)
            elif rpath.is_dir():
                rpath = rpath.relative_to(vdir)
                dirs.add(rpath)
                # _logger.debug("BASE DIR: %s", rpath)
            else:
                raise ValueError
        return files, dirs

    @classmethod
    def _run_command(cls, cmd: str, silent: bool) -> bool:

        with sp.Popen(args=[cmd, ], stdout=sp.PIPE, stderr=sp.PIPE, shell=True) as child:
            outs_b, errs_b = child.communicate()
            exit_code = child.wait()
        outs = outs_b.decode(encoding="ascii", errors="ignore").split("\n")
        errs = errs_b.decode(encoding="ascii", errors="ignore").split("\n")
        if not silent:
            if exit_code != 0:
                print(f"\terror (exit code {exit_code})")
            for out in outs:
                if out != "":
                    print("\t", out)
            for err in errs:
                if err != "":
                    print("\t", err)
        return exit_code == 0

    @classmethod
    def _input_yes_no(cls) -> bool:
        """
        Empty means No
        """
        while True:
            user_input = input()
            if user_input in ["n", "N"]:
                return False
            if user_input in ["", "y", "Y"]:
                return True
