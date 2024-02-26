"""
Executing user requests related to my education.
"""
from __future__ import annotations

import logging
import random
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from dope.task import Task
from dope.term import Term
from dope.v_note import VNote

_logger = logging.getLogger(__name__)


@dataclass
class Lesson:
    """Encapsulates all information about a lesson."""

    descr: str
    vault: str
    note: str
    tag: str
    course: str
    size: str
    action: str

    @classmethod
    def collect(cls) -> list[Lesson]:
        """ Find all lessons in all vaults."""
        lessons: list[Lesson] = []

        num_lines = 0
        for v_note in VNote.collect_iter(exclude_trash=True):
            with open(v_note.note_path, "r", encoding="utf8") as note_fd:
                note_lines = note_fd.readlines()
            in_code_block = False
            for note_line in note_lines:
                if note_line.startswith("```"):
                    in_code_block = not in_code_block
                if not in_code_block:
                    num_lines += 1
                    for task in cls._parse_line(note_line=note_line, v_note=v_note):
                        lessons.append(task)
                        _logger.info("%s", task)
        _logger.debug("Checked %d lines, collected %d lessons", num_lines, len(lessons))

        return lessons

    @classmethod
    def _parse_line(cls, note_line: str, v_note: VNote) -> Generator[Lesson, None, None]:
        """Collect all lessons from the given line."""
        if "#edu/" not in note_line:
            return

        parts = note_line.split(" ")
        for part in parts:
            if part.startswith("#edu/"):
                tag = part.replace("#edu/", "")
                assert len(tag.split("/")) == 3, f"`{part}` has wrong number of components."
                course, size, action = tag.split("/")

                vault = v_note.vault_dir.name
                note = v_note.note_path.stem
                descr = Task.clean_line(note_line.replace(part, ""))

                yield Lesson(vault=vault, note=note, tag=tag, descr=descr,
                             course=course, size=size, action=action)


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
        if not args["edu"]:
            return self.ret_val

        lessons: list[Lesson] = Lesson.collect()

        # Filter by vault:
        vault_filter: None | list[str] = args["vault"]
        if vault_filter is not None:
            filtered: list[Lesson] = []
            for subtask in lessons:
                if any(token in subtask.vault for token in vault_filter):
                    filtered.append(subtask)
            lessons = filtered

        courses = set(stsk.course for stsk in lessons)
        _logger.debug("Courses: %s.", courses)

        print(Term.green("LESSONS:"))

        # Print as course -> size -> action -> vault -> note -> description.
        for course in sorted(courses):
            print(f"{course}")
            sizes = set(stsk.size for stsk in lessons if stsk.course == course)
            for size in sorted(sizes):
                print(f"\t{size}")
                actions = set(stsk.action for stsk in lessons
                              if stsk.course == course and stsk.size == size)
                for action in sorted(actions):
                    print(f"\t\t{action}")
                    filtered = [stsk for stsk in lessons
                                if (stsk.course == course
                                    and stsk.size == size
                                    and stsk.action == action)]
                    random.shuffle(filtered)
                    for stsk in filtered:
                        print(f"\t\t\t{stsk.vault}/", end="")
                        print(f"{Term.underline(Term.bold(stsk.note))}: ", end="")
                        print(f"{stsk.descr}.")

        return self.ret_val
