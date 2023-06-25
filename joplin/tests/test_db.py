"""
Testing the local Joplin database in general.
"""

# Standard library imports
import logging
import sqlite3
# Third party imports
# Local application/library imports


def test_db_encoding(db_local_conn: sqlite3.Connection) -> None:
    """
    Check that the encoding of the local database is UTF-8.
    """
    cur = db_local_conn.cursor()
    # Get the encoding, which is returned as a one-row one-column table.
    cur.execute("pragma encoding")
    encoding = cur.fetchall()[0][0]
    assert encoding == "UTF-8"


def test_db_sanity(db_local_conn: sqlite3.Connection, logger: logging.Logger) -> None:
    """
    Check that all necessary tables are present in the database.
    """
    essential_tables = ["folders", "tags", "note_tags", "resources", "notes"]
    cur = db_local_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type is 'table'")
    db_tables = [row[0] for row in cur.fetchall()]
    logger.debug("Tables in the local db: %s", db_tables)
    for table in essential_tables:
        assert table in db_tables, f"Table `{table}` is not in the database."
