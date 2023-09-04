""" The module tests local and remote resource files. """

# Standard library imports
import logging
import pathlib
# Third party imports
# Local application/library imports
import common


def test_resources_local(logger: logging.Logger):
    """
    Check that all resources referenced in notes exist in the local directory and vice-versa.
    There shouldn't be any extra files in the local directory.
    """
    res_dict: dict[common.JId32, common.JResource] = common.get_db_local_used_resources()
    res_paths: list[pathlib.PosixPath] = sorted(common.DIR_LOCAL_RESOURCES.glob("*"))

    res_ids_loc = [path.stem for path in res_paths]
    res_ids_db = list(res_dict.keys())
    num_res_loc = len(res_ids_loc)
    num_res_db = len(res_ids_db)
    assert num_res_loc == num_res_db, \
        f"Database knows about {num_res_db} resources. Directory contains {num_res_loc} resources."
    assert set(res_ids_loc) == set(res_ids_db), "Resource IDs are inconsistent."

    size_total_db = sum(res.size for res in res_dict.values())
    logger.info(f"Total resources size according to the database: "
                f"{round(size_total_db / 2**20)} MBytes ({size_total_db:,} Bytes)")
    size_total_loc = sum(path.stat().st_size for path in res_paths)
    logger.info(f"Total resources size in the local directory: "
                f"{round(size_total_loc / 2**20)} MBytes ({size_total_loc:,} Bytes)")
    if size_total_loc != size_total_db:
        for res in res_dict.values():
            try:
                path = next(common.DIR_LOCAL_RESOURCES.glob(res.id32 + ".*"))
                size_loc = path.stat().st_size
                size_db = res.size
                if size_loc != size_db:
                    logging.debug("`%s` (%s) has database size %d and the real file size is %d.",
                                  res.id32, res.title, size_db, size_loc)
            except StopIteration:
                logging.warning("Resource `%s` is problematic.", res.id32)
                raise
