"""
This module contains tests for settings of Obsidian vaults.
"""
import dataclasses
import json
import logging

from dope.paths import V_DIRS

_logger = logging.getLogger(__name__)


def test_v_settings_hotkeys() -> None:
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

    for vault_dir in V_DIRS:
        v_name = vault_dir.stem
        _logger.info("Checking %s", v_name)
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
