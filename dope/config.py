"""
Dope configuration.

Configuration files:
* vaults.json holds a list of all vault directories
"""
import json
import logging
from pathlib import PosixPath
from typing import Any

import platformdirs

_logger = logging.getLogger(__name__)


def get_vault_paths(filter: None | list[str] = None) -> list[PosixPath]:
    """
    Return contents of vaults.json converted to a list of PosixPath objects
    and filtered according to the optional filter.
    """
    vaults_json_path = _get_vaults_json_path()
    if not vaults_json_path.exists():
        _logger.warning("Vaults configuration doesn't exist; creating.")
        _write_vaults_json([])
        return []

    with open(vaults_json_path, "rb") as fp:
        vaults = json.load(fp=fp)
    if vaults == []:
        _logger.warning("Vaults configuration is empty.")
        return []

    vault_paths = [PosixPath(vault) for vault in vaults]
    if filter is None:
        return vault_paths

    vault_paths_filtered = []
    for vault_path in vault_paths:
        for vault_substr in filter:
            if vault_substr in vault_path.name:
                vault_paths_filtered.append(vault_path)
    return vault_paths_filtered


def add_vault(vault_path: PosixPath) -> bool:
    """
    Add a vault directory to the configuration and return True;
    return False if the directory is already there.
    """
    vault_paths = get_vault_paths()
    if vault_path in vault_paths:
        return False
    vault_paths.append(vault_path)
    _write_vaults_json(vault_paths)
    return True


def drop_vault(vault_path: PosixPath) -> bool:
    """
    Remove a vault directory from the configuration and return True;
    return False if the directory is not there.
    """
    vault_paths = get_vault_paths()
    if vault_path not in vault_paths:
        return False
    vault_paths.remove(vault_path)
    _write_vaults_json(vault_paths)
    return True


def _write_vaults_json(vault_paths: list[PosixPath]) -> None:
    vaults = [str(vault_path) for vault_path in vault_paths]
    with open(_get_vaults_json_path(), "w") as fp:
        json.dump(obj=vaults, fp=fp, indent=2)


def _get_vaults_json_path() -> PosixPath:
    """
    Return the expected path of "vaults.json" file.
    """
    config_dir_path = PosixPath(platformdirs.user_config_dir("dope"))
    config_dir_path.mkdir(parents=True, exist_ok=True)
    return config_dir_path / "vaults.json"

def get_config() -> dict[str, Any]:
    config_dir_path = PosixPath(platformdirs.user_config_dir("dope"))
    config_dir_path.mkdir(parents=True, exist_ok=True)
    config_file_path = config_dir_path / "config.json"
    if not config_file_path.exists():
        with config_file_path.open("w") as fp:
            fp.write("{}\n")
        return {}
    with config_file_path.open("rb") as fp:
        config = json.load(fp=fp)
    if not isinstance(config, dict):
        raise TypeError
    return config
