"""
Executing user requests related to tasks.
"""

import argparse
import datetime
import logging
import pathlib
from datetime import date
from typing import Any

from dope.config import get_vault_paths
from dope.task import Task, TaskNext, TaskNow, TaskWait
from dope.term import Term

_logger = logging.getLogger(__name__)


class TaskTracker:
    """An object of this class collects tasks and prints them according to user requests."""

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add arguments to the provided argument parser.

        This method is expected to run before parser.parse_args() is invoked.
        """
        task_group = parser.add_argument_group("Task tracker")

        optional_keywords_help = "If keywords are given, only tasks that contain them in note title or task description will be shown."
        task_group.add_argument(
            "-x",
            "--next",
            dest="tasks_next",
            help=f"Show next tasks. {optional_keywords_help}",
            nargs="*",  # 0 or any number
            default=None,  # if omitted
        )
        task_group.add_argument(
            "-w",
            "--wait",
            dest="tasks_wait",
            help=f"Show pending tasks. {optional_keywords_help}",
            nargs="*",  # 0 or any number
            default=None,  # if omitted
        )
        task_group.add_argument(
            "-n",
            "--now",
            dest="tasks_now",
            help=f"Show current tasks. {optional_keywords_help}",
            nargs="*",  # 0 or any number
            default=None,  # if omitted
        )
        task_group.add_argument(
            "-t",
            "--tasks",
            dest="tasks_all",
            help=f"Show all tasks. {optional_keywords_help}",
            nargs="*",  # 0 or any number
            default=None,  # if omitted
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
            nargs="+",  # 1 or more
            default=["123"],
            action="store",
            help=(
                "List of priorities (1=urgent/very important, 2=moderate importance, "
                '3=not important). "12" means both "1" and "2\'.'
            ),
        )

    @staticmethod
    def check_arguments(parser: argparse.ArgumentParser, args: dict[str, Any]) -> None:
        is_tasks_cmd = (
            args["tasks_next"] is not None
            or args["tasks_wait"] is not None
            or args["tasks_now"] is not None
            or args["tasks_all"] is not None
        )
        error_msg_ending = (
            "requires either -t/--tasks or -x/--next or -n/--now or -w/--wait to be provided."
        )
        if "priorities" in args and not is_tasks_cmd:
            parser.error(f"Argument -p/--priorities {error_msg_ending}")
        if "show_future_tasks" in args and not is_tasks_cmd:
            parser.error(f"Argument -f/--show-future-tasks {error_msg_ending}")

    __slots__ = (
        "tasks_next",
        "tasks_wait",
        "tasks_now",
        "tasks_all",
        "show_future_tasks",
        "priorities",
    )
    tasks_next: list[str] | None
    tasks_wait: list[str] | None
    tasks_now: list[str] | None
    tasks_all: list[str] | None
    show_future_tasks: bool
    priorities: list[str]

    def __init__(self, args: dict[str, Any]) -> None:
        self.tasks_next = args["tasks_next"]
        self.tasks_wait = args["tasks_wait"]
        self.tasks_now = args["tasks_now"]
        self.tasks_all = args["tasks_all"]
        self.show_future_tasks = args["show_future_tasks"]
        self.priorities = args["priorities"]

    @staticmethod
    def process(args: dict[str, Any]) -> int:
        """Executing user's requests related to tasks."""
        self = TaskTracker(args=args)
        if not any(
            t is not None
            for t in (self.tasks_next, self.tasks_wait, self.tasks_now, self.tasks_all)
        ):
            return 0

        vault_dirs = get_vault_paths(filter=args["vault"])
        return self.process_method(tasks=Task.collect(vault_dirs=vault_dirs))

    def process_method(self, tasks: list[Task]) -> int:
        """Filter and print."""

        tasks = self._filter_by_type(tasks=tasks)
        _logger.debug("Filtered %d tasks by type.", len(tasks))

        tasks = self._filter_by_priority(tasks=tasks)
        _logger.debug("Filtered %d tasks by priority.", len(tasks))

        tasks = self._filter_by_due_date(tasks=tasks)
        _logger.debug("Filtered %d tasks by due date.", len(tasks))

        # Sort them.
        def sort_func(task: Task) -> tuple[int, int, int]:
            return (task.get_days_to_dealine(), task.SORTING_PRECEDENCE, task.priority)

        tasks = sorted(tasks, key=sort_func, reverse=True)

        self._print_tasks(tasks)

        self._write_tasks(tasks)
        return 1

    def _filter_by_type(self, tasks: list[Task]) -> list[Task]:
        """Filter tasks by type."""
        tasks_flt = []
        for task in tasks:
            if self._filter_one(task, self.tasks_all):
                tasks_flt.append(task)
            elif isinstance(task, TaskNext) and self._filter_one(task, self.tasks_next):
                tasks_flt.append(task)
            elif isinstance(task, TaskNow) and self._filter_one(task, self.tasks_now):
                tasks_flt.append(task)
            elif isinstance(task, TaskWait) and self._filter_one(task, self.tasks_wait):
                tasks_flt.append(task)
        return tasks_flt

    @staticmethod
    def _filter_one(task: Task, filter_value: list[str] | None) -> bool:
        if filter_value is None:
            return False
        if filter_value:
            match = False
            for word in filter_value:
                if word.lower() in task.note.lower() or word.lower() in task.descr.lower():
                    match = True
            return match
        return True  # filter_value is an empty list

    def _filter_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Filter tasks by their priority."""
        # Only 1, 2, 3, or any combination of them are accepted.
        assert isinstance(self.priorities, list)
        assert all(isinstance(s, str) for s in self.priorities)
        try:
            priorities = {int(c) for c in "".join(self.priorities)}
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

    def _filter_by_due_date(self, tasks: list[Task]) -> list[Task]:
        """Filter tasks by due date."""
        today = date.today()
        tasks_flt = []
        for task in tasks:
            if task.deadline <= today or self.show_future_tasks:
                tasks_flt.append(task)
        return tasks_flt

    @staticmethod
    def _print_tasks(tasks: list[Task]) -> None:
        """Output the list of tasks to the terminal."""
        for task in tasks:
            if isinstance(task, TaskNext):
                task_str = Term.yellow(task.get_type_priority_short_string())
            elif isinstance(task, TaskNow):
                task_str = Term.green(task.get_type_priority_short_string())
            elif isinstance(task, TaskWait):
                task_str = Term.red(task.get_type_priority_short_string())
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

    @staticmethod
    def _write_tasks(tasks: list[Task]) -> None:
        """Write to TASKS.md for each vault that contains tasks."""
        vaults: dict[str, pathlib.PosixPath] = {}
        for task in tasks:
            vault_name = task.vault
            if vault_name not in vaults:
                vault_dirs = get_vault_paths(filter=[vault_name])
                assert len(vault_dirs) == 1
                vaults[vault_name] = vault_dirs[0]
        for vault_name, vault_dir in vaults.items():
            tasks_path = vault_dir / "TASKS.md"
            existed = tasks_path.exists()
            if not existed:
                _logger.debug("Creating '%s'.", tasks_path)
                tasks_path.touch()
            else:
                _logger.debug("'%s' already exists", tasks_path)

            text_orig: list[str] = tasks_path.read_text().splitlines()
            _logger.debug("%d lines", len(text_orig))

            text_new: list[str] = []

            dt_str = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
            text_new.append(f"Updated {dt_str}")

            last_written_task_type: str | None = None
            for task in reversed(tasks):
                if task.vault != vault_name:
                    continue

                dl_str = task.get_deadline_string()
                days = task.get_days_to_dealine()
                if days == 0:
                    deadline_str = f'<span style="color:green">today, {dl_str}</span>'
                elif days > 0:
                    deadline_str = f"in {days} days, {dl_str}"
                else:
                    deadline_str = f'<span style="color:red">{days} days ago, {dl_str}</span>'

                note_rel_path = task.note_rel_path.replace(" ", "%20")

                if type(task).__name__ != last_written_task_type:
                    text_new.append("***")
                    text_new.append(f"# {task.get_type_string().upper()}\n")

                text_new.append(
                    f"**{task.get_type_priority_short_string()}** {deadline_str}\n"
                    f"\t\t[**{task.note}** :{task.line_num}]({note_rel_path})\n"
                    f"\t\t\t\t{task.descr}\n"
                    ""
                )

                last_written_task_type = type(task).__name__

            text_new.append("***\n")

            tasks_path.write_text("\n".join(text_new))
            print(f"'{tasks_path}' was updated.")
