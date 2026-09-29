"""
Executing user requests related to my education.
"""

from __future__ import annotations

import argparse
import logging
import os
import random
from typing import Any

from dope.config import get_vault_paths
from dope.lesson import Lesson
from dope.term import Term

_logger = logging.getLogger(__name__)


class EduTracker:
    """
    An object of this class collects and prints lessons.
    """

    # There are many private methods instead, thus creating a class is still worth it.
    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        self.ret_val: int = 0

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to educational tasks.
        """
        if args["edu"] is None:
            return self.ret_val

        vault_dirs = get_vault_paths(filter=args["vault"])
        lessons: list[Lesson] = Lesson.collect(vault_dirs=vault_dirs, course_filter=args["edu"])

        courses = set(stsk.course for stsk in lessons)
        _logger.debug("Courses (%d): %s.", len(courses), courses)

        print(Term.green("LESSONS:"))

        # Print as course -> action -> vault -> note -> line_num -> description.
        for course in sorted(courses):
            print(f"{course}")
            actions = set(stsk.action for stsk in lessons if stsk.course == course)
            for action in sorted(actions):
                if action in {"x", "big"}:
                    action_str = Term.yellow(action.upper())
                elif action == "n":
                    action_str = Term.green(action.upper())
                elif action == "w":
                    action_str = Term.red(action.upper())
                else:
                    action_str = action.upper()
                print(f"\t\t{action_str}")
                filtered = [
                    stsk for stsk in lessons if (stsk.course == course and stsk.action == action)
                ]
                random.shuffle(filtered)
                for stsk in filtered:
                    print(f"\t\t\t{stsk.pretty_str()}")

        print("--------")
        print("STATS:")
        print(f"{len(courses)} courses, {len(lessons)} lessons")
        if lessons:
            print("--------")
            print("SELECTED:")
            rnd_lesson_idx = int(os.urandom(4).hex(), 16) % len(lessons)
            rnd_lesson = lessons[rnd_lesson_idx]
            print(f"\t{rnd_lesson.course}")
            print(f"\t{rnd_lesson.pretty_str()}")
        print("--------")

        return self.ret_val

    @staticmethod
    def _filter_by_vault(lessons: list[Lesson], vault_filter: None | list[str]) -> list[Lesson]:
        if vault_filter is not None:
            filtered: list[Lesson] = []
            for subtask in lessons:
                if any(token in subtask.vault for token in vault_filter):
                    filtered.append(subtask)
            lessons = filtered
        return lessons

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add arguments to the provided argument parser.

        This method is expected to run before parser.parse_args() is invoked.
        """
        parser.add_argument(
            "-e",
            "--edu",
            dest="edu",
            nargs="*",  # The result is None or a list.
            action="store",
            help="List all education tasks: lessons and quizzes.",
        )
