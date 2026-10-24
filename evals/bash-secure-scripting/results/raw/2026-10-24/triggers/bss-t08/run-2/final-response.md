# Job control in interactive bash

Job control lets one terminal run several pipelines at once. You can suspend them, resume them, and move them between the foreground and background. It relies on the kernel's process groups, sessions and controlling terminal, and bash manages these for you.

## The kernel pieces

- **Session:** the login shell and everything it starts. A session has one **controlling terminal**, such as a tty or pty.
- **Process group:** bash puts each pipeline (job) in its own process group. In `cat log | grep err | less`, all three processes share one process-group ID (PGID), so they can be signalled as a unit.
- **Foreground process group:** the terminal tracks exactly one foreground group at a time (`tcsetpgrp`). Only that group can read from the terminal. Keyboard-generated signals go to the whole foreground group:
  - `Ctrl-C` sends `SIGINT`
  - `Ctrl-\` sends `SIGQUIT`
  - `Ctrl-Z` sends `SIGTSTP`, which stops (suspends) the group

When you run a command in the foreground, bash makes that job's group the terminal's foreground group and waits for it. When the job exits or stops, bash takes the terminal back.

## Starting and managing jobs

| Action | Effect |
|---|---|
| `cmd &` | Runs in the background. Bash prints `[1] 12345` (job number, PID) and returns the prompt right away. |
| `Ctrl-Z` | Stops the foreground job. Bash reports `[1]+ Stopped cmd`. |
| `jobs` / `jobs -l` | Lists jobs with their state (Running, Stopped, Done) and, with `-l`, their PIDs. |
| `fg [%n]` | Gives job *n* the terminal, sends it `SIGCONT` if it's stopped, and waits for it. |
| `bg [%n]` | Sends `SIGCONT` to a stopped job so it keeps running in the background. |
| `kill %n` | Signals the job's whole process group. |
| `wait [%n]` | Blocks until a background job finishes. |
| `disown [%n]` | Removes a job from bash's job table, so bash won't send it `SIGHUP` on exit. |

### Ways to refer to a job

- `%1`: job number 1
- `%+` or `%%`: the current job, marked `+` in `jobs`. This is the default for `fg` and `bg`.
- `%-`: the previous job, marked `-`
- `%vim`: the job whose command starts with "vim"
- `%?log`: the job whose command contains "log"

A bare `%1` on its own is shorthand for `fg %1`, and `%1 &` is shorthand for `bg %1`.

## Background jobs and the terminal

- **Reading:** if a background job tries to read from the terminal, the kernel sends it `SIGTTIN`, which stops it. You'll see `Stopped (tty input)`. Bring it to the foreground with `fg` to give it input.
- **Writing:** background output normally appears on the terminal, mixed in with your prompt. If you run `stty tostop`, writes from background jobs trigger `SIGTTOU` and stop the job instead.
- **Ctrl-C** only reaches the foreground group, so it doesn't affect background jobs.

## Status notification

Bash gets job state changes through `SIGCHLD` and `waitpid`. By default it reports finished or stopped background jobs just before the next prompt, for example `[1]+ Done sleep 10`. With `set -b` (`set -o notify`), it reports them immediately.

## Exiting the shell

- If you try to exit while jobs are **stopped**, bash warns `There are stopped jobs.` A second `exit` in a row goes through anyway.
- With `shopt -s checkjobs`, bash also warns about **running** jobs.
- When an interactive login shell exits, or the terminal hangs up, bash sends `SIGHUP` to its jobs. Stopped jobs also get a `SIGCONT` so they can receive it. Ways to keep a job alive:
  - `disown` the job
  - Start it with `nohup cmd &`
  - Set `shopt -s huponexit`. This only changes the behaviour of login shells on a normal exit.
  - Use `setsid` or a multiplexer such as tmux or screen for a fully separate session.

## Scripts versus interactive shells

Job control (`set -m`, the `monitor` option) is on by default only in interactive shells. In a script:

- Background jobs share the script's process group instead of getting their own.
- `fg`, `bg` and `%n` references aren't available unless you enable `set -m` yourself.
- Background commands have `SIGINT` and `SIGQUIT` ignored, and their stdin is redirected from `/dev/null`.

Scripts normally manage children with `$!`, `wait` and `kill`, not with job specs.

## Example session

```text
$ sleep 100 &          # [1] 4242
$ vim notes.txt        # editing... press Ctrl-Z
[2]+  Stopped   vim notes.txt
$ jobs
[1]-  Running   sleep 100 &
[2]+  Stopped   vim notes.txt
$ bg %1                # already running; no-op message
$ kill %1              # SIGTERM to sleep's process group
$ fg                   # resumes vim (%+) in the foreground
```

In short, bash gives each pipeline its own process group and decides which group owns the terminal. `Ctrl-Z`, `fg` and `bg` switch that ownership and send `SIGTSTP` or `SIGCONT` signals.
