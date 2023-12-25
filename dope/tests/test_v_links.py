"""
This module contains tests for Obsidian vaults.
"""

import logging
import pathlib
import re
from collections.abc import Generator

import pytest

_logger = logging.getLogger(__name__)


def _exists(link_path: pathlib.PosixPath) -> bool:
    """Unquote the path and check if file exists."""
    link_path_s = str(link_path)
    link_path_s = link_path_s.replace("%20", " ")
    link_path_s = link_path_s.replace("%28", "(")
    link_path_s = link_path_s.replace("%29", ")")
    link_path_s = link_path_s.replace("%40", "@")
    link_path = pathlib.PosixPath(link_path_s)
    return link_path.exists()


def _find_md_link(note_line: str) -> Generator[tuple[str, str], None, None]:
    """Find all markdown links in a given line."""
    link_ptrn = re.compile(r"\[(?P<NAME>.*?)\]\((?P<URI>.*?)\)")
    for mtch in link_ptrn.finditer(note_line):
        link_name = mtch.groupdict()["NAME"]
        link_uri = mtch.groupdict()["URI"].strip()
        yield link_name, link_uri


def _check_v_link(v_dir: pathlib.PosixPath, note_path: pathlib.PosixPath,
                  line_idx: int, link_name: str, link_uri: str) -> None:
    _ = link_name  # yet unused
    if (link_uri.startswith("http") or link_uri.startswith("mailto")
            or link_uri.startswith("ssh")):
        return  # External link.
    if link_uri.startswith("evernote:"):
        # TODO: Remove them all.
        return  # Legacy Evernote link.
    if link_uri.startswith("file:"):
        return  # Legacy Windows link.
        # TODO: Remove them all.
    if link_uri.startswith("broken:"):
        return  # A link that no longer valid. This can be an ex Evernote link, Windows file,
        # or a link that was corrupted during the migration from Joplin database.
    # Internal link.
    link_uri = link_uri.split("#")[0]  # Remove heading.
    link_uri = link_uri.split("^")[0]  # Remove block.

    if link_uri.startswith("./") or (link_uri.startswith("../")):
        # Internal relative link.
        link_path_start = note_path.parent
        link_path_end = pathlib.PosixPath(link_uri)
        link_path = link_path_start / link_path_end
        assert _exists(link_path), \
            f"Int.rel.link does not exist. Note=`{note_path}`, line={line_idx}. URI=`{link_uri}`."
    else:
        # Internal absolute link.
        link_path_start = v_dir
        link_path_end = pathlib.PosixPath(link_uri)
        link_path = link_path_start / link_path_end
        assert _exists(link_path), \
            f"Int.abs.link does not exist. Note=`{note_path}`, line={line_idx}. URI=`{link_uri}`."


@pytest.mark.parametrize("nonfatal", [True])  # type: ignore[misc] # allow untyped decorator
def test_v_links(vault_notes: list[tuple[pathlib.PosixPath, pathlib.PosixPath]],
                 nonfatal: bool) -> None:
    """
    Check the correctness of all links in notes.

    Links can be external and internal.
    External link format:
        [link_name](link_uri)

    Internal link format:
        [link_name](file_path)
        [link_name](file_path#heading)
        [link_name](file_path^block_id)
    """

    num_errors = 0
    num_links = 0
    for v_dir, note_path in vault_notes:
        with open(note_path, "r", encoding="utf8") as note_fd:
            note_lines = note_fd.readlines()
        in_code_block = False
        for line_idx, note_line in enumerate(note_lines, start=1):
            if note_line.startswith("```"):
                in_code_block = not in_code_block
            if not in_code_block:
                for link_name, link_uri in _find_md_link(note_line):
                    link_uri = link_uri.strip()
                    try:
                        num_links += 1
                        _check_v_link(v_dir=v_dir, note_path=note_path, line_idx=line_idx,
                                      link_name=link_name, link_uri=link_uri)
                    except AssertionError as err:
                        num_errors += 1
                        _logger.error("%s: %s", err.__class__.__name__,
                                      str(err).split("\n", maxsplit=1)[0])
                        if not nonfatal:
                            raise

    _logger.info("%d links were found and checked", num_links)
    if num_errors:
        _logger.error("%d errors", num_errors)
