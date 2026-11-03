Job control lets one interactive shell run several pipelines at once, switch which one owns the terminal, and pause or resume them. It depends on three things working together: process groups, the terminal's foreground process group, and signals.

## The core pieces

**1. Jobs are process groups.**
Each pipeline you type becomes a *job*. Bash puts all of its processes into a new **process group** (via `setpgid`), and the group ID is the PID of the first process. So `grep foo log | sort | less` is one job made of three processes in one group. Signals are sent to the whole group, which is why Ctrl‑C stops every stage of a pipeline.

**2. The terminal has one foreground process group.**
The tty driver tracks which process group is in the foreground (`tcsetpgrp`). Only that group can:
- read from the terminal, and
- receive keyboard-generated signals:
  - Ctrl‑C → `SIGINT`
  - Ctrl‑\ → `SIGQUIT`
  - Ctrl‑Z → `SIGTSTP`

Bash hands the terminal to a job when it runs in the foreground and takes it back when the job stops or exits. Bash itself ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU`, so Ctrl‑Z doesn't suspend the shell.

**3. Background jobs that touch the terminal get stopped.**
- If a background job tries to read from the tty, the kernel sends it `SIGTTIN` and it stops.
- If it tries to write while `stty tostop` is set, it gets `SIGTTOU` (writing is allowed by default).

That's why a background `vim &` shows up straight away as "Stopped".

## How it looks day to day

| Action | What happens |
|---|---|
| `cmd &` | Starts the job in the background. Bash prints `[1] 12345` (job number and PID) and gives you the prompt back. |
| Ctrl‑Z | The tty sends `SIGTSTP` to the foreground group. The job stops and bash takes the terminal back: `[1]+ Stopped`. |
| `jobs` / `jobs -l` | Lists jobs with their state (Running, Stopped, Done). `-l` adds PIDs. |
| `fg %n` | Gives the terminal to job *n*, sends `SIGCONT` if it was stopped, and waits for it. |
| `bg %n` | Sends `SIGCONT` to a stopped job so it keeps running in the background. |
| `kill %n` | Sends a signal (default `SIGTERM`) to the job's process group. |
| `wait %n` | Waits until the job finishes and returns its exit status. |
| `disown %n` | Removes the job from bash's table so bash won't send it `SIGHUP` on exit. `disown -h` keeps it in the table but still skips the `SIGHUP`. |

**Ways to refer to a job:** `%1` (by number), `%%` or `%+` (the current job, marked `+`), `%-` (the previous job), `%vim` (command starts with "vim"), `%?log` (command contains "log").

## Bookkeeping and notification

- Bash gets `SIGCHLD` when a child changes state, and calls `waitpid(..., WUNTRACED|WCONTINUED)` to find out what happened.
- By default it reports finished background jobs just before the next prompt (`[1]+ Done ...`). With `set -b` (`notify`) it reports them immediately.
- `$!` holds the PID of the most recent background job. Note that it's the last process in the pipeline, not the group ID.

## Hangups and exiting

- When the terminal closes, bash gets `SIGHUP` and forwards it to all of its jobs, sending `SIGCONT` first to any stopped ones so they can handle it.
- With `shopt -s huponexit`, a login shell also sends `SIGHUP` to its jobs on a normal `exit`.
- If you try to exit while jobs are stopped, bash warns "There are stopped jobs." Exiting a second time goes ahead anyway. With `shopt -s checkjobs` it also warns about running jobs.
- To keep a job alive after logout, use `nohup`, `disown`, or `setsid`, or run it inside tmux or screen.

## Interactive only

Job control is controlled by `set -m` (`monitor`). It's on by default in interactive shells and off in scripts. In a script:
- background jobs stay in the shell's own process group,
- `fg`, `bg` and Ctrl‑Z don't behave as above, and
- background commands start with `SIGINT` and `SIGQUIT` ignored.

You can turn it on in a script with `set -m`, but it's rarely a good idea. Use `wait` and `$!` to manage background work instead.
