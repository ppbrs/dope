"""Utilities to manipulate Git repositories."""

import argparse
import json
import logging
import pathlib
import subprocess
from datetime import date
from typing import Any

from dope.config import get_config


class _DirtyJupyterNotebook(Exception):
    """Cannot commit."""


class GitHelper:
    """
    Git utilities.
    """

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add arguments to the provided argument parser.

        This method is expected to run before parser.parse_args() is invoked.
        """
        parser.add_argument(
            "-g",
            "--git-commit-daily",
            dest="git_commit_daily",
            action="store_true",
            help=(
                "Create a daily git commit - with message YYYY-MM-DD. "
                "Only works in configured directories."
            ),
        )

    @staticmethod
    def process(args: dict[str, Any]) -> int:
        """
        Executing user's requests related to Git version control.
        """
        if not args["git_commit_daily"]:
            return 0

        logger = logging.getLogger(__name__)

        config = get_config()
        daily_repos = config.get("git-commit-daily-repos", None)
        if daily_repos is None:
            raise ValueError("'git-commit-daily-repos' not found in configuration.")
        if not isinstance(daily_repos, list) or not any(isinstance(r, str) for r in daily_repos):
            raise TypeError("'git-commit-daily-repos' is not a list of paths.")

        daily_repos = [pathlib.PosixPath(p).expanduser().absolute() for p in daily_repos]
        logger.info("git-commit-daily-repos: %s", daily_repos)

        cwd = pathlib.Path.cwd()
        if cwd not in daily_repos:
            raise ValueError("Your directory is not configured to support -g/--git-commit-daily.")

        print("CLEANING UP Jupyter notebooks.")
        for file_path in cwd.rglob("*.ipynb"):
            try:
                GitHelper._clean_up_ipynb(file_path=file_path)
            except _DirtyJupyterNotebook:
                print("EXITING\n")
                return 0
        print()

        print("ADDING files to staging area.")
        _ = GitHelper._run_git_command(args=["add", ".", "-v"])
        print()

        print("STATUS")
        lines_status = GitHelper._run_git_command(args=["status", "-u", "--short"])
        for line in lines_status:
            print(f"\t{line}")
        print()
        if not lines_status:
            print("Nothing in staging area, EXITING.\n")
            return 1

        actual_commit_log = date.today().isoformat()
        print(f"ACTUAL COMMIT: {actual_commit_log}")
        print()

        lines_latest_commit = GitHelper._run_git_command(args=["show", "-s", "--format=%s"])
        assert len(lines_latest_commit) == 1
        latest_commit_log = lines_latest_commit[0]
        print(f"LATEST COMMIT: {latest_commit_log}")
        print()

        if latest_commit_log == actual_commit_log:
            print(f"AMENDING '{actual_commit_log}'")
            _ = GitHelper._run_git_command(args=["commit", "--amend", "--no-edit"])
        else:
            print(f"COMMITTING '{actual_commit_log}'")
            _ = GitHelper._run_git_command(args=["commit", "-m", actual_commit_log, "-v"])
        print()

        print("FETCHING")
        _ = GitHelper._run_git_command(args=["fetch"])
        lines_status = GitHelper._run_git_command(args=["status", "--branch", "--short"])
        for line in lines_status:
            print(f"\t{line}")
        print()

        print("PUSHING")
        for line in GitHelper._run_git_command(args=["push", "--force"]):
            print(f"\t{line}")
        print()

        print("CLEANING_UP")
        _ = GitHelper._run_git_command(args=["gc"])
        print()

        print("EXITING\n")
        return 1

    @staticmethod
    def _run_git_command(args: list[str]) -> list[str]:
        logger = logging.getLogger(__name__)
        logger.debug("git args: %s", args)
        proc: subprocess.CompletedProcess[str] = subprocess.run(
            ["/usr/bin/git", *args],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        lines = [x.strip() for x in proc.stdout.splitlines()]
        for line in lines:
            line_ = line.strip()
            if line_:
                logger.info("%s", line_)
        logger.info("%s", "----------------")
        proc.check_returncode()
        return lines

    @staticmethod
    def _clean_up_ipynb(file_path: pathlib.Path) -> None:
        """Remove run-time data from a Jupyter Notebook file."""
        file_path_rel = file_path.relative_to(pathlib.PosixPath.cwd())
        print(f"\tChecking '{file_path_rel}'.")

        assert file_path.exists()
        assert file_path.is_file()
        assert file_path.suffix == ".ipynb"
        logger = logging.getLogger(__name__)
        logger.info("Looking into '%s'", file_path)
        with file_path.open("rb") as fp:
            data = json.load(fp=fp)
        file_changed = False
        assert "cells" in data
        for i, cell in enumerate(data["cells"]):
            if "execution_count" in cell and cell["execution_count"] is not None:
                data["cells"][i]["execution_count"] = None
                file_changed = True
            if "outputs" in cell:
                assert isinstance(cell["outputs"], list)
                if cell["outputs"]:
                    data["cells"][i]["outputs"] = []
                    file_changed = True

        if file_changed:
            print(f"\t\t'{file_path_rel}' needs cleaning, proceed? [y/N]")
            if input() in ("y", "Y"):
                with file_path.open("w", encoding="utf-8") as fp:
                    json.dump(obj=data, fp=fp, indent=2)
                print("\t\t\tDone.")
            else:
                print("\t\t\tSkipped.")
                raise _DirtyJupyterNotebook
        else:
            print("\t\tClean.")
        return
