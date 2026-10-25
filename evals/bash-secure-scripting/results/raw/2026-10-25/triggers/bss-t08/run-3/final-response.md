Job control lets one interactive shell run several pipelines at once, stop and resume them, and choose which one gets the terminal. It's built on process groups, sessions, and terminal signals.

## The pieces underneath

- **Session and controlling terminal.** When you log in or open a terminal, bash leads a *session* tied to that terminal (TTY/PTY).
- **Process groups.** Each pipeline you run is a *job*. Bash puts it in its own process group, so `cat file | grep x | sort` is one job with three processes and one group ID.
- **Foreground process group.** The terminal tracks exactly one foreground process group (bash sets it with `tcsetpgrp`). Only that group can read from the terminal. Keyboard signals go to the whole foreground group:
  - `Ctrl-C` sends `SIGINT`
  - `Ctrl-\` sends `SIGQUIT`
  - `Ctrl-Z` sends `SIGTSTP` (suspend)
- **Background groups.** If a background job tries to read from the terminal, it gets `SIGTTIN` and stops. If it writes while `stty tostop` is set, it gets `SIGTTOU`.

When a foreground job finishes or stops, bash takes the terminal back and shows the prompt again.

## Starting jobs

```bash
long_command          # foreground: bash waits for it
long_command &        # background: bash prints [1] 12345 and returns the prompt
```

`[1]` is the job number and `12345` is the PID of the last process in the pipeline. `$!` holds that PID too.

## Commands for managing jobs

| Command | Effect |
|---|---|
| `jobs` / `jobs -l` | List jobs with their state (Running, Stopped, Done). `-l` adds PIDs. |
| `Ctrl-Z` | Stop the foreground job. |
| `fg [%job]` | Move a job to the foreground (sending `SIGCONT` if it was stopped). |
| `bg [%job]` | Resume a stopped job in the background. |
| `kill %job` | Signal every process in the job's group. |
| `wait [%job]` | Block until the job finishes and return its exit status. |
| `disown [%job]` | Drop the job from bash's table so it won't get `SIGHUP` when bash exits. `-h` keeps it in the table but still skips the `SIGHUP`. |
| `suspend` | Stop the shell itself (useful in a subshell or after `su`). |

## Job specifiers

- `%1`: job number 1
- `%%` or `%+`: the current job (most recently stopped or backgrounded)
- `%-`: the previous job
- `%vim`: the job whose command starts with `vim`
- `%?log`: the job whose command contains `log`

`%1` on its own works like `fg %1`, and `%1 &` works like `bg %1`.

## A typical session

```text
$ vim notes.txt
^Z
[1]+  Stopped                 vim notes.txt
$ make > build.log 2>&1 &
[2] 40211
$ jobs
[1]+  Stopped                 make ...    # (illustrative)
[2]-  Running                 make > build.log 2>&1 &
$ fg %1          # back into vim
```

## Status notification

Bash finds out about child state changes through `SIGCHLD` and `waitpid`. By default it reports finished background jobs just before the next prompt. With `set -b` (`notify`) it reports them right away.

## Hangups and exiting

- When the terminal closes, bash gets `SIGHUP` and passes it on to all its jobs, which usually kills them. To keep a job alive, use `disown`, `nohup`, `setsid`, or a multiplexer like tmux or screen.
- If bash exits normally, it only sends `SIGHUP` to jobs when `shopt -s huponexit` is set.
- If you try to exit while jobs are stopped, bash warns "There are stopped jobs." A second `exit` goes ahead anyway.

## Interactive versus scripts

The `monitor` option (`set -m`) controls job control. It's on by default in interactive shells and off in scripts. In a script:
- `&` and `wait` still work.
- Background jobs share the script's process group instead of getting their own.
- `fg`, `bg`, and `Ctrl-Z` behave as you'd expect only if you turn on `set -m`.
- Background commands have `SIGINT` and `SIGQUIT` ignored.

## Interactive gotchas

- **Background jobs that read stdin stop.** A job like `ssh host cmd &` will stop when it reads the terminal. Redirect its input (`< /dev/null`) or use `ssh -n`.
- **Background output mixes with your prompt** unless you redirect it.
- **Each pipeline is one job.** `Ctrl-Z` stops every process in it together.
- **A bare `wait` waits for every background job.** `wait -n` returns as soon as any single job finishes.
