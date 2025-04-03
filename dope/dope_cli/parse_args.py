"""Contains functionality related to parsing command line arguments."""

import argparse
import logging
from typing import Any

from dope.config import get_vault_paths
from dope.dope_cli.pomodoro import Pomodoro

_logger = logging.getLogger(__name__)


def parse_args() -> dict[str, Any]:
    """Parse and check command line arguments."""
    prsr = argparse.ArgumentParser(
        description="""Command-line interface to all vaults.""")

    #
    # Common:
    #
    prsr.add_argument(
        "-v", "--vault", dest="vault",
        nargs="*",  # The result is None | list[str].
        action="store",
        help=("Optional vault filter. If omitted, all vaults are used. "
              "If provided as a list of tokens, only those vaults are used "
              "whose names include these tokens."))
    prsr.add_argument(
        "-d", "--debug", dest="debug",
        action="store_true",
        help="Show all diagnostic messages.")

    #
    # Task related:
    #
    prsr.add_argument(
        "-x", dest="tasks_next",
        action="store_true",
        help="Show next tasks.")
    prsr.add_argument(
        "-w", dest="tasks_wait",
        action="store_true",
        help="Show pending tasks.")
    prsr.add_argument(
        "-n", dest="tasks_now",
        action="store_true",
        help="Show current tasks.")
    prsr.add_argument(
        "-t", dest="tasks_all",
        action="store_true",
        help="Show all tasks.")
    prsr.add_argument(
        "-p", "--priorities", dest="priorities",
        nargs="+", default=["123"],
        action="store",
        help=("List of priorities (1=urgent/very important, 2=moderate importance, "
              "3=not important). \"12\" means both \"1\" and \"2\'."))

    #
    # Vaults related:
    #
    prsr.add_argument(
        "--config-vault-add", dest="config_vault_add",
        nargs="+",
        action="store",
        help=("Add given vault directories to the configuration."))
    prsr.add_argument(
        "--config-vault-list", dest="config_vault_list",
        action="store_true",
        help=("List vault directories."))
    prsr.add_argument(
        "--config-vault-drop", dest="config_vault_drop",
        nargs="+",
        action="store",
        help=("Remove given vault directory from the configuration."))
    prsr.add_argument(
        "-i", "--ide", dest="ide",
        nargs="*",  # The result is None or a list.
        action="store",
        help=("Open the vaults in IDE. Supported parameters are `code` and `subl`. "
              "If none parameters provided, all IDEs will be opened."))
    prsr.add_argument(
        "-r", "--rover",
        dest="rover",
        choices=["dry", "wet"],  # The result is None or "dry" or "wet".
        action="store",
        help="Synchronize with my smartphone; parameters are `dry` or `wet`.")
    prsr.add_argument(
        "--test", dest="test",
        action="store_true",
        help="Run all tests.")
    prsr.add_argument(
        "--stat", dest="stat",
        action="store_true",
        help="Show vault statistics.")

    #
    # Education related:
    #
    prsr.add_argument(
        "-e", "--edu", dest="edu",
        action="store_true",
        help="List all education tasks: lessons and quizzes.")

    Pomodoro().add_arguments(parser=prsr)

    args = prsr.parse_args().__dict__

    # Sanity check
    vault_filter: None | list[str] = args["vault"]
    assert (
        vault_filter is None
        or (isinstance(vault_filter, list)
            and len(vault_filter) > 0
            and all(isinstance(v, str) for v in vault_filter))
    ), (f"Error in the vault filter ({vault_filter}). "
        "Either omit it or provide a non-empty list of tokens.")
    if vault_filter is not None:
        empty = True
        vault_names = [v_dir.name for v_dir in get_vault_paths()]
        for token in vault_filter:
            if any(token in vault_name for vault_name in vault_names):
                empty = False
        assert not empty, (
            f"Error in the vault filter ({vault_filter}). No such vaults found in ({vault_names}).")

    return args
