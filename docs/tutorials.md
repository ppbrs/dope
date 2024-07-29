# Tutorials

## Using the task tracker

1. Open a note and add a line containing a short description of the task.
```
Buy some rinse aid for my dishwasher.
```
2. Add a task tag on that line.
```
#nxt/p3/20240105 Buy some rinse aid for my dishwasher.
```
3. Use the command-line tool to browse tasks.
```
$ d --nxt
#NXT-P3 [in 3 days] Buy some rinse aid for my dishwasher.
```

***
## Using pomodoro timers

## Starting timers
Starting a 45-minute timer named `MR review`:
```
$ d -ps 45 MR review
Started a 45-minute pomodoro timer `MR review` (pid=262133).
```

Starting a default timer:
```
$ d -ps
Started a 30-minute pomodoro timer `default` (pid=262150).
```

## Listing active timers
```
$ d -pl
2 active pomodoro timers found:
        1: MR review (pid=262133), 45 min, 08:26:56 -> 09:11:56, expires in 00:44:03.
        2: default (pid=262150), 30 min, 08:27:15 -> 08:57:15, expires in 00:29:21.
```

## Deleting running timers
Use the full process ID or a part of it:
```
$ d -pk 133
Killing the timer MR review (pid=262133), which would have expired in 00:42:13.
```
***
