""" The module tests local and remote resource files. """

import logging
import os
import pathlib
import sqlite3
import pytest

from joplin.common import (DIR_LOCAL_EDITED_RESOURCES, DIR_LOCAL_RESOURCES, DIR_REMOTE_RESOURCES,
                           JId32, JResource, get_db_local_used_resources)


def test_resources_local(logger: logging.Logger) -> None:
    """
    Check that all resources referenced in notes exist in the local directory and vice-versa.
    There shouldn't be any extra files in the local directory.
    """
    res_dict: dict[JId32, JResource] = get_db_local_used_resources()
    res_paths: list[pathlib.PosixPath] = sorted(DIR_LOCAL_RESOURCES.glob("*"))

    res_ids_loc = [path.stem for path in res_paths]
    res_ids_db = list(res_dict.keys())
    num_res_loc = len(res_ids_loc)
    num_res_db = len(res_ids_db)
    assert num_res_loc == num_res_db, \
        f"Database knows about {num_res_db} resources. Local directory contains {num_res_loc} resources."
    assert set(res_ids_loc) == set(res_ids_db), "Resource IDs are inconsistent."
    logger.info(f"Total {num_res_loc} resources.")

    size_total_db = sum(res.size for res in res_dict.values())
    logger.info(f"Total resources size according to the database: "
                f"{round(size_total_db / 2**20)} MBytes ({size_total_db:,} Bytes)")
    size_total_loc = sum(path.stat().st_size for path in res_paths)
    logger.info(f"Total resources size in the local directory: "
                f"{round(size_total_loc / 2**20)} MBytes ({size_total_loc:,} Bytes)")
    if size_total_loc != size_total_db:
        for res in res_dict.values():
            try:
                path = next(DIR_LOCAL_RESOURCES.glob(res.id32 + ".*"))
                size_loc = path.stat().st_size
                size_db = res.size
                if size_loc != size_db:
                    logging.debug("`%s` (%s) has database size %d and the real file size is %d.",
                                  res.id32, res.title, size_db, size_loc)
            except StopIteration:
                logging.warning("Resource `%s` is problematic.", res.id32)
                raise


def test_resources_remote(db_local_conn: sqlite3.Connection, logger: logging.Logger):
    """
    Check that all database resources are in the remote folder and vice-versa.
    There should not be any extra files in the remote folder.
    """
    res_dict: dict[JId32, JResource] = get_db_local_used_resources()
    res_paths_rem: list[pathlib.PosixPath] = sorted(DIR_REMOTE_RESOURCES.glob("*"))

    res_ids_rem = [path.stem for path in res_paths_rem]
    res_ids_db = list(res_dict.keys())

    num_res_rem = len(res_ids_rem)
    num_res_db = len(res_ids_db)
    assert num_res_rem == num_res_db, \
        f"Database knows about {num_res_db} resources. Remote directory contains {num_res_rem} resources."
    assert set(res_ids_rem) == set(res_ids_db), "Resource IDs are inconsistent."

    size_total_db = sum(res.size for res in res_dict.values())
    logger.info(f"Total resources size according to the database: "
                f"{round(size_total_db / 2**20)} MBytes ({size_total_db:,} Bytes)")
    size_total_rem = sum(path.stat().st_size for path in res_paths_rem)
    logger.info(f"Total resources size in the local directory: "
                f"{round(size_total_rem / 2**20)} MBytes ({size_total_rem:,} Bytes)")

    # set_res_ids_rem = set(res_ids_rem)
    # set_res_ids_db = set(res_ids_db)
    # if set_res_ids_rem != set_res_ids_db:
    #     set_diff_db = set_res_ids_db - set_res_ids_rem
    #     if set_diff_db:
    #         logger.warning("Database resources that are not in the remote directory:")
    #         cur = db_local_conn.cursor()
    #         set_diff_db_str = ",".join([("\"" + x + "\"") for x in set_diff_db])
    #         sql = f"SELECT id, title, mime, size FROM resources WHERE id in ({set_diff_db_str})"
    #         cur.execute(sql)
    #         for res in cur.fetchall():
    #             res_id, title, mime, size = res
    #             logger.warning(f"  id={res_id}, {title=}, {mime=}, {size=} Bytes,")

    #     set_diff_rem = set_res_ids_rem - set_res_ids_db
    #     if set_diff_rem:
    #         logger.warning("Remote resources that are not in the database:")
    #         for res_id in set_diff_rem:
    #             path = os.path.join(common.DIR_REMOTE_RESOURCES, res_id)
    #             size = os.path.getsize(path)
    #             logger.warning(f"  id={res_id}, {size=} Bytes")

    assert set(res_ids_rem) == set(res_ids_db)


def test_resources_being_edited(db_local_used_resources: dict[JId32, JResource],
                                logger: logging.Logger) -> None:
    """
    Check that there are no resource files that were being edited and not closed afterwards.
    """
    if not DIR_LOCAL_EDITED_RESOURCES.exists():
        return
    edited_resources = []
    for path in DIR_LOCAL_EDITED_RESOURCES.glob("*"):
        for jres in db_local_used_resources.values():
            if jres.title == path.name:
                edited_resources.append(jres)
                break
    for resource in edited_resources:
        logger.error(f"Resource is not closed: {resource}.")
    assert len(edited_resources) == 0, \
        "There are resources that were not closed after being edited."


@pytest.mark.skip
def test_resources_not_in_notes(db_local_used_resources: dict[JId32, JResource],
                                logger: logging.Logger):
    """
    Check that there are no resources not mentioned in notes.
    """
    orphans = [jres for jres in db_local_used_resources.values() if not jres.notes]
    for orphan in orphans:
        logger.warning(f"Resource not referenced: {orphan}")
    assert not orphans, f"{len(orphans)} resources are not referenced in notes."
