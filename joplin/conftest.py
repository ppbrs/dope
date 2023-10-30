""" This module provides fixtures for Joplin tests."""

# Standard library imports
import logging
import sqlite3
# Third party imports
import pytest
# Local application/library imports
import common


@pytest.fixture
def logger() -> logging.Logger:
    """ Logger fixture.
    Note that the logger name is conftest.py when using this fixture, which may be misleading,
    so adding the test function name to the message format is recommended.
    """
    return logging.getLogger(__name__)


@pytest.fixture
def db_local_conn() -> sqlite3.Connection:
    """ Open the local database and provide a connection object. """
    with sqlite3.connect(database=f"file:{common.FPATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        yield db_conn


@pytest.fixture
def db_local_notes() -> dict[common.JId32, common.JNote]:
    """
    Returns a dictionary with notes' IDs as keys and JNote objects as values.
    """
    return common.get_db_local_notes()


@pytest.fixture
def db_local_notebooks() -> dict[common.JId32, common.JNotebook]:
    """
    Returns a dictionary with notebooks's id32 as key and Notebook object as value.
    """
    return common.get_db_local_notebooks()


@pytest.fixture
def db_local_tags() -> dict[common.JId32, common.JTag]:
    """
    Returns a dictionary with tags's id32 as key and Resource object as value.
    """
    return common.get_db_local_tags()
