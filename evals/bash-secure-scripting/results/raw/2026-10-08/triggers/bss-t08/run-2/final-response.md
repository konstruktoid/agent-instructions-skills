# Job control in an interactive Bash session

Job control lets one terminal run several pipelines. You can suspend them, resume them, and move them between the foreground and background. The terminal driver (the TTY layer) and the shell do this work together.

## Core concepts

**Jobs and process groups.** Each pipeline you type becomes one *job*. Bash puts every process in that pipeline into the same **process group**, and the group's ID (PGID) is usually the PID of the first process. In `grep foo log | sort | less`, all three processes share one PGID, so the shell can signal them as a unit.

**Sessions and the controlling terminal.** Your login shell leads a **session**, and that session has a **controlling terminal** (`/dev/pts/N`). Every job you start belongs to this session.

**Foreground process group.** Exactly one process group per terminal is in the foreground. The kernel records which one, and Bash changes it with `tcsetpgrp()`. This matters in two ways:
- Keyboard-generated signals go to every process in the **foreground** group only.
- Only the foreground group may read from the terminal freely.

## Keyboard signals

The terminal driver turns special keys into signals, which `stty -a` lists:

| Key | Signal | Default effect |
|---|---|---|
| `Ctrl-C` | `SIGINT` | terminate |
| `Ctrl-\` | `SIGQUIT` | terminate and dump core |
| `Ctrl-Z` | `SIGTSTP` | stop (suspend) |

Bash doesn't send these signals. The kernel's TTY layer sends them to the foreground group. While a job is in the foreground, the interactive shell is not in that group, so it doesn't receive them.

## Background jobs and terminal access

- **Reading:** if a background job tries to read from the terminal, the kernel sends its group `SIGTTIN`, which stops it. Bring it to the foreground to give it input.
- **Writing:** by default a background job can write to the terminal, which is why output gets mixed together. If you run `stty tostop`, writes trigger `SIGTTOU` and the job stops instead.

## How Bash tracks state

Bash calls `waitpid()` with `WUNTRACED`/`WCONTINUED` to learn when children stop, continue, or exit. It updates its job table and reports changes before the next prompt, or right away if `set -b` (notify) is on. This is where messages like `[1]+  Stopped  vim` and `[2]-  Done  make` come from.

## Commands

| Command | What it does |
|---|---|
| `cmd &` | Start the job in the background. Bash prints `[jobnum] PID`. |
| `Ctrl-Z` | Stop the foreground job. Bash takes the terminal back. |
| `jobs` / `jobs -l` | List jobs (`-l` adds PIDs). `+` marks the current job and `-` the previous one. |
| `fg [%job]` | Give the terminal to the job's group and send `SIGCONT`. |
| `bg [%job]` | Send `SIGCONT` to a stopped job but leave it in the background. |
| `kill %job` | Signal the whole process group of that job. |
| `wait [%job]` | Block until the job finishes. |
| `disown [%job]` | Remove the job from Bash's table so it won't get `SIGHUP` when the shell exits. |
| `suspend` | Stop the shell itself, for example a subshell or `su` session. |

### Job specs

| Spec | Refers to |
|---|---|
| `%1` | job number 1 |
| `%%` or `%+` | the current job |
| `%-` | the previous job |
| `%vim` | the job whose command starts with `vim` |
| `%?log` | the job whose command contains `log` |

A bare `%1` is shorthand for `fg %1`, and `%1 &` is shorthand for `bg %1`.

## A typical sequence

```
$ vim notes.txt          # foreground; the terminal belongs to vim's group
^Z                       # TTY sends SIGTSTP; vim stops
[1]+  Stopped   vim notes.txt
$ make > build.log 2>&1 &
[2] 41237
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make > build.log 2>&1 &
$ fg %1                  # tcsetpgrp(vim's PGID), then SIGCONT
```

## Shell exit and SIGHUP

- When an interactive login shell exits, or the terminal hangs up, Bash sends `SIGHUP` to its jobs. It sends `SIGCONT` to stopped jobs first so they can handle the hangup. The kernel also sends `SIGHUP` to the foreground group when the terminal closes.
- If `shopt -s huponexit` is set, a login shell also sends `SIGHUP` to its jobs on a normal `exit`.
- If any jobs are **stopped**, Bash warns "There are stopped jobs" the first time you try to exit. A second `exit` exits anyway.
- To keep a job running after you log out:
  - `disown` removes it from Bash's job table.
  - `nohup cmd &` ignores `SIGHUP` and sends output to `nohup.out`.
  - `setsid cmd` starts it in a new session with no controlling terminal.
  - `tmux` or `screen` keep the whole terminal alive.

## Interactive vs. non-interactive

Job control is enabled with `set -m` (monitor mode), which is on by default only in interactive shells. Scripts run with it off. In a script, background jobs stay in the script's process group, `fg` and `bg` aren't useful, and a background command started with `&` has its stdin redirected from `/dev/null` and ignores `SIGINT`/`SIGQUIT`. You can turn it on with `set -m` in a script, but that's rarely the right choice. Plain `&` plus `wait` is the usual pattern there.
