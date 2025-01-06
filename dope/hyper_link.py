"""Contains HyperLink class."""
from dataclasses import dataclass


@dataclass()
class HyperLink:
    """Base class for specific types of links."""

    name: str
    """Human-readable link name"""
    uri: str
    """Uniform Resource Identifier"""
    uri_raw: str
    """Uniform Resource Identifier as it appears in the note"""

    def __init__(self, name: str, uri_raw: str):
        self.name = name
        self.uri_raw = uri_raw
        self.uri = uri_raw.strip()

    def __eq__(self, other) -> bool:
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
