# Explanations

## Sources of data

After dropping the support of Joplin databases in 2024, `dope` tracks only my Obsidian vaults.

The list of active vaults is in `~/.config/dope/vaults.json`.
You can add a vault using command `--config-vault-add`, remove a vault with `--config-vault-drop`, and see the list with `--config-vault-list`.

## GTD-inspired task tracker

Tasks lines have a tag the format `#<date>/<type-of-task><priority>[:]`.

`<type-of-task>` can be one of the following:
* `n`, or **now**, which is something that I am doing at the moment.
* `x`, or **next**, which is something that I should do later.
* `w`, or **waiting**, which is something that is waiting for some external event to happen.

`<priority>` can be a digit from 1 to 3.
* `1` is for high-priority tasks.
* `2` is for normal-priority tasks.
* `3` is for low-priority tasks.

`<date>` is the date in format YYYY-MM-DD:
* today for `n` tasks,
* the deadline for `x` tasks
* the date by which the external event `w` is expected to happen.

Examples of task lines:
`* [ ] #2024-09-10/x2 Do the thing A.`
`* [ ] #2024-09-10/w2 Wait for B to happen.`.
`* [ ] #2024-09-10/n2: Do the thing C.`

***
## Lesson tracker

Lesson lines have a tag with the format `#edu/<course>/<action>`.

Action:
* `x` for lessons that can be learned,
* `n` for lessons that are being learned,
* `w` for lessons that can be learned after some other lesson,
* `big` for big lessons not yet split into digestible chunks.

Command `dope --edu` with optional course filter and vault filter will list lessons. 

***
## Check list

The **check-list** file is a spreadsheet that is opened when `dope -cl` command is received.

***
