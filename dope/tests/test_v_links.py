"""
This module contains tests for Obsidian vaults.
"""
import enum
import logging
import pathlib

from dope.hyper_link import HyperLink
from dope.markdown_link import MarkdownLink
from dope.v_note import VNote
from dope.wiki_link import WikiLink

from .common import vault_dirs

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


class HyperLinkType(enum.Enum):
    BROKEN = enum.auto()
    EXTERNAL = enum.auto()
    INTERNAL = enum.auto()


def _check_v_link_validity(
    v_note: VNote,
    line_idx: int,
    hyper_link: HyperLink
) -> HyperLinkType:
    """
    Check that the link points to an existing file or note.

    For notes, the .md extension may be omitted.

    :param hyper_link: hyper_link.uri may be changed if the link is relative.
    """
    if hyper_link.is_external():
        return HyperLinkType.EXTERNAL
    if hyper_link.uri.startswith("broken:"):
        return HyperLinkType.BROKEN  # A link that no longer valid. This can be an ex Evernote link, Windows file,
        # or a link that was corrupted during the migration from Joplin database.
    assert not hyper_link.uri.startswith("evernote:"), \
        (f"Legacy Evernote link."
         f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{hyper_link.uri}`.")
    assert not hyper_link.uri.startswith("file:"), \
        (f"Legacy Windows link."
         f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{hyper_link.uri}`.")
    # Internal link.
    hyper_link.uri = hyper_link.decoded()
    # hyper_link.uri = hyper_link.uri.split("#")[0]  # Remove heading.
    # hyper_link.uri = hyper_link.uri.split("^")[0]  # Remove block.

    if hyper_link.uri.startswith("./") or (hyper_link.uri.startswith("../")):
        # Internal relative link.
        # e.g. '../../_resources/ecfa7cf0d551039c07863c011e388191.png'
        link_path_start = v_note.note_path.parent
        link_path_end_as_is = pathlib.PosixPath(hyper_link.uri)
        link_path_as_is = (link_path_start / link_path_end_as_is).resolve()
        link_path_end_dot_md = pathlib.PosixPath(hyper_link.uri + ".md")  # The link may be a note.
        link_path_dot_md = link_path_start / link_path_end_dot_md
        if link_path_as_is.exists():
            hyper_link.uri = str(link_path_as_is)
            return HyperLinkType.INTERNAL
        if link_path_dot_md.exists():
            return HyperLinkType.INTERNAL
        raise ValueError(
            "Int.rel.link does not exist. "
            f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{hyper_link.uri}`."
        )
    else:
        # Internal absolute link.
        link_path_start = v_note.vault_dir
        link_path_end_as_is = pathlib.PosixPath(hyper_link.uri)
        link_path_as_is = link_path_start / link_path_end_as_is
        link_path_end_dot_md = pathlib.PosixPath(hyper_link.uri + ".md")
        link_path_dot_md = link_path_start / link_path_end_dot_md
        assert link_path_as_is.exists() or link_path_dot_md.exists(), \
            (f"Int.abs.link does not exist. "
             f"Note=`{v_note.note_path}`, line={line_idx}. URI=`{hyper_link.uri}`.")
        return HyperLinkType.INTERNAL


@vault_dirs
def test_v_links_validity(vault_dir: pathlib.PosixPath) -> None:
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

    num_md_links = 0
    num_wk_links = 0
    for v_note in VNote.collect_iter(vault_dirs=[vault_dir], exclude_trash=True):
        for line_idx, note_line in v_note.lines_iter(lazy=True, remove_newline=True):
            for md_link in MarkdownLink.collect_iter(line=note_line):
                num_md_links += 1
                _check_v_link_validity(v_note=v_note, line_idx=line_idx, hyper_link=md_link)

            for wk_link in WikiLink.collect_iter(line=note_line):
                num_wk_links += 1
                _check_v_link_validity(v_note=v_note, line_idx=line_idx, hyper_link=wk_link)

    _logger.info("%d Markdown links were found and checked", num_md_links)
    _logger.info("%d Wiki links were found", num_wk_links)


@vault_dirs
def test_v_links_resources(vault_dir: pathlib.PosixPath) -> None:
    """
    Check that a resource referenced by a hyperlink is the local "res" directory.
    """

    num_res_checked = 0
    num_res_errors = 0
    for v_note in VNote.collect_iter(vault_dirs=[vault_dir], exclude_trash=True):
        for line_idx, note_line in v_note.lines_iter(lazy=True, remove_newline=True):
            for hyper_link in MarkdownLink.collect_iter(line=note_line):
                if pathlib.Path(hyper_link.uri).suffix == ".md":
                    continue  # Ignore links to notes.
                _logger.debug("hyper_link '%s'.", hyper_link.uri)
                num_res_checked += 1
                match _check_v_link_validity(v_note=v_note, line_idx=line_idx, hyper_link=hyper_link):
                    case HyperLinkType.EXTERNAL:
                        pass
                    case HyperLinkType.INTERNAL:
                        note_dir_rpath = v_note.note_path.relative_to(v_note.vault_dir).parent
                        note_res_rpath = note_dir_rpath / "res"
                        link_dir_path = pathlib.Path(hyper_link.uri).parent
                        if link_dir_path.is_absolute():
                            link_dir_rpath = link_dir_path.relative_to(v_note.vault_dir)
                        else:
                            link_dir_rpath = link_dir_path
                        if note_res_rpath != link_dir_rpath:
                            _logger.error(
                                "%s: line %d: Resource ('%s') is not in the local 'res' directory ('%s').",
                                v_note.note_path.name, line_idx, hyper_link.uri, note_res_rpath)
                            _logger.debug("res BAD: '%s', file in '%s'.", note_res_rpath, link_dir_path)
                            num_res_errors += 1
                        else:
                            _logger.debug("res GOOD: '%s', file in '%s'.", note_res_rpath, link_dir_path)


    _logger.info("%d hyper-links were found and checked, %d problems.", num_res_checked, num_res_errors)
