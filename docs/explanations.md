# Explanations

## Sources of data

After dropping the support of Joplin databases, `dope` tracks only my Obsidian vaults.

Paths are set in `dope/paths.py`.

## GTD-inspired task tracker

Tasks lines have a tag the format `#<type-of-task>/<priority>/<date>[:]`.

`<type-of-task>` can be one of the following:
* `n`, or **now**, which is something that I am doing at the moment.
* `x`, or **next**, which is something that I should do later.
* `w`, or **waiting**, which is something that is waiting for some external event to happen.

`<priority>` can be one of the following:
* `p1` is for high-priority tasks.
* `p2` is for normal-priority tasks.
* `p3` is for low-priority tasks.

`<date>` is the date in format YYYY-MM-DD:
* today for `n` tasks,
* the deadline for `x` tasks
* the date by which the external event `w` is expected to happen.

Examples of task lines:
`* [ ] #x/p2/2024-09-10 Do the thing A.`
`* [ ] #w/p2/2024-09-10 Wait for B to happen.`.
`* [ ] #n/p2/2024-09-10: Do the thing C.`
