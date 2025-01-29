"""Common code for tests."""
import pytest
from dope.paths import V_DIRS

# Notes and other files cannot contain these symbols:
RESERVED_SYMBOLS = ["`", "[", "]", "'", "\""]

# pytest parametrization iterating over all configured vaults.
vault_dirs = pytest.mark.parametrize(
    argnames="vault_dir",
    argvalues=V_DIRS,
    ids=[v_dir.name for v_dir in V_DIRS],
)
