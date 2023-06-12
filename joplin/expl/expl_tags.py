""" Check get_db_local_tags(). """

# Standard library imports
import pprint
import sys
# Third party imports
# Local application/library imports
sys.path.append("..")
from joplin.common import get_db_local_tags  # pylint: disable=wrong-import-position


if __name__ == "__main__":

    pp = pprint.PrettyPrinter(indent=4, width=70,)
    tags = get_db_local_tags()
    pp.pprint(tags)
