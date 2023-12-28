"""Contains functionality related to parsing command line arguments."""

import argparse
from typing import Any


def parse_args() -> dict[str, Any]:
    """Parse and check command line arguments."""
    prsr = argparse.ArgumentParser(
        description="""Command-line interface to all vaults.""")

    #
    # Task related:
    #
    prsr.add_argument("--nxt", dest="tasks_next",
                      action="store_true",
                      help="Show next tasks.")
    prsr.add_argument("--w8", dest="tasks_wait",
                      action="store_true",
                      help="Show pending tasks.")
    prsr.add_argument("--now", dest="tasks_now",
                      action="store_true",
                      help="Show current tasks.")
    prsr.add_argument("-t", dest="tasks_all",
                      action="store_true",
                      help="Show all tasks.")
    prsr.add_argument("-v", "--vault", dest="vault", nargs=1,
                      action="store", help="Vault filter.")

    return prsr.parse_args().__dict__
