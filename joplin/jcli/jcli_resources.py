"""
Executing user's requests related to resources.
"""

# Standard library imports
import os
from pathlib import PosixPath
import time
from typing import Any
# Third party imports
from PIL import Image, UnidentifiedImageError
# Local application/library imports
import common


class JCliResources:
    """
    Executing user's requests related to resources.
    """

    def __init__(self) -> None:
        self.ret_val = 0
        self.resources: dict[common.JId32, common.JResource] = common.get_db_local_used_resources()

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to resources.
        """
        if (id32_hint := args.get("view_resource")) is not None:
            candidates = self._get_id32_candidates(id32_hint)
            if len(candidates) == 1:
                self._view_resource(id32=candidates[0])
            elif len(candidates) == 0:
                print(f"No resources starting with `{id32_hint}` were found.")
            else:
                print(f"{len(candidates)} candidates were found.")
                for id32 in candidates:
                    self._info_resource(id32=id32)
        if (id32_hint := args.get("edit_resource")) is not None:
            candidates = self._get_id32_candidates(id32_hint)
            if len(candidates) == 1:
                self._edit_resource(id32=candidates[0])
            elif len(candidates) == 0:
                print(f"No resources starting with `{id32_hint}` were found.")
            else:
                print(f"{len(candidates)} candidates were found.")
                for id32 in candidates:
                    self._info_resource(id32=id32)
        if (id32_hint := args.get("info_resource")) is not None:
            candidates = self._get_id32_candidates(id32_hint)
            for id32 in candidates:
                self._info_resource(id32=id32)
        return self.ret_val

    def _view_resource(self, id32: common.JId32) -> None:
        jres = self.resources.get(id32)
        assert jres is not None, f"Resource {id32} does not exist in the database."

        assert common.DIR_LOCAL_RESOURCES.is_dir(), \
            f"{common.DIR_LOCAL_RESOURCES} is not a directory"
        for res_fpath in common.DIR_LOCAL_RESOURCES.rglob("*"):
            if res_fpath.stem == id32:
                res_fpath = PosixPath(common.DIR_LOCAL_RESOURCES / res_fpath)
                os.system(f"xdg-open {res_fpath} &")
                break
        else:
            print(f"Could not find the file for {id32}")
            self.ret_val = -1

    def _edit_resource(self, id32: common.JId32) -> None:
        jres = self.resources.get(id32)
        assert jres is not None, f"Resource {id32} does not exist in the database."

        assert common.DIR_LOCAL_RESOURCES.is_dir(), \
            f"{common.DIR_LOCAL_RESOURCES} is not a directory"
        for res_fpath in common.DIR_LOCAL_RESOURCES.rglob("*"):
            if res_fpath.stem == id32:
                res_fpath = PosixPath(common.DIR_LOCAL_RESOURCES / res_fpath)
                if jres.mime in {"image/png", }:
                    os.system(f"pinta {res_fpath} &")
                elif jres.mime in {"application/pdf", }:
                    os.system(f"pdfarranger {res_fpath} &")
                else:
                    os.system(f"xdg-open {res_fpath} &")
                break
        else:
            print(f"Could not find the file for {id32}")
            self.ret_val = -1

    def _info_resource(self, id32: common.JId32) -> None:
        jres = self.resources.get(id32)
        if jres is not None:
            print(f"Resource {id32}:")
            print(f"\ttitle: {jres.title}")

            assert common.DIR_LOCAL_RESOURCES.is_dir(), \
                f"{common.DIR_LOCAL_RESOURCES} is not a directory"
            res_fpath = None
            for res_fpath in common.DIR_LOCAL_RESOURCES.rglob("*"):
                if res_fpath.stem == id32:
                    print(f"\tpath: {res_fpath}")
                    break
            else:
                RuntimeError("Resource file not found.")
            print(f"\tsize: {res_fpath.stat().st_size:,} bytes ({jres.size:,} bytes in database)")
            if jres.size != res_fpath.stat():
                print(f"\t\t{jres.size:,} bytes according to the database")

            stat = res_fpath.stat()
            atime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_atime))
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime))
            print(f"\tcreated {ctime}, modified {mtime}, accessed {atime}")

            print(f"\ttype: {jres.mime}")
            try:
                image = Image.open(res_fpath)
                print(f"\t\tsize: {image.size}")
                print(f"\t\tformat: {image.format}")
                print(f"\t\tmode: {image.mode}")
                print(f"\t\tpalette: {image.palette}")
            except UnidentifiedImageError:
                pass

            print("\tnotes:")
            for note in jres.notes:
                print(f"\t\t{note.title}")

        else:
            print("No such resource.")
            self.ret_val = -1

    def _get_id32_candidates(self, id32_hint: str) -> list[common.JId32]:
        return [k for k in self.resources if k.startswith(id32_hint)]
