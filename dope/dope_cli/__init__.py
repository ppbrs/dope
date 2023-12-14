"""
dope_cli submodule
"""
import sys


def dope_cli():
    """
    Temporary function that does nothing.
    It's purpose is to check that dope_cli can be invoked from a terminal as "d".
    """
    print("dope CLI")
    print(f"Arguments: {sys.argv[1:]}")
    return 0
