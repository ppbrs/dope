"""Terminal utilities"""


class Term:
    """
    A collection of helpers for coloring, highlighting, boldifying, and underlining
    text output in the terminal.
    """

    _PURPLE = "\033[95m"
    _CYAN = "\033[96m"
    _DARKCYAN = "\033[36m"
    _BLUE = "\033[94m"
    _GREEN = "\033[92m"
    _YELLOW = "\033[93m"
    _RED = "\033[91m"
    _BOLD = "\033[1m"
    _UNDERLINE = "\033[4m"
    _END = "\033[0m"

    @classmethod
    def underline(cls, text: str) -> str:
        """Convert text to underlined text."""
        return cls._UNDERLINE + text + cls._END

    @classmethod
    def bold(cls, text: str) -> str:
        """Convert text to bold text."""
        return cls._BOLD + text + cls._END

    @classmethod
    def red(cls, text: str) -> str:
        """Output the text in red color."""
        return cls._RED + text + cls._END

    @classmethod
    def green(cls, text: str) -> str:
        """Output the text in green color."""
        return cls._GREEN + text + cls._END

    @classmethod
    def yellow(cls, text: str) -> str:
        """Output the text in yellow color."""
        return cls._YELLOW + text + cls._END

    @classmethod
    def cyan(cls, text: str) -> str:
        """Output the text in cyan color."""
        return cls._CYAN + text + cls._END
