"""
dope_cli submodule
"""
import logging
import os
import sys

from dope.dope_cli.parse_args import parse_args
from dope.dope_cli.task_tracker import DopeCliTaskTracker


def dope_cli() -> int:
    """Process all user requests."""

    fmt = "%(asctime)s.%(msecs)03d %(levelname)-8s %(funcName)s: %(message)s"
    datefmt = "%Y%m%d:%H%M%S"
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=datefmt)
    _logger = logging.getLogger(__name__)

    if not sys.stdin.isatty():
        _logger.fatal("Input doesn't come from tty.")
        raise SystemExit

    os.system("clear")

    args = parse_args()
    _logger.debug("Raw arguments: %s", args)

    ret_val: int = DopeCliTaskTracker().process(args=args)

    return ret_val
