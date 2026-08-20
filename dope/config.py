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


def get_vault_paths(filter: None | list[str] = None) -> list[PosixPath]:
    """
    Return contents of vaults.json converted to a list of PosixPath objects
    and filtered according to the optional filter.
    """
    logger = logging.getLogger(__name__)
    config = get_config()
    vaults = config.get("vaults", None)
    if vaults is None:
        raise NotImplementedError
    else:
        vault_paths = [PosixPath(v).expanduser() for v in vaults]

    if filter is None:
        return vault_paths

    vault_paths_filtered = []
    for vault_path in vault_paths:
        for vault_substr in filter:
            if vault_substr in vault_path.name:
                vault_paths_filtered.append(vault_path)
    return vault_paths_filtered
