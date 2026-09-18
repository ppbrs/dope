"""Contains functionality related to parsing command line arguments."""

import argparse
import logging
from typing import Any

from dope.config import get_vault_paths
from dope.dope_cli.pomodoro import Pomodoro
from dope.dope_cli.task_tracker import TaskTracker

_logger = logging.getLogger(__name__)


def parse_args() -> dict[str, Any]:
    """Parse and check command line arguments."""
    parser = argparse.ArgumentParser(description="""Command-line interface to all vaults.""")

    #
    # Common:
    #
    parser.add_argument(
        "-v",
        "--vault",
        dest="vault",
        nargs="*",  # The result is None | list[str].
        action="store",
        help=(
            "Optional vault filter. If omitted, all vaults are used. "
            "If provided as a list of tokens, only those vaults are used "
            "whose names include these tokens."
        ),
    )
    parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", help="Show all diagnostic messages."
    )

    #
    # Vaults related:
    #
    parser.add_argument(
        "-i",
        "--ide",
        dest="ide",
        nargs="*",  # The result is None or a list.
        action="store",
        help=("Open the vaults in IDE. Supported parameters: `code`. "),
    )
    parser.add_argument(
        "-r",
        "--rover",
        dest="rover",
        choices=["dry", "wet"],  # The result is None or "dry" or "wet".
        action="store",
        help="Synchronize with my smartphone; parameters are `dry` or `wet`.",
    )
    parser.add_argument(
        "--test",
        dest="test",
        action="store_true",
        help="""Run all vault tests.
        Useful parameters:
            '-x'/'--exitfirst' to stop at first failure,
            '-k keyword' to run specific test based on their names,
            '--log-level=ERROR' to reduce noise of failed tests.
        See more at https://docs.pytest.org/en/6.2.x/usage.html.
        """,
    )
    parser.add_argument("--stat", dest="stat", action="store_true", help="Show vault statistics.")
    parser.add_argument(
        "--vector",
        dest="vector",
        action="store_true",
        help="Find all descriptions of vector images and regenerate them.",
    )

    #
    # Education related:
    #
    parser.add_argument(
        "-e",
        "--edu",
        dest="edu",
        nargs="*",  # The result is None or a list.
        action="store",
        help="List all education tasks: lessons and quizzes.",
    )

    #
    # Other
    #
    parser.add_argument(
        "-cl",
        "--check-list",
        dest="check_list",
        action="store_true",
        help="Open the check-list file.",
    )
    parser.add_argument(
        "--config",
        dest="config_editor",
        nargs=1,
        action="store",
        help=("Open the config with the provided editor."),
    )

    #
    # --
    #
    parser.add_argument(
        "remainder",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the underlying tool.",
    )

    TaskTracker.add_arguments(parser=parser)
    Pomodoro.add_arguments(parser=parser)

    args = parser.parse_args().__dict__

    # Sanity check
    vault_filter: None | list[str] = args["vault"]
    assert vault_filter is None or (
        isinstance(vault_filter, list)
        and len(vault_filter) > 0
        and all(isinstance(v, str) for v in vault_filter)
    ), (
        f"Error in the vault filter ({vault_filter}). "
        "Either omit it or provide a non-empty list of tokens."
    )
    if vault_filter is not None:
        empty = True
        vault_names = [v_dir.name for v_dir in get_vault_paths()]
        for token in vault_filter:
            if any(token in vault_name for vault_name in vault_names):
                empty = False
        assert not empty, (
            f"Error in the vault filter ({vault_filter}). No such vaults found in ({vault_names})."
        )

    return args
