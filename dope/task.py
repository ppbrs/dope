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
    SORTING_PRECEDENCE = -1
    """It is considered when listing tasks."""

    descr: str
    vault: str
    note: str
    priority: int
    deadline: date

    re_obj_full_tag = re.compile(
        r".*"  # Optional symbols before the tag.
        + r"(?P<full_tag>\#.*?\/(n|x|w)\d)"  # The tag itself.
        + r"(\s.*|\:|$)")  # Either nothing, or a colon, or at least one space after the tag.
    """
    A full tag looks like #2023-12-31/x2.
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

            task_cls = cls.get_task_class(full_tag)

            vault = v_note.vault_dir.stem
            note = v_note.note_path.stem

            # Correct errors in a tag and emit warnings here.
            tag_parts = full_tag.split("/")

            tag_ok = (
                len(tag_parts) == 2
                and tag_parts[0][0] == "#"
                and tag_parts[1][0] in {"n", "x", "w"}
                and tag_parts[1][1] in {"1", "2", "3"}
            )
            if not tag_ok:
                _logger.error(
                    "Corrupted tag `%s` in '%s/%s', line %d.", full_tag, vault, note, line_num)
            priority = int(tag_parts[1][1:]) if len(tag_parts) > 1 else 1

            mtch_deadline = cls.re_obj_deadline.fullmatch(tag_parts[0][1:])
            if mtch_deadline is not None:
                deadline = date(year=int(mtch_deadline.groupdict()["year"]),
                                month=int(mtch_deadline.groupdict()["month"]),
                                day=int(mtch_deadline.groupdict()["day"]))
            else:
                deadline = date.today()
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
    def get_task_class(cls, full_tag: str) -> type[TaskNext] | type[TaskWait] | type[TaskNow]:
        """Determine concrete type of a task using the given tag."""
        if full_tag[-2] == "x":
            return TaskNext
        if full_tag[-2] == "w":
            return TaskWait
        if full_tag[-2] == "n":
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
    SORTING_PRECEDENCE = 1


class TaskWait(Task):
    """Encapsulates all information about a pending action."""
    SORTING_PRECEDENCE = 2  # lowest


class TaskNow(Task):
    """Encapsulates all information about a current action."""
    SORTING_PRECEDENCE = 0  # highest


def test_task_parse_match_tag() -> None:
    """Test the regular expression used to find tags belonging to tasks in notes."""
    @dataclasses.dataclass
    class TestCase:
        """A test case."""
        string: str  # A text line.
        matches: bool  # Whether there is a tag in a line.
        full_tag: str | None  # The tag if there is one.
        task_class: type[TaskNext] | type[TaskWait] | type[TaskNow] | None

    test_cases = [
        TestCase("abcd #2020-09-09/w3 abcd", True, "#2020-09-09/w3", TaskWait),
        TestCase("#2020-09-09/w3 abcd", True, "#2020-09-09/w3", TaskWait),
        TestCase("#2020-09-09/w3", True, "#2020-09-09/w3", TaskWait),
        TestCase(" #2020-09-09/w3", True, "#2020-09-09/w3", TaskWait),

        TestCase("abcd #2020-09-09/x3 abcd", True, "#2020-09-09/x3", TaskNext),
        TestCase("#2020-09-09/x3 abcd", True, "#2020-09-09/x3", TaskNext),
        TestCase("#2020-09-09/x3", True, "#2020-09-09/x3", TaskNext),
        TestCase(" #2020-09-09/x3", True, "#2020-09-09/x3", TaskNext),

        TestCase("abcd #2020-09-09/n3 abcd", True, "#2020-09-09/n3", TaskNow),
        TestCase("#2020-09-09/n3 abcd", True, "#2020-09-09/n3", TaskNow),
        TestCase("#2020-09-09/n3", True, "#2020-09-09/n3", TaskNow),
        TestCase(" #2020-09-09/n3", True, "#2020-09-09/n3", TaskNow),

        TestCase("abcd #2020-09-09/n3: abcd", True, "#2020-09-09/n3", TaskNow),
        TestCase("#2020-09-09/n3: abcd", True, "#2020-09-09/n3", TaskNow),
        TestCase("#2020-09-09/n3:", True, "#2020-09-09/n3", TaskNow),
        TestCase(" #2020-09-09/n3:", True, "#2020-09-09/n3", TaskNow),

        TestCase("#week", False, None, None),
        TestCase("#now", False, None, None),
        TestCase("#xyz", False, None, None),
    ]

    for test_case in test_cases:
        match = Task.re_obj_full_tag.match(test_case.string)
        full_tag = match.groupdict()["full_tag"] if match is not None else None
        if test_case.matches:
            assert test_case.full_tag is not None

            assert match, f"Tag expected in '{test_case.string}'."
            assert full_tag == test_case.full_tag, \
                f"Tag expected '{test_case.full_tag}', got '{full_tag}'."

        else:
            assert not match, f"No tag expected in '{test_case.string}', but got '{full_tag}'."
