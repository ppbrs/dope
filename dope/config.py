"""
Dope configuration.

Configuration files:
* vaults.json holds a list of all vault directories
"""
import json
import logging
from pathlib import PosixPath

import platformdirs

_logger = logging.getLogger(__name__)


def get_vault_paths() -> list[PosixPath]:
    """
    Return contents of vaults.json converted to a list of PosixPath objects.
    """
    vaults_json_path = _get_vaults_json_path()
    if vaults_json_path.exists():
        with open(vaults_json_path, "rb") as fp:
            vaults = json.load(fp=fp)
        if vaults == []:
            _logger.warning("Vaults configuration is empty.")
        vault_paths = [PosixPath(vault) for vault in vaults]
    else:
        _logger.warning("Vaults configuration doesn't exist; creating.")
        vault_paths = []
        _write_vaults_json(vault_paths)
    return vault_paths


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
