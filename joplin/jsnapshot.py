#!/usr/bin/python3
"""
A script for generating human-readable snapshots of Joplin data.
"""

import enum
import os
from pathlib import Path
import time

from joplin.common import (JId32, JNotebook, JNote, JItem, JTag,
                           get_db_local_notebooks, get_db_local_notes, get_db_local_tags)


class TreeNode:
    """ A container that stores a notebook or a note
    as long as all notebook's child notebooks and notes.

    The root node is a special case and it's a non-existent notebook.
    """
    def __init__(self, jitem: JItem):
        self.jitem = jitem
        self.children = []

    def add_node(self, node: "TreeNode",
                 notebooks: dict[JId32, JNotebook], notes: dict[JId32, JNote]):
        """ Add a node to the tree. """
        self.children.append(node)
        for notebook in notebooks.values():
            if notebook.id32_parent == node.jitem.id32:
                self.children[-1].add_node(TreeNode(notebook), notebooks, notes)
        for note in notes.values():
            if note.id32_parent == node.jitem.id32:
                self.children[-1].add_node(TreeNode(note), notebooks, notes)


class JSnapshot:
    """ Class that does all the work. """

    class Source(enum.Enum):
        """ Possible sources of data for generaing snapshots. """
        LOCAL_DB = enum.auto()
        REMOTE_DIR = enum.auto()
        LOCAL_DOPE = enum.auto()

    def __init__(self, source: "Source"):
        self.cwd = os.getcwd()
        match source:
            case self.Source.LOCAL_DB:
                self._process_local_db()
            case _:
                raise NotImplementedError

    def _make_notebook_dir(self, node: TreeNode, path: Path):
        path = Path(path, node.jitem.title)
        os.makedirs(name=path, exist_ok=True)
        for child in node.children:
            if isinstance(child.jitem, JNotebook):
                assert "/" not in child.jitem.title, f"Slash in notebook title: {child.jitem.title}"
                self._make_notebook_dir(child, path)
            elif isinstance(child.jitem, JNote):
                assert "/" not in child.jitem.title, f"Slash in note title: {child.jitem.title}"
                note_path = os.path.join(path, child.jitem.title)
                # print(f"not a dir: {note_path}")
                with open(note_path, "w", encoding="utf-8") as file:
                    file.write(child.jitem.body)
            else:
                raise TypeError

    def _process_local_db(self):

        dir_name = Path(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time())))  # str
        self.root_dir = Path(self.cwd, "snapshots", dir_name)
        os.makedirs(name=self.root_dir, exist_ok=True)

        # Notebooks

        notebooks: dict[JId32, JNotebook] = get_db_local_notebooks()
        notes: dict[JId32, JNote] = get_db_local_notes()

        root = TreeNode(JNotebook(id32=None, title="notebooks", id32_parent=None))
        for notebook in notebooks.values():
            if notebook.id32_parent is None:
                root.add_node(TreeNode(notebook), notebooks, notes)

        os.chdir(self.root_dir)
        self._make_notebook_dir(root, self.root_dir)

        # Tags

        os.chdir(self.root_dir)
        root_tags = os.path.join(self.root_dir, "tags")
        os.makedirs(name=root_tags, exist_ok=True)
        os.chdir(root_tags)

        tags: list[JTag] = get_db_local_tags().values()
        for tag in tags:
            tag_dir = os.path.join(root_tags, tag.title)
            os.makedirs(name=tag_dir, exist_ok=True)
            os.chdir(tag_dir)
            for note in tag.notes:
                assert note.id32 in notes
                note_path = os.path.join(self.root_dir, "notebooks",
                                         notebooks[note.id32_parent]
                                         .get_path(note.title, notebooks))
                assert os.path.exists(note_path) and os.path.isfile(note_path)
                os.symlink(src=note_path, dst=note.title)  # TODO: src should be relative


if __name__ == "__main__":

    JSnapshot(source=JSnapshot.Source.LOCAL_DB)
