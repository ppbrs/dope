""" JTask class and its children.
"""
from __future__ import annotations

# Standard library imports
from dataclasses import dataclass
from datetime import date, timedelta
import logging
import re
# Third party imports
# Local application/library imports


@dataclass
class JTask:
    """ All useful data of an action. """
    title: str  # The title of the containing note.
    line: str  # Task line with removed useless symbols.
    priority: int  # 1, 2, 3
    priority_ok: bool
    deadline: date
    deadline_ok: bool
    marks: set[str]  # Additional marks like @evergreen

    # todo: make it an abstract class.

    def __post_init__(self):
        self._clean_line()

    def get_days_to_dealine(self) -> int:
        """ Calculate number of days till deadline. """
        return (self.deadline - date.today()).days

    @classmethod
    def parse_task(cls: type[JNext] | type[JWait] | type[JNow],
                   title: str, line: str) -> None | JTask:
        """ If there is no @nxt/@w8/@now marker in the line, return None.
        Otherwise, parse it.
        """
        # pylint: disable=too-many-branches, too-many-statements
        if cls in (JNext, JWait, JNow):
            prefix = cls.PREFIX
            if prefix not in line:
                return None
            mtch = cls.PTRN.match(line)
        else:
            raise TypeError

        if mtch is not None:
            line_res = line.replace(mtch.groups()[0], "")
            marker = (mtch.groups()[0]).strip()
            marks = set()

            marker = marker.replace(prefix, "")
            if marker.startswith(":"):
                marker = marker[1:]

            params = marker.split(":")
            if len(params) == 0:
                priority = 3
                priority_ok = False
                deadline = date.today() + timedelta(days=1)
                deadline_ok = False
            else:
                prio_str = params[0]
                if prio_str.startswith("p"):
                    prio_str = prio_str[1:]
                try:
                    priority = int(prio_str)
                    priority_ok = True
                except ValueError:
                    priority = 3
                    priority_ok = False
                assert priority in [1, 2, 3]

                deadline_ok = True
                if len(params) > 1:
                    dstr = params[1]
                    if dstr == "asap":
                        deadline = date.today()
                    elif (mtch := re.search(r"(\d\d\d\d)-?(\d\d)-?(\d\d)", dstr)) is not None:
                        year, month, day = mtch.groups()
                        deadline = date(year=int(year), month=int(month), day=int(day))
                    elif dstr == "":
                        deadline = date.today() + timedelta(days=1)
                        deadline_ok = False
                    else:
                        raise ValueError(f"Cannot parse deadline in `{line}`")
                else:
                    deadline = date.today() + timedelta(days=1)
                    deadline_ok = False

            # Separate marks:
            for word in line_res.split():
                if word.startswith("@") and word.endswith(":"):
                    marks.add(word)
            for mark in marks:
                line_res = line_res.replace(mark, "")

            return cls(title=title, line=line_res,
                       priority=priority, priority_ok=priority_ok,
                       deadline=deadline, deadline_ok=deadline_ok,
                       marks=marks)
        return None

    def _clean_line(self) -> None:
        """
        Clean up the line describing the task.
        """
        line = self.line.strip()
        line = line.replace("- [ ]", "")
        line = line.replace("\t", " ")
        line = line.replace("    ", " ")
        line = line.replace("   ", " ")
        line = line.replace("  ", " ")
        line = line.strip()
        line = line[1:] if line.startswith("*") or line.startswith("-") \
            else line
        line = line.strip()
        self.line = line


@dataclass
class JNext(JTask):
    """ All useful data of a next action. """
    PREFIX = "@nxt"
    PTRN = re.compile(r".*(\@nxt.*?)(\s.*|$)")


@dataclass
class JWait(JTask):
    """ All useful data of a pending action. """
    PREFIX = "@w8"
    PTRN = re.compile(r".*(\@w8.*?)(\s.*|$)")


@dataclass
class JNow(JTask):
    """ All useful data of the actual action. """
    PREFIX = "@now"
    PTRN = re.compile(r".*(\@now.*?)(\s.*|$)")


def test_jtask_parse_task(logger: logging.Logger):
    """ Extensively test the function JTask.parse_task(...)
    """

    # todo: this test is not run when pytest is envoked from the root directory of the project.

    @dataclass
    class TestCase:
        """ Store test inputs and outputs. """
        line: str
        clss: type[JNext] | type[JWait] | type[JNow]
        """ Class to parse for. """
        res: type[JNext] | type[JWait] | type[JNow]

    test_cases = [
        # ------------------------------------------------------------------------------------------
        TestCase(line="line", clss=JNow, res=None),
        # ------------------------------------------------------------------------------------------
        TestCase(
            line="@nxt:p3:20230601: Carry out May 2023 tasks.", clss=JNext,
            res=JNext(line="Carry out May 2023 tasks.",
                      title="", priority=3, priority_ok=True,
                      deadline=date(2023, 6, 1), deadline_ok=True, marks=set())),
        TestCase(
            line="@nxt::2023-06-03", clss=JNext,
            res=JNext(line="",
                      title="", priority=3, priority_ok=False,
                      deadline=date(2023, 6, 3), deadline_ok=True, marks=set())),
        # # ------------------------------------------------------------------------------------------
        TestCase(
            line="@nxt", clss=JNext,
            res=JNext(line="", title="", priority=3, priority_ok=False,
                      deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        TestCase(
            line="@w8", clss=JWait,
            res=JWait(line="", title="", priority=3, priority_ok=False,
                      deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        TestCase(
            line="@now", clss=JNow,
            res=JNow(line="", title="", priority=3, priority_ok=False,
                     deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        # # ------------------------------------------------------------------------------------------
        TestCase(
            line="@nxt abcdefgh", clss=JNext,
            res=JNext(line="abcdefgh", title="", priority=3, priority_ok=False,
                      deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        TestCase(
            line="@nxt: abcdefgh", clss=JNext,
            res=JNext(line="abcdefgh", title="", priority=3, priority_ok=False,
                      deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        TestCase(
            line="@nxt:: abcdefgh", clss=JNext,
            res=JNext(line="abcdefgh", title="", priority=3, priority_ok=False,
                      deadline=date.today() + timedelta(days=1), deadline_ok=False, marks=set())),
        # ------------------------------------------------------------------------------------------
    ]

    for i, test_case in enumerate(test_cases):
        res = test_case.clss.parse_task(title="", line=test_case.line)
        if res != test_case.res:
            logger.error("test_case[#`%d] failed: %s", i, str(test_case))
            assert test_case.res.__class__ == res.__class__, \
                f"Class is wrong: expected `{test_case.res.__class__}` != parsed `{res.__class__}`"
            for field in fields(test_case.res.__class__):
                left = getattr(test_case.res, field.name)
                right = getattr(res, field.name)
                assert left == right, \
                    f"`{field.name}` is wrong: expected `{left}` != parsed `{right}`"
