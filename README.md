# dope

`dope` is a collection of tests and a CLI tool for my Joplin database and Obsidian vaults.
`dope` is also my task tracker.

# Sources of data

`dope` tracks several sources of data:
* the local copy of my Joplin database,
* the external synchronization target for my Joplin database,
* my Obsidian vaults.

# Building instructions (for the maintainer)

Run this command in the directory where `pyproject.toml` is located.
```
python3 -m build
```
Two files will be created in the `dist` directory:
```
dist/
├── dope-0.0.1-py3-none-any.whl
└── dope-0.0.1.tar.gz
```
