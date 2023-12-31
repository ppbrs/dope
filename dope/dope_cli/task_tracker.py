"""
Executing user requests related to tasks.
"""
import logging
from typing import Any

from dope.task import Task, TaskNext, TaskNow, TaskWait
from dope.term import Term

_logger = logging.getLogger(__name__)


class DopeCliTaskTracker:
    """An object of this class collects tasks and prints them according to user requests."""

    # There are many private methods instead, thus creating a class is still worth it.
    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        self.ret_val: int = 0

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to tasks.
        """
        if not any((args["tasks_next"], args["tasks_wait"], args["tasks_now"], args["tasks_all"])):
            return self.ret_val

        tasks = Task.collect()

        tasks = self._filter_by_type(tasks=tasks, args=args)
        _logger.debug("Filtered %d tasks by type.", len(tasks))

        tasks = self._filter_by_vault(tasks=tasks, args=args)
        _logger.debug("Filtered %d tasks by vault.", len(tasks))

        # Sort them.
        def sort_func(task: Task) -> tuple[int, int, int]:
            return (
                task.get_days_to_dealine(),
                {TaskNow: 0, TaskNext: 1, TaskWait: 2}[type(task)],
                task.priority
            )
        tasks = sorted(tasks, key=sort_func, reverse=True)

        self._print_tasks(tasks)
        return self.ret_val

    @staticmethod
    def _filter_by_type(tasks: list[Task], args: dict[str, Any]) -> list[Task]:
        """Filter tasks by type."""
        tasks_flt = []
        for task in tasks:
            if args["tasks_all"]:
                tasks_flt.append(task)
            elif isinstance(task, TaskNext) and args["tasks_next"]:
                tasks_flt.append(task)
            elif isinstance(task, TaskNow) and args["tasks_now"]:
                tasks_flt.append(task)
            elif isinstance(task, TaskWait) and args["tasks_wait"]:
                tasks_flt.append(task)
        return tasks_flt

    @staticmethod
    def _filter_by_vault(tasks: list[Task], args: dict[str, Any]) -> list[Task]:
        """Filter tasks by vault."""
        if args["vault"] is not None:
            tasks_flt = []
            for task in tasks:
                if args["vault"][0] in task.vault:
                    tasks_flt.append(task)
        else:
            tasks_flt = tasks
        return tasks_flt

    @staticmethod
    def _print_tasks(tasks: list[Task]) -> None:
        """Output the list of tasks to the terminal."""
        for task in tasks:

            if isinstance(task, TaskNext):
                task_str = Term.yellow(f"#nxt-P{task.priority}")
            elif isinstance(task, TaskNow):
                task_str = Term.green(f"#now-P{task.priority}")
            elif isinstance(task, TaskWait):
                task_str = Term.red(f" #w8-P{task.priority}")
            else:
                raise RuntimeError(str(task))
            if task.priority == 1:
                task_str = Term.underline(task_str)
            print(f"{task_str}: ", end="")

            days = task.get_days_to_dealine()
            if days == 0:
                deadline_str = Term.bold(Term.green("[today]"))
            elif days > 0:
                deadline_str = f"[in {days} days]"
            else:
                deadline_str = Term.bold(Term.cyan(f"[{days} days ago]"))
            print(f"{deadline_str} ", end="")

            note_str = Term.underline(Term.bold(task.note))
            print(f"{task.vault}/{note_str}", end="")
            print()

            print(f"{task.descr}\n\n", end="")
