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


def get_vault_paths(filter: None | list[str] = None) -> list[PosixPath]:
    """
    Return contents of vaults.json converted to a list of PosixPath objects
    and filtered according to the optional filter.
    """
    logger = logging.getLogger(__name__)
    vaults_json_path = _get_vaults_json_path()
    if not vaults_json_path.exists():
        logger.warning("Vaults configuration (%s) doesn't exist; creating.", vaults_json_path)
        _write_vaults_json([])
        return []

    with open(vaults_json_path, "rb") as fp:
        vaults = json.load(fp=fp)
    if vaults == []:
        logger.warning("Vaults configuration (%s) is empty.", vaults_json_path)
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


def get_config_path() -> PosixPath:
    config_dir_path = PosixPath(platformdirs.user_config_dir("dope"))
    config_dir_path.mkdir(parents=True, exist_ok=True)
    config_file_path = config_dir_path / "config.json"
    return config_file_path


def get_config() -> dict[str, Any]:
    """Read local dope configuration. Create default configuration if not found."""
    logger = logging.getLogger(__name__)
    config_file_path = get_config_path()
    if not config_file_path.exists():
        logger.warning("App configuration (%s) does not exist. Creating empty.", config_file_path)
        with config_file_path.open("w") as fp:
            fp.write("{}\n")
        return {}
    with config_file_path.open("rb") as fp:
        config = json.load(fp=fp)
    if not isinstance(config, dict):
        raise TypeError
    return config


def update_config(update: dict[str, Any]) -> None:
    """Add fields to the local dope configuration."""
    config_file_path = PosixPath(platformdirs.user_config_dir("dope")) / "config.json"
    assert config_file_path.exists()
    assert config_file_path.is_file()
    with config_file_path.open("rb") as fp:
        config = json.load(fp=fp)
    config.update(update)
    with config_file_path.open("w") as fp:
        json.dump(obj=config, fp=fp)
