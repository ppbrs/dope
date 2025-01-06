"""
A collection of helpers that extract wiki links from notes.

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

_logger = logging.getLogger(__name__)


@dataclass()
class WikiLink:
    """
    A collection of helpers that extract wiki links from notes.
    """
    name: str
    """Human-readable link name"""
    uri: str
    """Uniform Resource Identifier"""
    uri_raw: str
    """Uniform Resource Identifier as it appears in the note"""

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri_raw = uri
        self.uri = uri.strip()

    @classmethod
    def collect_iter(cls, line: str) -> Generator[WikiLink, None, None]:
        """Find all wiki links in a given line."""
 

def test_wiki_link_collect() -> None:
    """Check that all links are detected correctly."""
    @dataclass
    class TestCase:
        """Inputs and outputs of a test."""
        line: str
        wiki_links: list[WikiLink]

    test_cases: list[TestCase] = [
        #
        # No links
        #
        # TestCase(line="", wiki_links=[]),
        # TestCase(line="there-is-no-link", wiki_links=[]),
        # TestCase(line="there[is[no[link", wiki_links=[]),
        # TestCase(line="[name] (uri)", wiki_links=[]),
        #
        # Simple links
        #
        # TestCase(line="before[name](uri)after",
        #          wiki_links=[WikiLink("name", "uri"), ]),
        # TestCase(line="before[name1](uri1)between[name2](uri2)after",
        #          wiki_links=[WikiLink("name1", "uri1"),
        #                    WikiLink("name2", "uri2"), ]),
        # TestCase(line="before[empty-uri]()after",
        #          wiki_links=[WikiLink("empty-uri", ""),]),
        # TestCase(line="before[name](uri(parens))after",
        #          wiki_links=[WikiLink("name", "uri(parens)"),]),
        #
        # Links with brackets
        #
        # TestCase(line="before[name[1[2[3]2]1]](uri(1(2(3)2)1))after",
        #          wiki_links=[WikiLink("name[1[2[3]2]1]", "uri(1(2(3)2)1)"),]),
    ]

    for test_case in test_cases:

        wiki_links = list(WikiLink.collect_iter(line=test_case.line))
        assert len(wiki_links) == len(test_case.wiki_links)
        for idx, md_link in enumerate(wiki_links):
            assert md_link == test_case.wiki_links[idx], f"{md_link} != {test_case.wiki_links[idx]}"