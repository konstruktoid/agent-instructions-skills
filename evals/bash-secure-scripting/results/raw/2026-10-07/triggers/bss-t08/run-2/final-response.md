# Job control in interactive bash

Job control lets you suspend, resume, and move processes between foreground and background in one terminal. It is on by default in interactive shells (`set -m` / `monitor` option) and off in scripts.

## Core concepts

- **Job**: a pipeline (or a single command) that the shell started. Bash tracks each one in a job table with a number, such as `[1]`.
- **Process group**: each job runs in its own process group, and the shell is the group leader of its own. This lets the shell and terminal signal a whole pipeline at once.
- **Controlling terminal and foreground process group**: a terminal has exactly one foreground process group at a time. Only that group can read from the terminal. Background groups that try to read get `SIGTTIN`, which stops them. With `stty tostop` set, background writes get `SIGTTOU`.
- **Foreground job**: the shell hands it the terminal (`tcsetpgrp`) and waits for it. When it exits or stops, the shell takes the terminal back.

## Moving jobs around

| Action | Effect |
|---|---|
| `cmd &` | Start in the background. The shell prints `[n] PID` and returns the prompt immediately. |
| `Ctrl-Z` | The terminal driver sends `SIGTSTP` to the foreground group. The job is **Stopped**, and the shell regains control. |
| `Ctrl-C` | Sends `SIGINT` to the foreground group. |
| `bg [%n]` | Sends `SIGCONT` to a stopped job, which keeps running in the background. |
| `fg [%n]` | Resumes the job (if stopped) and gives it the terminal. |
| `jobs [-l\|-p]` | Lists jobs with their state (Running, Stopped, Done). `-l` adds PIDs and `-p` shows only PIDs. |
| `kill %n` | Signals a job by job spec instead of PID. |
| `wait [%n\|PID]` | Blocks until the job finishes and returns its exit status. |
| `disown [-h] [%n]` | Removes the job from the table so the shell won't send it `SIGHUP`. `-h` keeps it in the table but skips the `SIGHUP`. |

## Job specs

- `%n` is job number n.
- `%%` or `%+` is the current job, and `%-` is the previous one.
- `%str` is the job whose command starts with `str`.
- `%?str` is the job whose command contains `str`.

The `+` and `-` marks in `jobs` output show the current and previous jobs. A bare `fg` or `bg` acts on the current job, which is usually the one most recently stopped or backgrounded.

## Status reporting

Bash learns about state changes through `SIGCHLD` and `waitpid`. It normally announces changes (`[1]+ Done ...`, `[1]+ Stopped ...`) just before the next prompt. `set -b` (notify) reports them immediately instead.

## Interaction with shell exit

- When an interactive shell receives `SIGHUP` (for example, when the terminal closes), it forwards `SIGHUP` to its jobs. `nohup`, `disown`, or `setsid` avoid this.
- With `shopt -s huponexit`, bash also sends `SIGHUP` to jobs when a login shell exits normally.
- If you exit with stopped jobs, bash warns once (`There are stopped jobs.`). A second `exit` kills them.

## Practical details

- A pipeline like `a | b | c &` is one job with one process group. `$!` holds the PID of the last process in it, and `$?` is the exit status of the last command. `pipefail` changes how that status is computed.
- Backgrounded jobs still write to your terminal unless you redirect their output. Jobs that need input stop on `SIGTTIN` until you `fg` them.
- Subshells `( ... )` and command substitutions don't have their own job table entries. Only the top-level interactive shell does job control.
- In scripts, `monitor` is off. Background jobs stay in the script's process group and there's no `fg`/`bg`, but `&`, `wait`, and `$!` still work.
- `suspend` suspends the shell itself, and `Ctrl-Z` at the prompt does nothing to the shell.

## Typical workflow

```text
$ vim notes.txt     # editing...
^Z
[1]+  Stopped        vim notes.txt
$ make -j8 &        # build in the background
[2] 4121
$ jobs
[1]+  Stopped        vim notes.txt
[2]-  Running        make -j8 &
$ fg %1             # back to vim
```
