"""
This module contains tests for Obsidian vaults.
"""

import logging
import pathlib

import pytest

from dope.markdown_link import MarkdownLink
from dope.v_note import VNote

_logger = logging.getLogger(__name__)


def _unquote(path: pathlib.PosixPath) -> pathlib.PosixPath:
    """Unquote the path."""
    path_s = str(path)
    path_s = path_s.replace("%20", " ")
    path_s = path_s.replace("%28", "(")
    path_s = path_s.replace("%29", ")")
    path_s = path_s.replace("%40", "@")
    return pathlib.PosixPath(path_s)


def _exists(link_path: pathlib.PosixPath) -> bool:
    """Unquote the path and check if file exists."""
    link_path_s = str(link_path)
    link_path_s = link_path_s.replace("%20", " ")
    link_path_s = link_path_s.replace("%28", "(")
    link_path_s = link_path_s.replace("%29", ")")
    link_path_s = link_path_s.replace("%40", "@")
    link_path = pathlib.PosixPath(link_path_s)
    return link_path.exists()


def _check_v_link(v_note: VNote, line_idx: int, md_link: MarkdownLink) -> None:
    if md_link.is_external():
        return
    if md_link.uri.startswith("evernote:"):
        # TODO: Remove them all.
        return  # Legacy Evernote link.
    if md_link.uri.startswith("file:"):
        return  # Legacy Windows link.
        # TODO: Remove them all.
    if md_link.uri.startswith("broken:"):
        return  # A link that no longer valid. This can be an ex Evernote link, Windows file,
        # or a link that was corrupted during the migration from Joplin database.
    # Internal link.
    md_link.uri = md_link.decoded()
    md_link.uri = md_link.uri.split("#")[0]  # Remove heading.
    md_link.uri = md_link.uri.split("^")[0]  # Remove block.

    if md_link.uri.startswith("./") or (md_link.uri.startswith("../")):
        # Internal relative link.
        link_path_start = v_note.note_path.parent
        link_path_end = pathlib.PosixPath(md_link.uri)
        link_path = link_path_start / link_path_end
        if not link_path.exists():
            pass
        assert link_path.exists(), \
            (f"Int.rel.link does not exist. "
             f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{md_link.uri}`.")
    else:
        # Internal absolute link.
        link_path_start = v_note.vault_dir
        link_path_end = pathlib.PosixPath(md_link.uri)
        link_path = link_path_start / link_path_end
        if not link_path.exists():
            pass
        assert link_path.exists(), \
            (f"Int.abs.link does not exist. "
             f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{md_link.uri}`.")


@pytest.mark.parametrize("nonfatal", [True])  # type: ignore[misc] # allow untyped decorator
def test_v_links(nonfatal: bool) -> None:
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
    for v_note in VNote.collect_iter(exclude_trash=True):
        with open(v_note.note_path, "r", encoding="utf8") as note_fd:
            note_lines = note_fd.readlines()
        in_code_block = False
        for line_idx, note_line in enumerate(note_lines, start=1):
            if note_line.startswith("```"):
                in_code_block = not in_code_block
            if not in_code_block:
                # pylint: disable-next=not-an-iterable
                # (This looks like a false positive).
                for md_link in MarkdownLink.collect_iter(line=note_line):
                    try:
                        num_links += 1
                        _check_v_link(v_note=v_note, line_idx=line_idx, md_link=md_link)
                    except AssertionError as err:
                        num_errors += 1
                        _logger.error("%s: %s", err.__class__.__name__,
                                      str(err).split("\n", maxsplit=1)[0])
                        if not nonfatal:
                            raise

    _logger.info("%d links were found and checked", num_links)
    if num_errors:
        _logger.error("%d errors", num_errors)
