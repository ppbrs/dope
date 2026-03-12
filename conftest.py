"""pytest configuration file"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Define custom command-line options."""

    # Allow passing optional list of vaults to pytests.
    parser.addoption(
        # pytest doesn't allow using "-v" (lowercase shortoptions reserved)
        "--vault",
        nargs="*",  # The result is None | list[str].
        action="store",
    )
