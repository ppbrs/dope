"""
Parsing jcli command line arguments.
"""

import argparse
from dataclasses import dataclass
import sys
from typing import Any


def jcli_parse_args() -> dict[str, Any]:
    """
    Parse and check command line arguments.
    """
    prsr = argparse.ArgumentParser(
        description="""Command-line interface to Joplin.""")

    #
    # General:
    #
    prsr.add_argument("-j", "--start-joplin", dest="start_joplin",
                      action="store_true",
                      help="Open Joplin.")

    #
    # Resource related:
    #
    prsr.add_argument("-v", "--view-resource", dest="view_resource", type=str, default=None,
                      action="store",
                      help="Open the resource by its unique ID for viewing. Only the beginning of the ID is necessary.")
    prsr.add_argument("-e", "--edit-resource", dest="edit_resource", type=str, default=None,
                      action="store",
                      help="Open the resource by its unique ID for editing. Only the beginning of the ID is necessary.")
    prsr.add_argument("-i", "--info-resource", dest="info_resource", type=str, default=None,
                      action="store",
                      help="Print the properties of the resource by its unique ID. Only the beginning of the ID is necessary.")
    # todo: interactive resource opener.

    #
    # Task related:
    #
    prsr.add_argument("--nxt", dest="tasks_next",
                      action="store_true",
                      help="Show next actions.")
    prsr.add_argument("--w8", dest="tasks_wait",
                      action="store_true",
                      help="Show pending actions.")
    prsr.add_argument("--now", dest="tasks_now",
                      action="store_true",
                      help="Show current actions.")
    prsr.add_argument("-t", dest="tasks_all",
                      action="store_true",
                      help="Show all tasks.")

    prsr.add_argument("-p", "--priorities", dest="priorities", nargs="+",
                      action="store",
                      help="List of priorities (1=urgent/very important, 2=moderate importance, 3=not important).")

    prsr.add_argument("-l", "--limit", dest="limit", nargs="?", type=int,
                      action="store", help="Number of tasks to show at once.")

    prsr.add_argument("-f", "--filter-or", dest="fltr_or", nargs="*",
                      action="store", help="OR-filter title actions.")

    prsr.add_argument("-#", dest="free_task_indices",
                      action="store_true",
                      help="Suggest the next task indices that are not in use.")

    return prsr.parse_args().__dict__


def test_jcli_parse_args() -> None:
    """
    Check that command line arguments are parsed correctly.
    """

    # todo: this test is not run when pytest is envoked from the root directory of the project.
    argv_saved = sys.argv  # save sys.argv

    @dataclass
    class TestCase:
        """ Store test inputs and outputs. """
        args: list[str]  # Arguments without the first one.
        res: dict[str, Any]

    test_cases = [
        TestCase(args=["-p", "1", "2"],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=False, tasks_wait=False, tasks_now=False, tasks_all=False,
                          limit=None,
                          fltr_or=None,
                          priorities=["1", "2"])),

        TestCase(args=["-#", ],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=True,
                          tasks_next=False, tasks_wait=False, tasks_now=False, tasks_all=False,
                          limit=None,
                          fltr_or=None,
                          priorities=None)),

        TestCase(args=["-f", "ham", "eggs"],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=False, tasks_wait=False, tasks_now=False, tasks_all=False,
                          limit=None,
                          fltr_or=["ham", "eggs"],
                          priorities=None)),

        TestCase(args=["--nxt", ],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=True, tasks_wait=False, tasks_now=False, tasks_all=False,
                          limit=None,
                          fltr_or=None,
                          priorities=None)),

        TestCase(args=["--w8", ],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=False, tasks_wait=True, tasks_now=False, tasks_all=False,
                          limit=None,
                          fltr_or=None,
                          priorities=None)),

        TestCase(args=["--now", ],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=False, tasks_wait=False, tasks_now=True, tasks_all=False,
                          limit=None,
                          fltr_or=None,
                          priorities=None)),

        TestCase(args=["-t", ],
                 res=dict(start_joplin=False,
                          view_resource=None, info_resource=None, edit_resource=None,
                          free_task_indices=False,
                          tasks_next=False, tasks_wait=False, tasks_now=False, tasks_all=True,
                          limit=None,
                          fltr_or=None,
                          priorities=None)),

    ]

    for i, test_case in enumerate(test_cases):
        sys.argv = ["jcli"] + test_case.args
        res = jcli_parse_args()  # pylint: disable=protected-access
        # logger.warning(f"result =           {res=}")
        # logger.warning(f"expect = {test_case.res=}")
        assert not set(res) - set(test_case.res), \
            f"Test case #{i}: Missing keys in parse result: {set(res) - set(test_case.res)}"
        assert not set(test_case.res) - set(res), \
            f"Test case #{i}: Extra keys in parse result: {set(test_case.res) - set(res)}"

        check_ok = all(test_case.res[k] == v for k, v in res.items())
        if not check_ok:
            for k, v in res.items():
                assert test_case.res.get(k) == v, \
                    f"Test case #{i}: Got {k}={v}, expected {test_case.res.get(k)}"

    sys.argv = argv_saved  # restore sys.argv
