"""
dope_cli submodule
"""
import logging
import os
import pathlib
import sys
from pprint import pformat

from dope.config import get_config
from dope.config import get_vault_paths
from dope.dope_cli.check_list import process_check_list
from dope.dope_cli.config import process_arguments
from dope.dope_cli.edu_tracker import EduTracker
from dope.dope_cli.parse_args import parse_args
from dope.dope_cli.pomodoro import Pomodoro
from dope.dope_cli.rover_sync import RoverSync
from dope.dope_cli.task_tracker import TaskTracker
from dope.dope_cli.vault_utils import VaultUtils
from dope.dope_cli.vector import Vector


def dope_cli() -> int:
    """Process all user requests."""

    try:
        fmt = "%(asctime)s.%(msecs)03d %(levelname)-8s %(funcName)s: %(message)s"
        datefmt = "%H%M%S"
        logging.basicConfig(level=logging.WARNING, format=fmt, datefmt=datefmt)
        _logger = logging.getLogger(__name__)

        if not sys.stdin.isatty():
            _logger.fatal("Input doesn't come from tty.")
            raise SystemExit

        os.system("clear")

        args = parse_args()
        if args["debug"]:
            _logger.setLevel(logging.DEBUG)

        _logger.info("Raw arguments: %s", args)

        _logger.info("Package directory: %s", pathlib.PosixPath(__file__).parent)

        # Report configuration.
        _logger.info("Configuration:")
        for line in pformat(get_config()).split("\n"):
            _logger.info(line)
        if get_vault_paths():
            _logger.info(
                "Configured vaults (%d): %s.",
                len(get_vault_paths()), ", ".join(f"'{v}'" for v in get_vault_paths()))
        else:
            _logger.warning("No vaults configured.")

        ret_val: int = TaskTracker().process(args=args)
        ret_val += EduTracker().process(args=args)
        ret_val += VaultUtils().process(args=args)
        ret_val += Pomodoro.process(args=args)
        ret_val += RoverSync.process(args=args)
        ret_val += Vector.process(args=args)
        ret_val += process_arguments(args=args)
        ret_val += process_check_list(args=args)

        if args["test"]:
            dope_root_dir = pathlib.PosixPath(__file__).parent.parent.parent
            os.system(f"cd {dope_root_dir} && pytest")

        return ret_val
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        return 1
