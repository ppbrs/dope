# Next features:

## Search tasks by keywords

`$ jcli -s zaber vega`
All keywords are or-ed.
Keywords are searched in both note titles and task lines.

# Usage:

This will list all Q1 tasks:
`$ jcli --nxt 1`
`$ jcli --nxt q1`  # is equivalent to the above.

This will list all Q1 and Q4 tasks:
`$ jcli --nxt 1 4`
Q1 and Q4 will be listed separately.

This will list all tasks sorted by deadline:
`$ jcli --nxt`
