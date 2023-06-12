"""
Executing miscellaneous user requests.
"""

# Standard library imports
import re
from typing import Any
# Third party imports
# Local application/library imports
import common
from jcli_common import Tty


class JCliHelpers:
    """
    Executing user's requests related to miscellaneous helpers.
    """
    # pylint: disable=too-few-public-methods

    PTRN_TITLE_TASK = re.compile(r"(\d\d\d\d):\s.*")
    """ Regex pattern for the titles of task notes. """

    WARNING_STR = Tty.RED + Tty.BOLD + "WARNING:" + Tty.END

    def __init__(self) -> None:
        self.ret_val = 0

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to resources.
        """
        if args["free_task_indices"]:
            self._print_task_index()

        return self.ret_val

    def _print_task_index(self) -> None:
        # Collect the indices:
        idx_set = set()
        idx_cnt = 0
        for title in [jnote.title for jnote in common.get_db_local_notes().values()]:
            if (mtch := self.PTRN_TITLE_TASK.match(title)):
                idx = int(mtch.groups()[0])
                idx_cnt += 1
                if idx in idx_set:
                    print(f"{self.WARNING_STR} Index {idx} is used more than once.")
                else:
                    idx_set.add(int(mtch.groups()[0]))

        # Report the number of indices:
        if idx_cnt:
            print(f"There are {idx_cnt} indices used.")
        else:
            print("None indices used, ")

        # Suggest next indices:
        idx_next = []
        res_cnt = 5
        for i in range(0, 10000):
            if i not in idx_set:
                idx_next.append(i)
        idx_next_str_active = ", ".join(f"{idx:04d}" for idx in idx_next[:res_cnt])
        idx_next_str_archived = ", ".join(f"{idx:04d}" for idx in idx_next[-res_cnt:])
        print(f"Next 5 available ACTIVE task indices:   {idx_next_str_active}.")
        print(f"Next 5 available ARCHIVED task indices: {idx_next_str_archived}.")
