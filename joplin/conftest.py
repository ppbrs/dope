""" This module provides fixtures for Joplin tests."""

# Standard library imports
import logging
import sqlite3
# Third party imports
import pytest
# Local application/library imports
from joplin.common import FPATH_LOCAL_DB, get_db_local_notebooks, get_db_local_notes, \
    get_db_local_tags, get_db_local_used_resources, JId32, JNote, JNotebook, JResource, JTag


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def logger() -> logging.Logger:
    """ Logger fixture.
    Note that the logger name is conftest.py when using this fixture, which may be misleading,
    so adding the test function name to the message format is recommended.
    """
    return logging.getLogger(__name__)


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def db_local_conn() -> sqlite3.Connection:
    """ Open the local database and provide a connection object. """
    with sqlite3.connect(database=f"file:{FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        yield db_conn


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def db_local_notes() -> dict[JId32, JNote]:
    """
    Returns a dictionary with notes' IDs as keys and JNote objects as values.
    """
    return get_db_local_notes()


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def db_local_notebooks() -> dict[JId32, JNotebook]:
    """
    Returns a dictionary with notebooks's id32 as key and Notebook object as value.
    """
    return get_db_local_notebooks()


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def db_local_used_resources() -> dict[JId32, JResource]:
    """
    Returns a dictionary with notebooks's id32 as key and Resource object as value.
    """
    return get_db_local_used_resources()


@pytest.fixture  # type: ignore[misc] # Untyped decorator makes function untyped
def db_local_tags() -> dict[JId32, JTag]:
    """
    Returns a dictionary with tags's id32 as key and Resource object as value.
    """
    return get_db_local_tags()
