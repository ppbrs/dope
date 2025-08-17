"""
Processing user requests in the dope command-line tool
that are related to dope configuration
"""
from pathlib import PosixPath
from typing import Any

from dope.config import add_vault
from dope.config import drop_vault
from dope.config import get_vault_paths


def process_arguments(args: dict[str, Any]) -> int:
    """Process arguments related to vaults configuration."""
    assert "config_vault_add" in args
    assert "config_vault_list" in args
    assert "config_vault_drop" in args

    if (paths_add := args["config_vault_add"]) and paths_add:
        assert isinstance(paths_add, list) and all(isinstance(path, str) for path in paths_add)
        for path in paths_add:
            vault_path = PosixPath(path).expanduser()
            assert vault_path.exists() and vault_path.is_dir()
            if (res := add_vault(vault_path=vault_path)):
                print(f"\nAdded '{vault_path}' to the configuration.")
            else:
                print(f"\nVault '{vault_path}' in already in the configuration.")

    if args["config_vault_list"]:
        if (vault_paths := get_vault_paths()):
            print("\nConfigured vaults:")
            for vault in vault_paths:
                print(f"\t{vault}")
        else:
            print("No configured vaults.")

    if (paths_drop := args["config_vault_drop"]) and paths_drop:
        assert isinstance(paths_drop, list) and all(isinstance(path, str) for path in paths_drop)
        for path in paths_drop:
            vault_path = PosixPath(path).expanduser()
            assert vault_path.exists() and vault_path.is_dir()
            if (res := drop_vault(vault_path=vault_path)):
                print(f"\nRemoved '{vault_path}' from the configuration.")
            else:
                print(f"\nVault '{vault_path}' in not in the configuration.")

    return 0
