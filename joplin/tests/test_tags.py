"""
The module tests tags in the local database.
"""

from joplin.common import JId32, JTag, validate_title


def test_tags_titles(db_local_tags: dict[JId32, JTag]) -> None:
    """
    Test names of all tags for validity.
    """
    for title in [tag.title for tag in db_local_tags.values()]:
        validate_title(title, True)
