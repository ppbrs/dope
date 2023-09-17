"""
Test notebooks.
"""

import common


def test_notebooks_titles(db_local_notebooks: dict[common.JId32, common.JNotebook]):
    """
    Test titles of all notebooks for validity.
    """
    for title in [note.title for note in db_local_notebooks.values()]:
        common.validate_title(title)
