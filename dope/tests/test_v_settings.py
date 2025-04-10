"""
This module contains tests for settings of Obsidian vaults.
"""
import dataclasses
import json
import logging
import pathlib

from .common import vault_dirs

_logger = logging.getLogger(__name__)


@vault_dirs
def test_v_settings_hotkeys(vault_dir: pathlib.PosixPath) -> None:
    """
    Check that hotkeys.json contains all my hot keys.

    hotkeys.json looks like this example:
    {
        "app:toggle-left-sidebar": [
            {
                "modifiers": [
                    "Mod"
                ],
                "key": "0"
            }
        ],
        ...
    }
    """

    @dataclasses.dataclass
    class Hotkey:
        """Holds all information of a hotkey."""
        action: str
        modifiers: list[str]  # Mod, Alt, Shift
        key: str

        def __str__(self) -> str:
            return f"Hotkey({self.action}, {self.modifiers}, {self.key})"

        def __repr__(self) -> str:
            return self.__str__()

    # Hotkeys that must be in hotkeys.json:
    hk_exp = [
        Hotkey("app:toggle-left-sidebar", ["Mod", ], "0"),
        Hotkey("editor:insert-wikilink", ["Mod", ], "K"),
        Hotkey("app:open-vault", ["Mod", "Shift"], "V"),
        Hotkey("file-explorer:reveal-active-file", ["Mod", "Shift"], "Y"),
        Hotkey("editor:swap-line-down", ["Alt"], "ArrowDown"),
        Hotkey("editor:swap-line-up", ["Alt"], "ArrowUp"),
        Hotkey("tag-pane:open", ["Mod"], "["),
        Hotkey("outline:open", ["Mod"], "]"),
        Hotkey("insert-current-date", ["Mod", "Shift"], "D"),
        Hotkey("theme:use-dark", ["Alt", "Shift"], "D"),
        Hotkey("theme:use-light", ["Alt", "Shift"], "L"),
    ]

    v_name = vault_dir.stem
    hk_path = vault_dir / ".obsidian" / "hotkeys.json"
    assert hk_path.exists() and hk_path.is_file(), f"Could not find file `{hk_path}`."
    with open(hk_path, "rb") as hk_fp:
        hk_json_obj = json.load(fp=hk_fp)

    hk_v_arr: list[Hotkey] = []
    for action, settings in hk_json_obj.items():
        for setting in settings:
            # An item may be empty; it means that the setting is removed from the vault.
            if setting.get("modifiers") is not None and setting.get("key") is not None:
                hk_v_arr.append(Hotkey(action, setting["modifiers"], setting["key"]))
                # _logger.info(hk_v_arr[-1])

    for hk in hk_exp:
        hk_v_arr_filtered = [hk_v for hk_v in hk_v_arr if hk.action == hk_v.action]
        assert len(hk_v_arr_filtered) > 0, f"{v_name}: `{hk.action}` is not in hotkeys.json."
        assert any(hk == hk_v for hk_v in hk_v_arr_filtered), \
            f"{v_name}: {hk} is not in {hk_v_arr_filtered}."


@vault_dirs
def test_v_settings_app(vault_dir: pathlib.PosixPath) -> None:
    """
    Check that app.json contains all my preferences.
    """
    app_exp = {
        #
        # Editor settings
        #
        # Show line numbers:
        "showLineNumber": True,
        # Don't limit maximum line length:
        "readableLineLength": False,
        # Don't pair brackets and quotes automatically:
        "autoPairBrackets": False,
        # Don't pair Markdown syntax automatically (for bold, italic, etc.):
        "autoPairMarkdown": False,

        # Vim key bindings:
        "vimMode": True,
        #
        # Files and links settings
        #
        # Deleted files are moved to Obsidian trash (.trash folder):
        "trashOption": "local",
        # Default location for new attachments: in subfolder "res" under current folder:
        "attachmentFolderPath": "./res",
        # Default location for new notes: "_inbox" folder:
        "newFileLocation": "folder",
        "newFileFolderPath": "_inbox",
        # New link format: Absolute path in vault:
        "newLinkFormat": "absolute",
        # Automatically update internal links: Yes:
        "alwaysUpdateLinks": True,
        # Don't use [[Wikilinks]], generate Markdown links instead:
        "useMarkdownLinks": True,
        # Show files with all extensions: Yes:
        # Previously, a lot of useful files could not be easily found or opened.
        # Moreover, when I see all the files, it's easier to understand the situation in the directory.
        "showUnsupportedFiles": True,
    }

    v_name = vault_dir.stem
    app_path = vault_dir / ".obsidian" / "app.json"
    assert app_path.exists() and app_path.is_file(), f"Could not find file `{app_path}`."
    with open(app_path, "rb") as app_fp:
        app_vault = json.load(fp=app_fp)
    for k, v in app_exp.items():
        assert k in app_vault, \
            f"{v_name}: \"{k}\" is not in `app.json`."
        assert v == app_vault[k], \
            f"{v_name}: \"{k}\" is expected to be `{v}` but is `{app_vault[k]}`."


@vault_dirs
def test_v_settings_community_plugins(vault_dir: pathlib.PosixPath) -> None:
    """Check that all required community plugins are installed for each vault."""
    plugins_required = frozenset([
        "homepage",
        "obsidian-plantuml",
        "better-export-pdf",
        "obsidian-graphviz",
    ])

    plugins_config_path = vault_dir / ".obsidian" / "community-plugins.json"
    assert plugins_config_path.exists() and plugins_config_path.is_file(), \
        (f"Could not find file `{plugins_config_path.relative_to(vault_dir)}`; "
        "this may mean that community plugins are disabled or none of them is installed "
        f"for vault '{vault_dir.name}'.")
    with open(plugins_config_path, "rb") as fp:
        plugins_config = json.load(fp=fp)
    assert isinstance(plugins_config, list)
    assert all(isinstance(item, str) for item in plugins_config)
    plugins_installed = frozenset(plugins_config)
    plugins_missing = plugins_required - plugins_installed
    assert not plugins_missing, \
        ("Some required community plugins are not installed or installed but not enabled: "
        f"{', '.join(list(plugins_missing))}.")
