"""
Executing user requests related to tasks.
"""
# Standard library imports
from datetime import date
from typing import Any
# Third party imports
# Local application/library imports
from jtask import JTask, JNext, JWait, JNow
from jcli_common import Tty, collect_tasks


class JCliTasks:
    """ An object of this class holds the list of collected tasks
    and has functions for showing tasks according to user requests. """

    def __init__(self) -> None:
        self.ret_val = 0
        self.jtasks = collect_tasks()

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to tasks.
        """
        if not any((args["tasks_next"], args["tasks_wait"], args["tasks_now"], args["tasks_all"])):
            return self.ret_val

        # self._print_sep()
        # os.system("clear")

        clss = set()
        if args["tasks_next"]:
            clss.add(JNext)
        if args["tasks_wait"]:
            clss.add(JWait)
        if args["tasks_now"]:
            clss.add(JNow)
        if args["tasks_all"]:
            clss.add(JNext)
            clss.add(JWait)
            clss.add(JNow)

        self._show_tasks(limit=args["limit"], clss=list(clss),
                         fltr_or=args["fltr_or"], priorities=args["priorities"])
        return self.ret_val

    def _show_tasks(self, limit: int | None,
                    clss: list[type[JNext] | type[JWait] | type[JNow]],
                    fltr_or: list[str] | None,
                    priorities: list[str] | None) -> None:

        jtask_lst = [jtask for jtask in self.jtasks if type(jtask) in clss]
        if fltr_or is not None:
            jtask_lst = [jtask for jtask in jtask_lst
                         if any(word.lower() in jtask.title.lower() for word in fltr_or)]

        if priorities is None:
            priorities_list = [1, 2, 3]
        else:
            priorities_list = [int(p) for p in priorities]
        jtask_lst = [jtask for jtask in jtask_lst if jtask.priority in priorities_list]

        Tty.print_sep()

        def sort_func(x: JTask) -> tuple[int, int, int]:
            return (
                x.get_days_to_dealine(),
                {JNow: 0, JNext: 1, JWait: 2}[type(x)],
                x.priority
            )

        jtask_lst_to_print = sorted(jtask_lst, key=sort_func, reverse=True)
        if limit is not None:
            jtask_lst_to_print = jtask_lst_to_print[-limit:]
        if len(jtask_lst) > len(jtask_lst_to_print):
            num_hidden = len(jtask_lst) - len(jtask_lst_to_print)
            # print(f"... {num_hidden} {task_type_str} more tasks.")
            print(f"... {num_hidden} more tasks.")
        for jtask in jtask_lst_to_print:
            self._print_jtask(jtask)
        if not jtask_lst_to_print:
            print("There are no tasks in this category.")
        Tty.print_sep()

    @staticmethod
    def _deadline_to_str(deadline: date) -> str:
        assert isinstance(deadline, date)
        weekday = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su", ][deadline.weekday()]
        return f"{deadline}-{weekday}"

    def _print_jtask(self, jtask: JTask) -> None:

        #
        # type of task and priority
        #
        prefix_s = jtask.PREFIX.upper()
        if len(prefix_s) < 4:
            prefix_s = " " + prefix_s
        if isinstance(jtask, JWait):
            prefix_s = f"{Tty.RED}{prefix_s}-P{jtask.priority}{Tty.END}"
        elif isinstance(jtask, JNext):
            prefix_s = f"{Tty.YELLOW}{prefix_s}-P{jtask.priority}{Tty.END}"
        elif isinstance(jtask, JNow):
            prefix_s = f"{Tty.GREEN}{prefix_s}-P{jtask.priority}{Tty.END}"
        else:
            raise RuntimeError(f"{type(jtask)=}, {jtask.__class__=}")
        if jtask.priority <= 2:
            prefix_s = Tty.BOLD + prefix_s
        if jtask.priority == 1:
            prefix_s = Tty.UNDERLINE + prefix_s
        print(f"{prefix_s}: ", end="")

        #
        # deadline
        #
        days = jtask.get_days_to_dealine()
        if days == 0:
            deadline_str = Tty.GREEN + Tty.BOLD + "[today] " + Tty.END
        elif days < 0:
            deadline_str = Tty.CYAN + Tty.BOLD + f"[in {days} days] " + Tty.END
        else:
            deadline_str = f"[in {days} days] "
        print(deadline_str, end="")

        #
        # title
        #
        print(f"{Tty.BOLD}{Tty.UNDERLINE}{jtask.title}{Tty.END}.")

        #
        # task description
        #
        print("\t", end="")
        if jtask.marks:
            print(Tty.RED, end="")
            print(" ".join(jtask.marks), "", end="")
            print(Tty.END, end="")
        print(f"{jtask.line}")
        print()
