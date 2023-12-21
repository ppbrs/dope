"""
Test notebooks.
"""

from joplin.common import JId32, JNotebook, validate_title


def test_notebooks_titles(db_local_notebooks: dict[JId32, JNotebook]) -> None:
    """
    Test titles of all notebooks for validity.
    """
    for title in [note.title for note in db_local_notebooks.values()]:
        validate_title(title)
