# Job control in interactive bash

Job control lets you run several pipelines from one terminal, pause them, and move them between the foreground and the background. Bash enables it by default in interactive shells (`set -m`). Non-interactive scripts have it off.

## The underlying model

- **Jobs are process groups.** Each pipeline you start, such as `grep foo file | sort`, becomes one *job*. Bash puts every process in that pipeline into a new process group, so the whole pipeline can be signalled as a unit.
- **The terminal has one foreground process group.** The kernel's TTY driver tracks which process group is in the foreground (`tcsetpgrp`). Only that group can read from the terminal. It's also the group that receives keyboard-generated signals:
  - `Ctrl-C` sends `SIGINT`
  - `Ctrl-\` sends `SIGQUIT`
  - `Ctrl-Z` sends `SIGTSTP` (stop/suspend)
- **Background jobs** are process groups that aren't in the foreground. If one tries to read from the terminal, the kernel sends it `SIGTTIN` and it stops. If it writes while `stty tostop` is set, it gets `SIGTTOU`. Otherwise its output goes to the terminal mixed in with whatever else is printing.
- **Bash itself** ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU`, so it never stops itself. It takes the terminal back whenever a foreground job finishes or stops. It learns about state changes through `SIGCHLD` and `waitpid()` with `WUNTRACED`/`WCONTINUED`.

## Starting and moving jobs

| Action | Effect |
|---|---|
| `cmd &` | Starts the job in the background. Bash prints `[1] 12345` (job number, PID of the last process in the pipeline). |
| `Ctrl-Z` | Stops the foreground job and gives you the prompt back. |
| `bg [%job]` | Resumes a stopped job in the background by sending it `SIGCONT`. |
| `fg [%job]` | Gives the job the terminal and sends it `SIGCONT` if it's stopped, then waits for it. |
| `jobs` / `jobs -l` | Lists jobs with their state (Running, Stopped, Done). `-l` adds PIDs. |
| `kill %job` | Signals the job's whole process group. |
| `wait [%job]` | Blocks until the job finishes. |
| `disown [%job]` | Removes the job from bash's table so the shell won't send it `SIGHUP` on exit. `disown -h` keeps it in the table but still skips the `SIGHUP`. |
| `suspend` | Stops the shell itself, e.g. a subshell started with `su`. |

## Job specifications

- `%n`: job number *n*
- `%%` or `%+`: the current job (the most recently stopped or backgrounded one)
- `%-`: the previous job
- `%str`: the job whose command starts with *str*
- `%?str`: the job whose command contains *str*
- Typing just `%1` is shorthand for `fg %1`, and `%1 &` is shorthand for `bg %1`.

## Notifications and status

- By default bash reports job state changes (e.g. `[1]+ Done ...`) just before it prints the next prompt. `set -b` (`notify`) reports them immediately instead.
- `$!` holds the PID of the most recent background job.
- If you try to exit while jobs are stopped, bash warns "There are stopped jobs." A second `exit` goes ahead anyway. `shopt -s checkjobs` adds the same warning for running jobs.

## Hangups and exiting

When an interactive login shell gets `SIGHUP`, for example because the terminal closed, it forwards `SIGHUP` to all its jobs and sends `SIGCONT` to stopped ones so they can handle it. `shopt -s huponexit` makes a normal `exit` from a login shell do the same. To keep a job running after you leave, use `disown`, `nohup`, `setsid`, or a multiplexer like tmux or screen.

## A typical session

```text
$ vim notes.txt        # editing...
^Z                     # SIGTSTP → vim stops
[1]+  Stopped   vim notes.txt
$ make -j8 > build.log 2>&1 &
[2] 40211
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make -j8 > build.log 2>&1 &
$ fg %1                # back into vim; make keeps building
```

## Caveats

- In scripts, job control is off unless you run `set -m`. Background jobs there share the script's process group, and `fg`/`bg` aren't useful.
- Commands in a pipeline run in subshells, but job control acts on the pipeline as a whole.
- Programs that change terminal modes, like editors and pagers, catch `SIGTSTP`/`SIGCONT` so they can restore the terminal before stopping and redraw after resuming.
