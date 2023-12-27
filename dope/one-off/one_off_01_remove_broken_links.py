"""
When exporting notes to markdown, Joplin truncates file names and replaces some symbols.
This one-off script removes internal links which are impossible to fix.

Created 2023-12-26.
"""

import logging
import pathlib
import sys

from dope.markdown_link import MarkdownLink
from dope.v_note import VNote


class RemoveBrokenLinks:  # pylint: disable=too-few-public-methods
    """
    An interactive script that looks for broken links and replaces them with (broken:)
    if the user confirms.
    """

    def __init__(self) -> None:
        fmt = '%(levelname)-8s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)
        self.logger = logging.getLogger(self.__class__.__name__)

        if not sys.stdin.isatty():
            self.logger.fatal("Input doesn't come from tty.")
            raise SystemExit

    def __call__(self) -> None:
        for v_note in VNote.collect_iter(exclude_trash=True):
            self._process_note(v_note)

    @classmethod
    def _process_note(cls, v_note: VNote) -> None:
        for line_idx, line in v_note.lines_iter(lazy=False, remove_newline=True):
            # pylint: disable-next=not-an-iterable
            # (This looks like a false positive).
            for md_link in MarkdownLink.collect_iter(line=line):
                if md_link.is_external():
                    continue
                if md_link.uri.startswith("evernote:") or md_link.uri.startswith("file:"):
                    if cls._remove_if_confirmed(v_note=v_note, md_link=md_link, line_idx=line_idx,
                                                line=line):
                        return
                if md_link.uri.startswith("broken:"):
                    continue
                # Internal link.
                md_link.uri = md_link.decoded()
                md_link.uri = md_link.uri.split("#")[0]  # Remove heading.
                md_link.uri = md_link.uri.split("^")[0]  # Remove block.

                if md_link.uri.startswith("./") or (md_link.uri.startswith("../")):
                    # Internal relative link.
                    link_path_start = v_note.note_path.parent
                    link_path_end = pathlib.PosixPath(md_link.uri)
                    link_path = link_path_start / link_path_end
                else:
                    # Internal absolute link.
                    link_path_start = v_note.vault_dir
                    link_path_end = pathlib.PosixPath(md_link.uri)
                    link_path = link_path_start / link_path_end

                if not link_path.exists():
                    cls._remove_if_confirmed(v_note=v_note, md_link=md_link, line_idx=line_idx,
                                             line=line)

    @classmethod
    def _remove_if_confirmed(
            cls, v_note: VNote, md_link: MarkdownLink, line_idx: int, line: str) -> bool:
        print("============================================")
        print(f"VAULT: {v_note.vault_dir.name}")
        print(f"NOTE: {v_note.note_path.stem}")
        print(f"LINE: {line_idx}: {line}")
        print(f"NAME: {md_link.name}")

        print(f"URI: {md_link.uri}")
        print()
        print("enter y to remove it")

        if input() == "y":
            print("Replacing with (broken:)")

            data = v_note.read()
            assert md_link.uri_raw in data, f"`{md_link.uri_raw}` not found in\n{data}"
            data = data.replace(md_link.uri_raw, "broken:", 1)
            v_note.write(data)

            print("Done.\n")
            return True
        print("Skipped.\n")
        return False


if __name__ == "__main__":

    RemoveBrokenLinks()()
