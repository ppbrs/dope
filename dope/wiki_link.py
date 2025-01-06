"""
A collection of helpers that extract wiki links from notes.

Wiki syntax for a hyperlink is doubled square brackets:
[[https://link-url-here.org|Link text Here]]
"""
from __future__ import annotations

import enum
import logging
from collections.abc import Generator
from dataclasses import dataclass

from dope.hyper_link import HyperLink

_logger = logging.getLogger(__name__)


# @dataclass()
class WikiLink(HyperLink):
    """
    A collection of helpers that extract wiki links from notes.
    """

    @classmethod
    def collect_iter(cls, line: str) -> Generator[WikiLink, None, None]:
        """Find all wiki links in a given line."""
        @enum.unique
        class _State(enum.Enum):
            IDLE = enum.auto()  # We are waiting for the first opening square bracket.
            OPENING = enum.auto()  # We are waiting for the second opening square bracket.
            URI = enum.auto()  # We are in the URI of a wiki link.
            NAME = enum.auto()  # We are in the name of a wiki link.
            CLOSING = enum.auto()  # We are waiting for the second closing square bracket.
            INLINE_CODE = enum.auto()
            """We are inside a inline code block and all links will be ignored."""

        state = _State.IDLE
        idx_uri_head = None
        idx_uri_tail = None  # non inclusive
        idx_name_head = None
        idx_name_tail = None  # non inclusive

        for i, char in enumerate(line):
            match state:
                case _State.IDLE:
                    idx_uri_head = None
                    if char == "[":
                        state = _State.OPENING
                    if char == "`":
                        state = _State.INLINE_CODE
                case _State.OPENING:
                    if char == "[":
                        state = _State.URI
                        idx_uri_head = i + 1
                    else:
                        state = _State.IDLE
                case _State.URI:
                    if char == "]":
                        state = _State.CLOSING
                        idx_uri_tail = i
                        idx_name_head = idx_name_tail = 0
                    elif char == "|":
                        state = _State.NAME
                        idx_uri_tail = i
                        idx_name_head = i + 1
                case _State.NAME:
                    if char == "]":
                        state = _State.CLOSING
                        idx_name_tail = i
                case _State.CLOSING:
                    if char == "]":
                        name = line[idx_name_head:idx_name_tail].strip()
                        if (uri_raw := line[idx_uri_head:idx_uri_tail]):
                            yield WikiLink(name=name, uri_raw=uri_raw)
                    state = _State.IDLE
                case _State.INLINE_CODE:
                    if char == "`":
                        state = _State.IDLE


def test_wiki_link_collect() -> None:
    """Check that all wiki links are detected correctly."""
    @dataclass
    class TestCase:
        """Inputs and outputs of a test."""
        line: str
        wiki_links: list[WikiLink]

    test_cases: list[TestCase] = [
        #
        # No links
        #
        TestCase(line="", wiki_links=[]),
        TestCase(line="there-is-no-link", wiki_links=[]),
        TestCase(line="there[is[no[link", wiki_links=[]),
        TestCase(line="there[[is no link]", wiki_links=[]),
        #
        # Simple links
        #
        TestCase(
            line="before[[uri|name]]after",
            wiki_links=[WikiLink("name", "uri"), ]),
        TestCase(
            line="before[[ uri | name ]]after",
            wiki_links=[WikiLink("name", "uri"), ]),
        TestCase(
            line="before[[uri1|name1]]between[[uri2|name2]]after",
            wiki_links=[WikiLink("name1", "uri1"), WikiLink("name2", "uri2"), ]),
        TestCase(
            line="before[[uri1|name1]][[uri2|name2]]after",
            wiki_links=[WikiLink("name1", "uri1"), WikiLink("name2", "uri2"), ]),
        TestCase(
            line="before[[nameless-uri]]after",
            wiki_links=[WikiLink(name="", uri_raw="nameless-uri"),]),
        TestCase(
            line="before[[]]after",
            wiki_links=[]),
        #
        # Inside inline code
        #
        TestCase(
            line="before`[[uri]]`after",
            wiki_links=[]),
        #
        # With a section
        #
        TestCase(
            line="before[[uri#section|name]]after",
            wiki_links=[WikiLink(name="name", uri_raw="uri#section"),]),
    ]

    for test_case in test_cases:

        wiki_links = list(WikiLink.collect_iter(line=test_case.line))
        assert len(wiki_links) == len(test_case.wiki_links)
        for idx, md_link in enumerate(wiki_links):
            assert md_link == test_case.wiki_links[idx], \
                f"Expected {test_case.wiki_links[idx]}. Got {md_link}."
