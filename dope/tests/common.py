"""Common code for tests."""
import pytest

from dope.config import get_vault_paths

# Notes and other files cannot contain these symbols:
RESERVED_SYMBOLS = ["`", "[", "]", "'", "\""]

# pytest parametrization iterating over all configured vaults.
vault_dirs = pytest.mark.parametrize(
    argnames="vault_dir",
    argvalues=get_vault_paths(),
    ids=[v_dir.name for v_dir in get_vault_paths()],
)
