"""Contains VNote class only."""
from __future__ import annotations

import logging
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import PosixPath

from dope.paths import V_DIRS

_logger = logging.getLogger(__name__)


@dataclass
class VNote:
    """Encapsulates all the information about a note in a vault."""
    vault_dir: PosixPath
    note_path: PosixPath

    @classmethod
    def collect(cls, exclude_trash: bool) -> list[VNote]:
        """
        Walk through all vaults and get all notes.
        """
        v_notes: list[VNote] = []
        for v_note in cls.collect_iter(exclude_trash):
            v_notes.append(v_note)
        _logger.debug("Collected %d vault notes from %d vaults", len(v_notes), len(V_DIRS))
        return v_notes

    @classmethod
    def collect_iter(cls, exclude_trash: bool) -> Generator[VNote, None, None]:
        """
        Walk through all vaults and get all notes.
        """
        for vault_dir in V_DIRS:
            for note_path in vault_dir.rglob("*.md"):
                assert note_path.is_file()
                if exclude_trash and ".trash" in note_path.parts:
                    continue
                yield VNote(vault_dir, note_path)
