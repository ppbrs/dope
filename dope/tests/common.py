"""Common code for tests."""
import argparse
from pathlib import PosixPath

import pytest

from dope.config import get_vault_paths

# Notes and other files cannot contain these symbols:
RESERVED_SYMBOLS = ["`", "[", "]", "'", "\""]

def _get_vault_paths_tests() -> list[PosixPath]:
    """
    A wrapper around get_vault_paths() that filters vault names.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", nargs="*", action="store")
    pytest_args, _ = parser.parse_known_args()
    return get_vault_paths(filter=pytest_args.vault)

# pytest parametrization iterating over all configured vaults.
vault_dirs = pytest.mark.parametrize(
    argnames="vault_dir",
    argvalues=(v_dirs := _get_vault_paths_tests()),
    ids=[v_dir.name for v_dir in v_dirs],
)
