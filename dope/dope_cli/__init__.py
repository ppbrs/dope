"""
dope_cli submodule
"""
import logging
import os
import pathlib
import sys

from dope.dope_cli.edu_tracker import EduTracker
from dope.dope_cli.parse_args import parse_args
from dope.dope_cli.task_tracker import TaskTracker
from dope.dope_cli.vault_utils import VaultUtils


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

        _logger.info("Package directory: %s", pathlib.PosixPath(__file__).parent)

        ret_val: int = TaskTracker().process(args=args)
        ret_val += EduTracker().process(args=args)
        ret_val += VaultUtils().process(args=args)

        if args["test"]:
            dope_root_dir = pathlib.PosixPath(__file__).parent.parent.parent
            os.system(f"cd {dope_root_dir} && pytest")

        return ret_val
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        return 1
