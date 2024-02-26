"""Contains Task abstraction and its subtypes."""
from __future__ import annotations

import logging
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

    re_obj_full_tag = re.compile(r".*(?P<full_tag>\#(nxt|w8|now).*?)(\s.*|$)")
    """
    A full tag looks like #nxt/p2/20231231.
    """
    re_obj_deadline = re.compile(r"^(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)$")

    @classmethod
    def _parse_line(cls, note_line: str, v_note: VNote) -> Generator[Task, None, None]:
        """Collect all tasks from the given line."""
        if "#" not in note_line:
            return

        for mtch_full_tag in cls.re_obj_full_tag.finditer(note_line):
            vault = v_note.vault_dir.stem
            note = v_note.note_path.stem
            full_tag = mtch_full_tag.groupdict()["full_tag"]
            note_line = note_line.replace(full_tag, "")

            task_cls = cls._get_task_class(full_tag)

            # Correct errors in a tag and emit warnings here.
            tag_parts = full_tag.split("/")
            if tag_parts[0] not in {"#nxt", "#now", "#w8"}:
                _logger.error("Tag `%s` in `%s/%s` is corrupted.", tag_parts[0], vault, note)
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
        if full_tag.startswith("#nxt"):
            return TaskNext
        if full_tag.startswith("#w8"):
            return TaskWait
        if full_tag.startswith("#now"):
            return TaskNow
        raise RuntimeError

    @classmethod
    def collect(cls) -> list[Task]:
        """ Find all tasks in all vaults."""
        tasks: list[Task] = []

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
