# Job control in interactive bash

**What it is:** Job control lets you run multiple processes from one terminal, suspend them, and move them between foreground and background. It's enabled by default in interactive shells (`set -m` / `monitor` option) and off in scripts.

## Core concepts

- **Job**: a pipeline (or single command) the shell launched. Each job gets its own **process group**, and the shell assigns it a job number (`%1`, `%2`, …).
- **Foreground job**: the one process group that owns the terminal. It receives keyboard input and terminal-generated signals.
- **Background job**: runs without terminal input. If it tries to read from the tty, it gets `SIGTTIN` and stops. With `stty tostop` set, writing to it stops it too (`SIGTTOU`).
- **Controlling terminal**: the kernel tracks which process group is foreground (`tcsetpgrp`). Bash hands the terminal to a job when you run it in the foreground and takes it back when the job stops or exits.

## Keyboard signals

| Key | Signal | Effect |
|---|---|---|
| `Ctrl-C` | `SIGINT` | Interrupts the foreground job |
| `Ctrl-Z` | `SIGTSTP` | Suspends the foreground job (it becomes "Stopped") |
| `Ctrl-\` | `SIGQUIT` | Quits, usually with a core dump |

The terminal driver sends these to the whole foreground process group, so every process in a pipeline receives them.

## Commands

- `cmd &`: start in the background. Bash prints `[1] 12345` (job number and PID). `$!` holds the last background PID.
- `jobs` (`-l` adds PIDs, `-p` PIDs only, `-r` running, `-s` stopped): list jobs. `+` marks the current job, `-` the previous one.
- `fg [%n]`: bring a job to the foreground, resuming it if stopped.
- `bg [%n]`: resume a stopped job in the background (sends `SIGCONT`).
- `kill %n` / `kill -STOP %n` / `kill -CONT %n`: signal a job by job spec.
- `wait [%n|pid]`: block until a job finishes and return its exit status.
- `disown [-h] [%n]`: remove the job from the shell's table so it won't get `SIGHUP` on exit. `-h` keeps it in the table but suppresses the HUP. `-a` and `-r` affect all or only running jobs.
- `suspend`: suspend the shell itself (not allowed in a login shell without `-f`).

## Job specs

`%n` is job number n. `%%` or `%+` is the current job. `%-` is the previous one. `%str` is a job whose command starts with `str`. `%?str` is a job whose command contains `str`. A bare `%1` runs as `fg %1`, and `%1 &` runs as `bg %1`.

## Typical workflow

1. Run `vim notes.txt`, then press `Ctrl-Z`. You see `[1]+  Stopped  vim notes.txt`.
2. Run `make -j8 &` to start a build in the background.
3. `jobs` lists both.
4. `fg %1` goes back to vim.

## Status notifications

Bash checks job status before printing a prompt, so it reports state changes like `Done` or `Stopped` then. `set -b` (`notify`) makes it report immediately instead.

## Exit and hangup behavior

- Closing the terminal sends `SIGHUP` to the shell. With `shopt -s huponexit`, an interactive login shell also sends it to jobs on exit. Otherwise bash typically passes the HUP on to its jobs when it receives one itself.
- If you exit with stopped jobs, bash warns once (`There are stopped jobs.`). Run `exit` again to leave anyway, which kills them.
- To keep a process alive after logout, use `nohup cmd &`, `disown`, or a multiplexer such as `tmux` or `screen`.

## Subtleties

- **Pipelines**: all stages share one process group, so they're one job. `$?` reflects the last stage unless `pipefail` is set. `PIPESTATUS` holds all of them.
- **Subshells and `$()`**: these don't do job control. Background jobs started inside them aren't in the parent's job table.
- **Scripts**: job control is off by default, so `&` jobs stay in the script's process group and `fg`/`bg` don't work. `wait` still works.
- **`SIGCHLD`**: bash uses it to learn when children change state, then reaps them with `waitpid`.
- **Background output**: a background job still writes to your terminal, so its output can interleave with your prompt. Redirect it if that's a problem.
