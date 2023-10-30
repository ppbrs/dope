"""
The module tests tags in the local database.
"""

# Standard library imports
# Third party imports
# Local application/library imports
import common  # pylint: disable=import-error


def test_tags_titles(db_local_tags: dict[common.JId32, common.JTag]):
    """
    Test names of all tags for validity.
    """
    for title in [tag.title for tag in db_local_tags.values()]:
        common.validate_title(title, True)
