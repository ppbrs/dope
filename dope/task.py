"""Contains Task abstraction and its subtypes."""
from __future__ import annotations

import dataclasses
import logging
import pathlib
import re
from collections.abc import Generator
from dataclasses import dataclass
from datetime import date

from dope.v_note import VNote

_logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Encapsulates all information about a task."""

    descr: str
    vault: str
    note: str
    priority: int
    deadline: date

    re_obj_full_tag = re.compile(
        r".*"  # Pptional symbols before the tag.
        + r"(?P<full_tag>\#(n|x|w)\/.*?)"  # The tag itself.
        + r"(\s.*|\:|$)")  # Either nothing, or a colon, or at least one space after the tag.
    """
    A full tag looks like #x/p2/2023-12-31.
    """
    re_obj_deadline = re.compile(r"^(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)$")

    @classmethod
    def _parse_line(
        cls, note_line: str, v_note: VNote, line_num: int
    ) -> Generator[Task, None, None]:
        """Collect all tasks from the given line."""
        if "#" not in note_line:
            return

        matches = cls.re_obj_full_tag.findall(note_line)
        if len(matches) > 1:
            _logger.error("More than 1 task flag in a line: '%s'.", note_line)
        elif len(matches) == 1:
            mtch_full_tag = cls.re_obj_full_tag.match(note_line)
            assert mtch_full_tag is not None
            full_tag = mtch_full_tag.groupdict()["full_tag"]
            note_line = note_line.replace(full_tag, "")

            task_cls = cls._get_task_class(full_tag)

            vault = v_note.vault_dir.stem
            note = v_note.note_path.stem

            # Correct errors in a tag and emit warnings here.
            tag_parts = full_tag.split("/")
            if tag_parts[0] not in {"#n", "#x", "#w"}:
                _logger.error(
                    "Corrupted tag `%s`, line %d of '%s/%s'.", tag_parts[0], line_num, vault, note)
            priority = 3
            if len(tag_parts) >= 2:
                if tag_parts[1] not in {"p1", "p2", "p3"}:
                    _logger.error("Tag `%s` in `%s/%s` has unknown priority.",
                                  full_tag, vault, note)
                else:
                    priority = int(tag_parts[1][1:])

            deadline = date.today()
            if len(tag_parts) != 3:
                _logger.error("Tag `%s` in `%s/%s` is missing required subtags.",
                              full_tag, vault, note)
            else:
                mtch_deadline = cls.re_obj_deadline.fullmatch(tag_parts[2])
                if mtch_deadline is not None:
                    deadline = date(year=int(mtch_deadline.groupdict()["year"]),
                                    month=int(mtch_deadline.groupdict()["month"]),
                                    day=int(mtch_deadline.groupdict()["day"]))
                else:
                    _logger.error("Tag `%s` in `%s/%s` has corrupted deadline.",
                                  full_tag, vault, note)

            yield task_cls(descr=cls.clean_line(note_line), vault=vault, note=note,
                           priority=priority, deadline=deadline)

    @classmethod
    def clean_line(cls, note_line: str) -> str:
        """Remove useless symbols."""
        note_line = note_line.replace("\n", "")
        note_line = note_line.replace("\r", "")
        note_line = note_line.replace("- [ ]", " ")
        note_line = note_line.replace("* [ ]", " ")
        note_line = note_line.replace("🟧", "")
        note_line = note_line.replace("\t", " ")
        note_line = note_line.strip()
        if note_line.startswith("*") or note_line.startswith("-"):
            note_line = note_line[1:]
        note_line = note_line.replace("   ", " ")
        note_line = note_line.replace("  ", " ")
        note_line = note_line.strip()
        return note_line

    @classmethod
    def _get_task_class(cls, full_tag: str) -> type[TaskNext] | type[TaskWait] | type[TaskNow]:
        if full_tag.startswith("#x"):
            return TaskNext
        if full_tag.startswith("#w"):
            return TaskWait
        if full_tag.startswith("#n"):
            return TaskNow
        raise RuntimeError

    @classmethod
    def collect(cls, vault_dirs: list[pathlib.PosixPath]) -> list[Task]:
        """ Find all tasks in all vaults."""
        tasks: list[Task] = []

        num_lines = 0
        for v_note in VNote.collect_iter(vault_dirs=vault_dirs, exclude_trash=True):
            with open(v_note.note_path, "r", encoding="utf8") as note_fd:
                note_lines = note_fd.readlines()
            in_code_block = False
            for line_num, note_line in enumerate(note_lines, start=1):
                if note_line.startswith("```"):
                    in_code_block = not in_code_block
                if not in_code_block:
                    num_lines += 1
                    for task in cls._parse_line(
                        note_line=note_line, v_note=v_note, line_num=line_num
                    ):
                        tasks.append(task)
                        _logger.info("%s", task)
        _logger.debug("Checked %d lines, collected %d tasks", num_lines, len(tasks))

        return tasks

    def get_days_to_dealine(self) -> int:
        """Calculate the number of days to the deadline."""
        return (self.deadline - date.today()).days

    def get_deadline_string(self) -> str:
        """Return the deadline in the format YYYY-MM-DD-DOW."""
        weekday_idx = self.deadline.weekday()  # Monday is 0 and Sunday is 6
        weekday_str = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][weekday_idx]
        return str(self.deadline) + " " + weekday_str


class TaskNext(Task):
    """Encapsulates all information about a next action."""


class TaskWait(Task):
    """Encapsulates all information about a pending action."""


class TaskNow(Task):
    """Encapsulates all information about a current action."""


def test_task_parse_match_tag() -> None:
    """Test the regular expression used to find tags belonging to tasks in notes."""
    @dataclasses.dataclass
    class TestCase:
        """A test case."""
        string: str  # A text line.
        matches: bool  # Whether there is a tag in a line.
        full_tag: str | None  # The tag if there is one.

    test_cases = [
        TestCase("abcd #w/p3/2020-09-09 abcd", True, "#w/p3/2020-09-09"),
        TestCase("#w/p3/2020-09-09 abcd", True, "#w/p3/2020-09-09"),
        TestCase("#w/p3/2020-09-09", True, "#w/p3/2020-09-09"),
        TestCase(" #w/p3/2020-09-09", True, "#w/p3/2020-09-09"),

        TestCase("abcd #x/p3/2020-09-09 abcd", True, "#x/p3/2020-09-09"),
        TestCase("#x/p3/2020-09-09 abcd", True, "#x/p3/2020-09-09"),
        TestCase("#x/p3/2020-09-09", True, "#x/p3/2020-09-09"),
        TestCase(" #x/p3/2020-09-09", True, "#x/p3/2020-09-09"),

        TestCase("abcd #n/p3/2020-09-09 abcd", True, "#n/p3/2020-09-09"),
        TestCase("#n/p3/2020-09-09 abcd", True, "#n/p3/2020-09-09"),
        TestCase("#n/p3/2020-09-09", True, "#n/p3/2020-09-09"),
        TestCase(" #n/p3/2020-09-09", True, "#n/p3/2020-09-09"),

        TestCase("abcd #n/p3/2020-09-09: abcd", True, "#n/p3/2020-09-09"),
        TestCase("#n/p3/2020-09-09: abcd", True, "#n/p3/2020-09-09"),
        TestCase("#n/p3/2020-09-09:", True, "#n/p3/2020-09-09"),
        TestCase(" #n/p3/2020-09-09:", True, "#n/p3/2020-09-09"),

        TestCase("#week", False, None),
        TestCase("#now", False, None),
        TestCase("#xyz", False, None),
    ]

    for test_case in test_cases:
        match = Task.re_obj_full_tag.match(test_case.string)
        if match is not None:
            full_tag = match.groupdict()["full_tag"]
        if test_case.matches:
            assert match, f"Tag expected in '{test_case.string}'."
            assert full_tag == test_case.full_tag, \
                f"Tag expected '{test_case.full_tag}', got '{full_tag}'."
        else:
            assert not match, f"No tag expected in '{test_case.string}', but got '{full_tag}'."
