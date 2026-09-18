"""
Executing user requests related to tasks.
"""

import argparse
import logging
from datetime import date
from typing import Any

from dope.config import get_vault_paths
from dope.task import Task, TaskNext, TaskNow, TaskWait
from dope.term import Term

_logger = logging.getLogger(__name__)


class TaskTracker:
    """An object of this class collects tasks and prints them according to user requests."""

    # There are many private methods instead, thus creating a class is still worth it.
    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        self.ret_val: int = 0

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add arguments to the provided argument parser.

        This method is expected to run before parser.parse_args() is invoked.
        """
        task_group = parser.add_argument_group("Task tracker")
        task_group.add_argument(
            "-x", "--next", dest="tasks_next", action="store_true", help="Show next tasks."
        )
        task_group.add_argument(
            "-w", "--wait", dest="tasks_wait", action="store_true", help="Show pending tasks."
        )
        task_group.add_argument(
            "-n", "--now", dest="tasks_now", action="store_true", help="Show current tasks."
        )
        task_group.add_argument(
            "-t", "--tasks", dest="tasks_all", action="store_true", help="Show all tasks."
        )
        task_group.add_argument(
            "-f",
            "--show-future-tasks",
            dest="show_future_tasks",
            action="store_true",
            help="When showing tasks, include future tasks.",
        )
        task_group.add_argument(
            "-p",
            "--priorities",
            dest="priorities",
            nargs="+",
            default=["123"],
            action="store",
            help=(
                "List of priorities (1=urgent/very important, 2=moderate importance, "
                '3=not important). "12" means both "1" and "2\'.'
            ),
        )

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to tasks.
        """
        if not any((args["tasks_next"], args["tasks_wait"], args["tasks_now"], args["tasks_all"])):
            return self.ret_val

        vault_dirs = get_vault_paths(filter=args["vault"])
        tasks = Task.collect(vault_dirs=vault_dirs)

        tasks = self._filter_by_type(tasks=tasks, args=args)
        _logger.debug("Filtered %d tasks by type.", len(tasks))

        tasks = self._filter_by_priority(tasks=tasks, args=args)
        _logger.debug("Filtered %d tasks by priority.", len(tasks))

        tasks = self._filter_by_due_date(tasks=tasks, args=args)
        _logger.debug("Filtered %d tasks by due date.", len(tasks))

        # Sort them.
        def sort_func(task: Task) -> tuple[int, int, int]:
            return (task.get_days_to_dealine(), task.SORTING_PRECEDENCE, task.priority)

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
    def _filter_by_priority(tasks: list[Task], args: dict[str, Any]) -> list[Task]:
        """Filter tasks by their priority."""
        # Only 1, 2, 3, or any combination of them are accepted.
        priorities = args["priorities"]
        assert isinstance(priorities, list)
        assert all(isinstance(i, str) for i in priorities)
        priorities = set("".join(priorities))
        try:
            priorities = {int(i) for i in priorities}
        except ValueError as err:
            raise ValueError("Priorities must be integers.") from err
        assert all(int(i) in [1, 2, 3] for i in priorities), (
            f"At least one priority is unrecognized: {priorities=}"
        )

        tasks_flt = []
        for task in tasks:
            match task.priority:
                case 1:
                    if 1 in priorities:
                        tasks_flt.append(task)
                case 2:
                    if 2 in priorities:
                        tasks_flt.append(task)
                case 3:
                    if 3 in priorities:
                        tasks_flt.append(task)
                case _:
                    raise ValueError(f"Unsupported priority: {task.priority}")
        return tasks_flt

    @staticmethod
    def _filter_by_due_date(tasks: list[Task], args: dict[str, Any]) -> list[Task]:
        """Filter tasks by due date."""
        show_future_tasks = args["show_future_tasks"]
        today = date.today()
        tasks_flt = []
        for task in tasks:
            if task.deadline <= today or show_future_tasks:
                tasks_flt.append(task)
        return tasks_flt

    @staticmethod
    def _print_tasks(tasks: list[Task]) -> None:
        """Output the list of tasks to the terminal."""
        for task in tasks:
            if isinstance(task, TaskNext):
                task_str = Term.yellow(f"#X{task.priority}")
            elif isinstance(task, TaskNow):
                task_str = Term.green(f"#N{task.priority}")
            elif isinstance(task, TaskWait):
                task_str = Term.red(f"#W{task.priority}")
            else:
                raise RuntimeError(str(task))
            if task.priority == 1:
                task_str = Term.underline(task_str)
            print(f"{task_str}: ", end="")

            dl_str = task.get_deadline_string()
            days = task.get_days_to_dealine()
            if days == 0:
                deadline_str = Term.bold(Term.green(f"[today, {dl_str}]"))
            elif days > 0:
                deadline_str = f"[in {days} days, {dl_str}]"
            else:
                deadline_str = Term.bold(Term.cyan(f"[{days} days ago, {dl_str}]"))
            print(f"{deadline_str} ", end="")

            note_str = Term.underline(Term.bold(task.note))
            print(f"{task.vault}/{note_str} :{task.line_num}", end="")
            print()

            print(f"\t{task.descr}\n\n", end="")
