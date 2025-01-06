"""
A collection of helpers that extract markdown links from notes.

Markdown syntax for a hyperlink is square brackets followed by parentheses:
[Link text Here](https://link-url-here.org)

Markdown links differ from Wiki links:
* [[link]] is seen as "link" in text and links to page "link".
* [[a|b]] appears as "b" but links to page "a".
"""
from __future__ import annotations

import enum
import logging
from collections.abc import Generator
from dataclasses import dataclass

from dope.hyper_link import HyperLink

_logger = logging.getLogger(__name__)


# @dataclass()
class MarkdownLink(HyperLink):
    """
    A collection of helpers that extract markdown links from notes.
    """

    @classmethod
    def collect_iter(cls, line: str) -> Generator[MarkdownLink, None, None]:
        """Find all markdown links in a given line."""
        @enum.unique
        class _State(enum.Enum):
            IDLE = enum.auto()  # We are looking for the opening square bracket.
            NAME = enum.auto()  # We are inside a name.
            NAME_URI = enum.auto()  # We have just finished with the name and expecting an URI.
            URI = enum.auto()  # We are inside an URI.
            CODE = enum.auto()  # We are inside of an inline code snippet.

        state = _State.IDLE

        name: str
        uri: str
        idx_name_head: int = 0
        idx_name_tail: int = 0
        idx_uri_head: int = 0
        idx_uri_tail: int = 0
        cnt_brackets: int = 0  # The counter of parentheses or square brackets.
        for i, char in enumerate(line):
            match state:
                case _State.IDLE:
                    if char == "[":
                        state = _State.NAME
                        idx_name_head = i + 1
                        cnt_brackets = 1
                    elif char == "`":
                        state = _State.CODE
                case _State.NAME:
                    if char == "[":
                        cnt_brackets += 1
                    elif char == "]":
                        cnt_brackets -= 1
                        if cnt_brackets == 0:
                            idx_name_tail = i
                            state = _State.NAME_URI
                case _State.NAME_URI:
                    if char == "(":
                        cnt_brackets = 1
                        idx_uri_head = i + 1
                        state = _State.URI
                    else:
                        state = _State.IDLE
                case _State.URI:
                    if char == "(":
                        cnt_brackets += 1
                    elif char == ")":
                        cnt_brackets -= 1
                        if cnt_brackets == 0:
                            idx_uri_tail = i
                            state = _State.IDLE
                            name = line[idx_name_head:idx_name_tail].strip()
                            uri = line[idx_uri_head:idx_uri_tail]
                            yield MarkdownLink(name, uri)
                case _State.CODE:
                    if char == "`":
                        state = _State.IDLE
        # end of collect_iter


def test_markdown_link_collect() -> None:
    """Check that all links are detected correctly."""
    @dataclass
    class TestCase:
        """Inputs and outputs of a test."""
        line: str
        md_links: list[MarkdownLink]

    test_cases: list[TestCase] = [
        #
        # No links
        #
        TestCase(line="", md_links=[]),
        TestCase(line="there-is-no-link", md_links=[]),
        TestCase(line="there[is[no[link", md_links=[]),
        TestCase(line="[name] (uri)", md_links=[]),
        TestCase(line="Use `std::bitset<>::opeator[]()`.", md_links=[]),
        #
        # Simple links
        #
        TestCase(line="before[name](uri)after",
                 md_links=[MarkdownLink("name", "uri"), ]),
        TestCase(line="before[name1](uri1)between[name2](uri2)after",
                 md_links=[MarkdownLink("name1", "uri1"),
                           MarkdownLink("name2", "uri2"), ]),
        TestCase(line="before[empty-uri]()after",
                 md_links=[MarkdownLink("empty-uri", ""),]),
        TestCase(line="before[name](uri(parens))after",
                 md_links=[MarkdownLink("name", "uri(parens)"),]),
        #
        # Links with brackets
        #
        TestCase(line="before[name[1[2[3]2]1]](uri(1(2(3)2)1))after",
                 md_links=[MarkdownLink("name[1[2[3]2]1]", "uri(1(2(3)2)1)"),]),
    ]

    for test_case in test_cases:

        md_links = list(MarkdownLink.collect_iter(line=test_case.line))
        assert len(md_links) == len(test_case.md_links)
        for idx, md_link in enumerate(md_links):
            assert md_link == test_case.md_links[idx], f"{md_link} != {test_case.md_links[idx]}"
