"""
When exporting notes to markdown, Joplin truncates file names and replaces some symbols.
This one-off script attempts to fix those file names.

Created 2023-12-26.
"""

import sqlite3

from dope.paths import J_PATH_LOCAL_DB, V_DIRS


def get_j_titles() -> list[str]:
    """
    Parses the local database and returns a dictionary
    with notes' IDs as keys and JNote objects as values.
    """
    titles: list[str] = []
    with sqlite3.connect(database=f"file:{J_PATH_LOCAL_DB}?mode=ro", uri=True) as db_conn:
        cur = db_conn.cursor()
        cur.execute("SELECT title FROM notes")
        for title in cur.fetchall():
            title = title[0].replace(":", "_").replace(">", "_")
            titles.append(title)
    return titles


if __name__ == "__main__":

    j_titles = get_j_titles()

    v_note_paths = []
    v_dir = V_DIRS[0]
    for v_note_path in v_dir.rglob("*.md"):
        assert v_note_path.is_file()
        assert v_note_path.name == v_note_path.stem + ".md"
        v_note_paths.append(v_note_path)

    MAX_BATCH_SIZE = 10
    BATCH_SIZE = 0

    for v_note_path in v_note_paths:

        NUM_SUGGESTIONS_THIS = 0

        for j_title in j_titles:
            if j_title == v_note_path.stem:
                NUM_SUGGESTIONS_THIS = 0
                break
            if j_title.startswith(v_note_path.stem) and j_title != v_note_path.stem:
                new_v_note_path = v_note_path.with_stem(j_title)
                NUM_SUGGESTIONS_THIS += 1

        if NUM_SUGGESTIONS_THIS == 1:

            print(f"Suggesting renaming\n\t{v_note_path.name}\n\t{new_v_note_path.name}.")
            BATCH_SIZE += 1

            # v_note_path.rename(new_v_note_path)
            # print("\t\tRenamed.")

        if NUM_SUGGESTIONS_THIS >= 1:
            print(f"Consider renaming\n\t{v_note_path.name}\n\t{new_v_note_path.name}.")

        if BATCH_SIZE == MAX_BATCH_SIZE:
            break

    print(f"{MAX_BATCH_SIZE} suggestions.")
