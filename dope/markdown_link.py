"""
A collection of helpers that extract markdown links from notes.
"""
from __future__ import annotations

import enum
import logging
from collections.abc import Generator
from dataclasses import dataclass

_logger = logging.getLogger(__name__)


@dataclass()
class MarkdownLink:
    """
    A collection of helpers that extract markdown links from notes.
    """
    name: str
    """Human-readable name"""
    uri: str
    """Uniform resource identifier"""

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri.strip()

    @classmethod
    def collect_iter(cls, line: str) -> Generator[MarkdownLink, None, None]:
        """Find all markdown links in a given line."""
        @enum.unique
        class _State(enum.Enum):
            IDLE = enum.auto()  # We are looking for a name
            NAME = enum.auto()  # We are inside a name.
            NAME_URI = enum.auto()  # We have just finished with the name and expecting an URI.
            URI = enum.auto()  # We are inside an URI.

        state = _State.IDLE

        name: str
        uri: str
        idx_name_head: int
        idx_name_tail: int
        idx_uri_head: int
        idx_uri_tail: int
        cnt_brackets: int  # The counter of parentheses or square brackets.
        for i, char in enumerate(line):
            match state:
                case _State.IDLE:
                    if char == "[":
                        state = _State.NAME
                        idx_name_head = i + 1
                        cnt_brackets = 1
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
                            name = line[idx_name_head:idx_name_tail]
                            uri = line[idx_uri_head:idx_uri_tail]
                            yield MarkdownLink(name, uri)
        # end of collect_iter

    def decoded(self) -> str:
        """
        Decode a percent-encoded URI

        https://en.wikipedia.org/wiki/File_URI_scheme
        Characters which are not allowed in URIs, but which are allowed in filenames,
        must be percent-encoded. For example, any of "{}`^ " and all control characters.
        """
        uri_dec = str(self.uri)
        uri_dec = uri_dec.replace("%20", " ")
        uri_dec = uri_dec.replace("%28", "(")
        uri_dec = uri_dec.replace("%29", ")")
        uri_dec = uri_dec.replace("%40", "@")
        return uri_dec

    def is_external(self) -> bool:
        """Whether or not the URI points to an external resourse."""
        return (self.uri.startswith("http") or self.uri.startswith("mailto")
                or self.uri.startswith("ssh"))


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
