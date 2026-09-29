"""Contains Lesson class."""

from __future__ import annotations

import logging
import pathlib
from collections.abc import Iterator
from dataclasses import dataclass

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
    line_num: int
    tag: str
    course: str
    action: str  # one of _actions

    _actions = {"x", "n", "w", "big"}

    @staticmethod
    def collect(vault_dirs: list[pathlib.PosixPath], course_filter: list[str]) -> list[Lesson]:
        """Find all lessons in all vaults.

        A line of the form "... #edu/{course}/{action}[:] {descr}" is considered a lesson.
        """
        lessons: list[Lesson] = []

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
                    for lesson in Lesson._parse_line(
                        note_line=note_line, v_note=v_note, line_num=line_num
                    ):
                        if not course_filter:
                            lessons.append(lesson)
                        else:
                            for word in course_filter:
                                if word in lesson.course:
                                    lessons.append(lesson)
                                    break
                        _logger.info("%s", lesson)
        _logger.debug("Checked %d lines, collected %d lessons", num_lines, len(lessons))

        return lessons

    @staticmethod
    def _parse_line(note_line: str, v_note: VNote, line_num: int) -> Iterator[Lesson]:
        """Collect all lessons from the given line."""
        if "#edu/" not in note_line:
            return

        note_line = note_line.replace("\r", "").replace("\n", "")
        for word in note_line.split(" "):
            if word.startswith("#edu/"):
                tag = word[:-1] if word.endswith(":") else word
                tag_comps = tag.split("/")
                num_tag_comps = len("#edu/course/action".split("/"))
                if len(tag_comps) < num_tag_comps:
                    continue
                assert len(tag_comps) == num_tag_comps, (
                    f"Tag `{word}` in `{v_note.note_path.name}` has wrong number of components "
                    f"(got {len(tag_comps)}, expected {num_tag_comps})."
                )
                _, course, action = tag_comps

                vault = v_note.vault_dir.name
                note = v_note.note_path.stem
                descr = note_line.replace(tag, "")
                descr = Task.clean_line(descr)
                if action.lower() not in Lesson._actions:
                    _logger.warning(
                        "Unrecognized lesson action `%s` in %s (%s/%s: %s)",
                        action,
                        tag,
                        vault,
                        note,
                        descr,
                    )
                yield Lesson(
                    vault=vault,
                    note=note,
                    line_num=line_num,
                    tag=tag,
                    descr=descr,
                    course=course,
                    action=action,
                )

    def pretty_str(self) -> str:
        """Prepare Lesson description with colors and other decoration."""
        return (
            f"{self.vault}/{Term.underline(Term.bold(self.note))}:{self.line_num}: '{self.descr}'."
        )
