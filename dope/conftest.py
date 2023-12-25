""" This module provides fixtures for database and vault tests."""

import pathlib

import pytest

from dope.paths import V_DIRS


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def vault_notes() -> list[tuple[pathlib.PosixPath, pathlib.PosixPath]]:
    """
    Returns a list of tuples.
    The first element is the path to the vault.
    The second element is the path to the note.
    """
    paths = []
    for v_dir in V_DIRS:
        for note_path in v_dir.rglob("*.md"):
            assert note_path.is_file()
            paths.append((v_dir, note_path))
    return paths
