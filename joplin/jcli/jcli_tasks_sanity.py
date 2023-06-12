"""
Chaecking tasks sanity when user send requests related to tasks.
"""
# Standard library imports
from typing import Any
# Third party imports
# Local application/library imports
import common
from jtask import JNext, JWait, JNow
from jcli_helpers import JCliHelpers
from jcli_common import Tty, collect_tasks


class JCliTasksSanity:
    """ An object of this class holds the list of collected tasks
    and has functions for checking tasks sanity. """

    def __init__(self) -> None:
        self.ret_val = 0
        self.no_warnings = True
        self.warning_str = Tty.RED + Tty.BOLD + "WARNING:" + Tty.END

        self.jtasks = collect_tasks()

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to tasks.
        """
        if not any((args["tasks_next"], args["tasks_wait"], args["tasks_now"], args["tasks_all"])):
            return self.ret_val

        self._check_prefixes()
        self._check_forbidden_marks()
        self._check_indices()
        self._check_deadline()
        self._check_priority()
        if not self.no_warnings:
            Tty.print_sep()
        return self.ret_val

    def _check_forbidden_marks(self) -> None:
        forbidden_marks = ["$nxt", "$now", "$w8", "@ntx"]
        for jnote in common.get_db_local_notes().values():
            for forbidden_mark in forbidden_marks:
                if forbidden_mark in jnote.body:
                    print(f"{self.warning_str} `{Tty.underline(jnote.title)}` "
                          f"contains the forbidden mark {Tty.bold(forbidden_mark)}.")
                    self.no_warnings = False

    def _check_indices(self) -> None:
        """ Check that there are no repeating task indices. """
        titles = [x.title for x in common.get_db_local_notes().values()]
        idx_set = set()
        for title in titles:
            if (mtch := JCliHelpers.PTRN_TITLE_TASK.match(title)):
                idx = mtch.groups()[0]
                if idx in idx_set:
                    print(f"{self.warning_str} `There is more than one task with index `{idx}`.")
                    self.no_warnings = False
                idx_set.add(mtch.groups()[0])

    def _check_deadline(self) -> None:
        for jtask in self.jtasks:
            if not jtask.deadline_ok:
                print(f"{self.warning_str} `{Tty.underline(jtask.title)}` "
                      f"contains a {Tty.bold(jtask.PREFIX)} task without a deadline: "
                      f"{jtask.line}.")
                self.no_warnings = False

    def _check_priority(self) -> None:
        for jtask in self.jtasks:
            if not jtask.priority_ok:
                print(f"{self.warning_str} `{Tty.underline(jtask.title)}` "
                      f"contains a {Tty.bold(jtask.PREFIX)} task without a priority: "
                      f"{jtask.line}.")
                self.no_warnings = False

    def _check_prefixes(self) -> None:

        tags = [common.TAG_WAIT, common.TAG_NEXT, common.TAG_NOW]
        jtags: dict[str, common.JTag] = {}
        for tag in tags:
            jtags[tag] = [x for x in common.get_db_local_tags().values() if x.title == tag][0]
        # print(jtags_dict)

        prefixes = [JWait.PREFIX, JNext.PREFIX, JNow.PREFIX]
        jnotes: dict[str, common.JNote] = {}
        for prefix in prefixes:
            jnotes[prefix] = [x for x in common.get_db_local_notes().values() if prefix in x.body]
        # print(jnotes_dic)

        # Notes with certain prefixes MUST contain certain tags:
        for prefix, tag in [(JWait.PREFIX, common.TAG_WAIT),
                            (JNext.PREFIX, common.TAG_NEXT),
                            (JNow.PREFIX, common.TAG_NOW), ]:
            # print(f"{prefix=}, {tag=}")
            titles_prefix = set(x.title for x in jnotes[prefix])
            titles_tag = set(x.title for x in jtags[tag].notes)
            # print(f"\t{titles_prefix=}")
            # print(f"\t{titles_tag=}")
            if (diff := titles_prefix - titles_tag):
                for title in diff:
                    print(f"{self.warning_str} "
                          f"`{Tty.underline(title)}` contains PREFIX {Tty.bold(prefix)} "
                          f"but doesn't contain TAG {Tty.bold(tag)}.")
                self.no_warnings = False
            # if (diff := titles_tag - titles_prefix):
            #     for title in diff:
            #         print(f"{self.warning_str} "
            #               f"`{Tty.underline(title)}` has TAG {Tty.bold(tag)} "
            #               f"but doesn't contain PREFIX {Tty.bold(prefix)}.")
            #     self.no_warnings = False

        # Notes with certain tags MUST contain at least one prefix from the list:
        for tag, prefix in [(common.TAG_WAIT, {JWait.PREFIX, }),
                            (common.TAG_NEXT, {JNext.PREFIX, }),
                            (common.TAG_NOW, {JNow.PREFIX, }), ]:
            pass
            # print(f"{prefix=}, {tag=}")
