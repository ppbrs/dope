"""Contains VNote class only."""
from __future__ import annotations

import logging
import pathlib
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import PosixPath

_logger = logging.getLogger(__name__)


@dataclass
class VNote:
    """Encapsulates all the information about a note in a vault."""
    vault_dir: PosixPath
    note_path: PosixPath

    @classmethod
    def collect(cls, vault_dirs: list[pathlib.PosixPath], exclude_trash: bool) -> list[VNote]:
        """
        Walk through all vaults and get all notes.
        """
        v_notes: list[VNote] = []
        for v_note in cls.collect_iter(vault_dirs=vault_dirs, exclude_trash=exclude_trash):
            v_notes.append(v_note)
        _logger.debug("Collected %d vault notes from %d vaults", len(v_notes), len(vault_dirs))
        return v_notes

    @classmethod
    def collect_iter(
        cls, vault_dirs: list[pathlib.PosixPath], exclude_trash: bool
    ) -> Generator[VNote, None, None]:
        """
        Walk through all vaults and get all notes.
        """
        for vault_dir in vault_dirs:
            for note_path in vault_dir.rglob("*.md"):
                assert note_path.is_file()
                if exclude_trash and ".trash" in note_path.parts:
                    continue
                yield VNote(vault_dir, note_path)

    def lines_iter(self, lazy: bool, remove_newline: bool) -> Generator[tuple[int, str], None, None]:
        """
        Walk through all lines in a note except code lines.

        Note that the index of the line is one-based.

        The greedy, i.e. not lazy, variant closes the file before yielding, thus it should
        be used when you want to rewrite the file while analyzing its lines.
        """
        in_code_block = False
        if lazy:
            with open(self.note_path, "r", encoding="utf8") as note_fd:
                line_idx = 1
                while (note_line := note_fd.readline()) != "":
                    # f.readline() reads a single line from the file;
                    # a newline character (\n) is left at the end of the string,
                    # and is only omitted on the last line of the file if the file doesn’t end
                    # in a newline. This makes the return value unambiguous; if f.readline()
                    # returns an empty string, the end of the file has been reached,
                    # while a blank line is represented by '\n', a string containing only
                    # a single newline.
                    if note_line.startswith("```"):
                        in_code_block = not in_code_block
                    if not in_code_block:
                        if remove_newline:
                            note_line = note_line.replace("\n", "").replace("\r", "")
                        yield line_idx, note_line
                    line_idx += 1

        else:
            with open(self.note_path, "r", encoding="utf8") as note_fd:
                note_lines = note_fd.readlines()
            for line_idx, note_line in enumerate(note_lines, start=1):
                if note_line.startswith("```"):
                    in_code_block = not in_code_block
                if not in_code_block:
                    if remove_newline:
                        note_line = note_line.replace("\n", "").replace("\r", "")
                    yield line_idx, note_line

    def read(self) -> str:
        """Read the whole note."""
        with open(self.note_path, "r", encoding="utf8") as note_fd:
            return note_fd.read()

    def write(self, data: str) -> None:
        """Write the whole note."""
        with open(self.note_path, "w", encoding="utf8") as note_fd:
            note_fd.write(data)
