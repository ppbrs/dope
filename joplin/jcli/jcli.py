#!/usr/bin/python3
""" Joplin Command Line Interface tool. """

# Standard library imports
import os
import sys
# Third party imports
# Local application/library imports
from jcli_parse_args import jcli_parse_args
from jcli_resources import JCliResources
from jcli_start import JCliStart
from jcli_tasks import JCliTasks
from jcli_tasks_sanity import JCliTasksSanity
from jcli_helpers import JCliHelpers


class JCli:
    """
    The class that does all the work when instantiated.
    """

    def __init__(self, testing: bool = False) -> None:
        if testing:
            return  # This is for creating a testing instance of JCli.

        if not sys.stdin.isatty():
            print("Input doesn't come from tty.")
            raise SystemExit

        self.ret_val = 0
        self.args = jcli_parse_args()

    def process(self) -> int:
        """
        Process all user requests.
        """
        os.system("clear")
        self.ret_val = JCliResources().process(args=self.args)
        self.ret_val = JCliStart().process(args=self.args)
        self.ret_val = JCliTasks().process(args=self.args)
        self.ret_val = JCliTasksSanity().process(args=self.args)
        self.ret_val = JCliHelpers().process(args=self.args)
        return self.ret_val


if __name__ == "__main__":
    sys.exit(JCli(testing=False).process())
