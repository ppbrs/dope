"""
Executing user requests related to synchronizing vaults with my smartphone.
"""
import logging
import os
import subprocess as sp
from pathlib import PosixPath
from typing import Any

from dope.config import get_vault_paths
from dope.term import Term

_logger = logging.getLogger(__name__)


class RoverSync:
    """A namespace for functions that perform synchronization of files between the local vault
    (the Base) and my smartphone (the Rover)."""
    # pylint: disable=too-few-public-methods

    @classmethod
    def process(
        cls,
        args: dict[str, Any]
    ) -> int:
        """
        Executing user's requests related to synchronizing vaults with my smartphone.
        """
        if args["rover"] is None:
            return 0

        rover_path = cls._find_rover_path()
        if rover_path is None:
            return -1

        vault_dirs = get_vault_paths(filter=args["vault"])
        _logger.info("VAULTs: %s.", ", ".join(v.name for v in vault_dirs))

        for bvdir in vault_dirs:
            vault_name = bvdir.name
            rvdir = rover_path / vault_name
            if not rvdir.exists():
                print(f"`{vault_name}` is not on rover, do you want to create it?")
                if cls._input_yes_no(default=False):
                    cmd = f"gio mkdir -p '{rvdir}'"
                    cls._run_command(cmd=cmd, silent=True)
                else:
                    continue

            print(f"{vault_name}: Walking through BASE.")
            bfiles, bdirs = cls._get_files_dirs(bvdir)
            _logger.debug("%d files / %d directories on `%s` BASE.",
                          len(bfiles), len(bdirs), vault_name)

            print(f"{vault_name}: Walking through ROVER.")
            rfiles, rdirs = cls._get_files_dirs(rvdir)
            _logger.debug("%d files / %d directories on `%s` ROVER.",
                          len(rfiles), len(rdirs), vault_name)

            cls._process_dirs(args=args, rvdir=rvdir, rdirs=rdirs, bdirs=bdirs)
            cls._process_files(args=args, rvdir=rvdir, bvdir=bvdir, rfiles=rfiles, bfiles=bfiles)
        return 0

    @classmethod
    def _process_dirs(
        cls,
        args: dict[str, Any],
        rvdir: PosixPath,
        rdirs: set[PosixPath],
        bdirs: set[PosixPath]
    ) -> None:
        dir_diff_rb = rdirs - bdirs
        if not dir_diff_rb:
            print(f"{rvdir.name}: No directories on ROVER that can be removed.")
            return
        for dir_name in sorted(dir_diff_rb):
            if not (rvdir / dir_name).exists():
                # The directory may have already been deleted.
                continue
            msg = "Directory " + Term.bold(str(dir_name)) + " is on ROVER but not on BASE."
            print(msg)
            if args["rover"] == "wet":
                print("\tRemove from ROVER?")
                if cls._input_yes_no(default=False):
                    abs_path = rvdir / dir_name
                    cmd = f"rm -r '{abs_path}'"
                    res = cls._run_command(cmd=cmd, silent=False)
                    if res:
                        print("\tDone.")

    @classmethod
    def _process_files(  # pylint: disable=too-many-arguments
        cls,
        args: dict[str, Any],
        rvdir: PosixPath,
        bvdir: PosixPath,
        rfiles: set[PosixPath],
        bfiles: set[PosixPath]
    ) -> None:
        fdiff_rb = rfiles - bfiles  # Files on the Rover but not on the Base.
        if not fdiff_rb:
            print(f"{rvdir.name}: No files on ROVER that can be removed.")
        for fname in sorted(fdiff_rb):
            if not (rvdir / fname).exists():
                # The file may have already been deleted.
                continue
            print()
            msg = f"File {bvdir.name}/{Term.bold(str(fname))} is on ROVER but not on BASE."
            print(msg)
            if args["rover"] == "wet":
                cls._remove_from_rover(rvdir=rvdir, fname=fname)

        fdiff_br = sorted(bfiles - rfiles)
        if not fdiff_br:
            print(f"{rvdir.name}: No files on BASE that can be copied to ROVER.")
        for i, fname in enumerate(fdiff_br, start=1):
            if not (bvdir / fname).exists():
                # The file may have already been deleted.
                continue
            print()
            msg = (f"{i}/{len(fdiff_br)}: "
                   f"File {bvdir.name}/{Term.bold(str(fname))} is on BASE but not on ROVER.")
            print(msg)
            if args["rover"] == "wet":
                cls._copy_to_rover(rvdir=rvdir, bvdir=bvdir, fname=fname)

    @classmethod
    def _remove_from_rover(
        cls,
        rvdir: PosixPath,
        fname: PosixPath,
    ) -> None:
        print("\tRemove from ROVER? ", end="")
        if cls._input_yes_no(default=False):
            abs_path = rvdir / fname
            cmd = f"rm '{abs_path}'"
            res = cls._run_command(cmd=cmd, silent=False)
            if res:
                print("\tDone.")

    @classmethod
    def _copy_to_rover(
        cls,
        rvdir: PosixPath,
        bvdir: PosixPath,
        fname: PosixPath,
    ) -> None:
        src_fpath = bvdir / fname
        assert "*" not in str(src_fpath)
        assert "?" not in str(src_fpath)
        assert "\"" not in str(src_fpath)
        assert "'" not in str(src_fpath)

        dst_dpath = (rvdir / fname).parent
        assert "*" not in str(dst_dpath)
        assert "?" not in str(dst_dpath)
        assert "\"" not in str(dst_dpath)
        assert "'" not in str(dst_dpath)

        print(f"\tCopy to ROVER? ({cls._get_file_size_string(src_fpath)})", end="")
        if cls._input_yes_no(default=True):

            cmd = f"gio mkdir -p '{dst_dpath}'"
            cls._run_command(cmd=cmd, silent=True)

            cmd = f"gio copy '{src_fpath}' '{dst_dpath}'"
            res_copy = cls._run_command(cmd=cmd, silent=False)
            if res_copy:
                print("\tDone.")

    @classmethod
    def _get_files_dirs(
        cls,
        vdir: PosixPath
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
    def _run_command(
        cls,
        cmd: str,
        silent: bool
    ) -> bool:
        _logger.debug("$ %s", cmd)

        with sp.Popen(args=[cmd, ], stdout=sp.PIPE, stderr=sp.PIPE, shell=True) as child:
            outs_b, errs_b = child.communicate()
            exit_code = child.wait()
        outs = outs_b.decode(encoding="ascii", errors="ignore").split("\n")
        errs = errs_b.decode(encoding="ascii", errors="ignore").split("\n")
        for out in outs:
            if out:
                _logger.debug("stdout: %s", out)
                if not silent:
                    print(f"\tstdout: {out}")
        if exit_code != 0:
            _logger.debug("tFAILED, exit code = %d", exit_code)
            if not silent:
                print(f"\t$ {cmd}")
                print(f"\tFAILED, exit code = {exit_code}")
        for err in errs:
            if err:
                _logger.debug("stderr: %s", err)
                if not silent:
                    print(f"\tstderr: {err}")
        return exit_code == 0

    @classmethod
    def _input_yes_no(
        cls,
        default: bool,
    ) -> bool:
        """
        Empty means No.
        """
        choise = "Y/n" if default else "y/N"
        print(f"\t{choise}: ", end="")
        while True:
            user_input = input()
            if user_input in ["n", "N"]:
                return False
            if user_input in ["y", "Y"]:
                return True
            if user_input == "":
                print("y" if default else "n")
                return default
            print(f"\tTry again, {choise}: ", end="")

    @classmethod
    def _find_rover_path_one_level(
        cls,
        path: PosixPath,
        glob: str,
        level_name: str,
    ) -> PosixPath | None:
        """Let user choose one directory level when looking for ROVER path."""
        while True:
            print()
            dirs = list(path.glob(glob))
            if not dirs:
                print(f"None {level_name} mounted.")
                return None

            print(f"Mounted {level_name}:")
            for i, dir1 in enumerate(dirs, start=1):
                print(f"\t{i}: {Term.bold(dir1.name)}")
            print("Choose one by pressing its number: ", end="")
            try:
                user_input = int(input())
            except ValueError:
                user_input = 0
            if user_input in range(1, len(dirs) + 1):
                break
        return dirs[user_input - 1]

    @classmethod
    def _find_rover_path(cls) -> PosixPath | None:
        """Interactively select rover path.

        This function doesn't create any files or directories.

        Rover file system is expected to be mounted in
        /run/user/<user>/gvfs/<mtp>/<storage-type>/vaults
        """
        mtp_dir = cls._find_rover_path_one_level(
            path=PosixPath(f"/run/user/{os.getuid()}/gvfs/"),
            glob="mtp:*", level_name="MTP filesystems")
        if mtp_dir is None:
            return None
        print(f"'{mtp_dir.name}' chosen")

        storage_dir = cls._find_rover_path_one_level(
            path=mtp_dir, glob="*", level_name="storage directories")
        if storage_dir is None:
            return None
        print(f"'{mtp_dir.name} / {storage_dir.name}' was chosen.")
        print()

        rover_dir = storage_dir / "vaults"
        if rover_dir.exists() and rover_dir.is_dir():
            return PosixPath(rover_dir)

        print("'vaults' directory doesn't exist on chosen ROVER.")
        print()
        return None

    @classmethod
    def _get_file_size_string(cls, fpath: PosixPath) -> str:
        fsize_b = fpath.stat().st_size
        if fsize_b >= (1024 * 1024):
            fsize_mb = fsize_b / (1024 * 1024)
            return f"{fsize_mb:.1f}MB"
        if fsize_b >= 1024:
            fsize_kb = fsize_b / 1024
            return f"{fsize_kb:.1f}kB"
        return f"{fsize_b}B"
