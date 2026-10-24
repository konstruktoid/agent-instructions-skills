Job control lets one interactive terminal run several pipelines and decide which one is in the foreground. It depends on three things: the kernel's terminal and process-group features, the shell's bookkeeping, and a few signals.

## The core pieces

**Process groups and sessions**
- When you log into a terminal, bash becomes the **session leader**, and that terminal is the session's **controlling terminal**.
- Each pipeline you run (`cmd1 | cmd2 | cmd3`) is a **job**. Bash puts all of its processes into their own **process group**, whose ID is the PID of the first process.
- At any moment the terminal has exactly one **foreground process group**. Bash sets it with `tcsetpgrp()`. All the other jobs are background groups.

**What the terminal driver does**
- Keyboard-generated signals go to the *foreground process group only*:
  - `Ctrl-C` sends `SIGINT`
  - `Ctrl-\` sends `SIGQUIT`
  - `Ctrl-Z` sends `SIGTSTP` (suspend)
- A background process that tries to **read** from the terminal gets `SIGTTIN` and is stopped.
- A background process that tries to **write** gets `SIGTTOU`, but only if `stty tostop` is set. Otherwise the output just mixes in with whatever else is on screen.

Bash itself ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU`, so your keystrokes never suspend the shell.

## The life of a job

1. **Foreground launch** (`vim file`): bash forks, puts the child in a new process group, hands it the terminal, and calls `waitpid()`.
2. **Suspend** (`Ctrl-Z`): the job receives `SIGTSTP` and stops. `waitpid()` returns in bash (bash uses `WUNTRACED`), bash takes the terminal back, and prints `[1]+  Stopped  vim file`.
3. **Resume in the background** (`bg %1`): bash sends `SIGCONT` but keeps the terminal, so the job runs without keyboard input.
4. **Resume in the foreground** (`fg %1`): bash gives the terminal to the job's process group, sends `SIGCONT`, and waits again.
5. **Background launch** (`cmd &`): bash never hands over the terminal. It prints `[2] 12345` (job number and PID) and shows the next prompt straight away.
6. **Completion**: bash collects background jobs when `SIGCHLD` arrives. It reports `Done` just before the next prompt, or right away if you've run `set -b`.

## Commands and job specs

| Command | Purpose |
|---|---|
| `jobs` / `jobs -l` | List jobs (`-l` adds PIDs) |
| `fg [spec]` | Bring a job to the foreground |
| `bg [spec]` | Resume a stopped job in the background |
| `kill %spec` | Send a signal to the job's whole process group |
| `wait [spec]` | Block until the job finishes |
| `disown [-h] [spec]` | Remove a job from the table, or with `-h` keep it but don't send it SIGHUP |
| `suspend` | Stop the shell itself (for example, a subshell or an `su` session) |

Ways to name a job (job specs):
- `%n`: job number n
- `%+` or `%%`: the current job (the most recently stopped or backgrounded one)
- `%-`: the previous job
- `%str`: the job whose command starts with *str*
- `%?str`: the job whose command contains *str*

A bare `%1` on its own line means `fg %1`, and `%1 &` means `bg %1`.

## Hangups and logout

- If the terminal closes, the kernel sends `SIGHUP` to the session leader (bash). Bash then sends `SIGHUP` to every job in its table, and first sends `SIGCONT` to any stopped ones so they can act on it.
- If you try to `exit` while jobs are stopped, bash warns `There are stopped jobs.` A second `exit` goes ahead anyway.
- `shopt -s huponexit` makes bash send `SIGHUP` to jobs on a normal login-shell exit as well, not just when the terminal hangs up.
- A process can avoid being killed by the hangup in several ways:
  - `nohup cmd &` ignores SIGHUP and redirects output to `nohup.out` if stdout is a terminal.
  - `disown` stops bash from sending the signal.
  - `setsid cmd` starts a new session with no controlling terminal at all.
  - `tmux` or `screen` keep a terminal alive that doesn't depend on yours.

## Interactive only

Job control (`set -m`, "monitor mode") is **on by default only in interactive shells**. In a script:
- background jobs stay in the shell's own process group,
- `Ctrl-Z` doesn't apply to them,
- `fg` and `bg` fail with "no job control".

Scripts can still use `&`, `wait` and `$!`, which is enough to run work concurrently. You can turn on `set -m` in a script, but it's rarely what you want.

## Common surprises

- **A background job that reads stdin stops** (`[1]+ Stopped (tty input)`). Fix it with `< /dev/null` or by bringing the job to the foreground.
- **`Ctrl-C` doesn't reach background jobs**, because they aren't the foreground group. Use `kill %n`.
- **Pipelines are one unit.** `Ctrl-Z` stops every process in the pipeline, and `kill %1` signals all of them.
- **`$!` only gives the PID of the last process in the pipeline.** `%n` refers to the whole job.
