"""Contains HyperLink class."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass()
class HyperLink:
    """Base class for specific types of links."""

    name: str
    """
    Human-readable link name.
    """
    uri: str
    """
    Uniform Resource Identifier.

    Section name is stripped off.
    """
    uri_raw: str
    """
    Uniform Resource Identifier as it appears in the note.

    It includes section name.
    """
    section: str | None = field(default=None)
    """
    Optional section name referenced by the link.
    """

    def __init__(self, name: str, uri_raw: str) -> None:
        self.name = name
        self.uri_raw = uri_raw.strip()
        if "#" in uri_raw:
            self.uri, self.section = self.uri_raw.split("#")
        else:
            self.uri = self.uri_raw

    def __eq__(self, other: object) -> Any:
        assert isinstance(other, HyperLink)
        return self.name == other.name and self.uri == other.uri

    def is_external(self) -> bool:
        """Whether or not the URI points to an external resourse."""
        return (
            self.uri.startswith("http")
            or self.uri.startswith("mailto")
            or self.uri.startswith("ssh")
            or self.uri.startswith("chrome")
        )

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


def test_hyper_link_constructor() -> None:
    """Check that all links are constructed correctly."""

    @dataclass
    class TestCase:
        """Inputs and outputs of a test."""
        name: str
        """'name' that is passed to the constructor."""
        uri_raw: str
        """'uri_raw' that is passed to the constructor."""
        uri: str
        """'uri' attribute of the constructed link."""
        section: str | None
        """'section' attribute of the constructed link."""

    test_cases: list[TestCase] = [
        TestCase(name="name", uri_raw="uri", uri="uri", section=None),
        TestCase(name="name", uri_raw="uri#section", uri="uri", section="section"),
    ]

    for test_case in test_cases:
        hyper_link = HyperLink(name=test_case.name, uri_raw=test_case.uri_raw)
        assert hyper_link.name == test_case.name
        assert hyper_link.uri_raw == test_case.uri_raw
        assert hyper_link.uri == test_case.uri
        assert hyper_link.section == test_case.section
