"""
Various helpers used by JCli application.
"""
# Standard library imports
# Third party imports
# Local application/library imports
import common
from jtask import JTask, JNext, JWait, JNow


class Tty:
    """ Terminal color sequences. """
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @classmethod
    def underline(cls, text: str) -> str:
        """ Convert text to underlined text. """
        return cls.UNDERLINE + text + cls.END

    @classmethod
    def bold(cls, text: str) -> str:
        """ Convert text to bold text. """
        return cls.BOLD + text + cls.END

    @classmethod
    def print_sep(cls) -> None:
        """ Print a distint line that acts like a separator of topics. """
        print(f"{Tty.DARKCYAN}"
              "================================================================"
              "================================================================"
              f"{Tty.END}")


def collect_tasks() -> list[JTask]:
    """ Find all tasks in the database.
    """
    jnotes = common.get_db_local_notes().values()
    jtasks: list[JTask] = []
    for jnote in jnotes:
        for line in jnote.body.split("\n"):
            for clss in (JNext, JWait, JNow):
                jtask = clss.parse_task(title=jnote.title, line=line)
                if jtask is not None:
                    jtasks.append(jtask)
    return jtasks
