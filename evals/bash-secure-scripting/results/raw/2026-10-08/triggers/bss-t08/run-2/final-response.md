Job control lets one interactive shell run several pipelines at once, move them between the foreground and background, and pause or resume them. It depends on three things working together: the kernel's process groups and sessions, the terminal driver, and bash itself.

## The building blocks

**Process groups and sessions**
- Each pipeline you start becomes a **job**. Bash puts all of its processes (for example, every command in `a | b | c`) into a single **process group**. The group ID is the PID of the first process.
- The shell and all of its jobs belong to one **session**, and that session is tied to a **controlling terminal** (your tty or pty).

**The foreground process group**
- At any moment the terminal has exactly one foreground process group. Bash sets it with `tcsetpgrp()`.
- Only the foreground group can read from the terminal. A background group that tries to read gets **SIGTTIN**, and by default that stops it. If `stty tostop` is set, a background write gets **SIGTTOU** and stops too.

**Keyboard-generated signals**
The terminal driver, not bash, turns certain keys into signals. It sends them to the **whole foreground process group**:

| Key | Signal | Default effect |
|---|---|---|
| Ctrl-C | SIGINT | terminate |
| Ctrl-\ | SIGQUIT | terminate + core dump |
| Ctrl-Z | SIGTSTP | stop (suspend) |

Bash ignores these signals while it waits for a foreground job, so pressing Ctrl-C kills the job and leaves your shell running.

## What bash does

1. **Launching:** For a command line without `&`, bash forks, puts the children in a new process group, makes that group the terminal's foreground group, and waits with `waitpid(..., WUNTRACED)`. A command ending in `&` also gets its own group, but bash keeps the terminal itself and returns to the prompt straight away. It prints something like `[1] 12345`.
2. **Detecting state changes:** When a child stops or exits, the kernel sends **SIGCHLD**. Bash records the new state in its job table. If you press Ctrl-Z, `waitpid` reports the job as stopped. Bash then takes the terminal back, saves the job's terminal modes, and prints `[1]+  Stopped  vim`.
3. **Reporting:** By default bash reports background job changes just before the next prompt. With `set -b` (notify) it reports them immediately.

## The user-facing commands

- `jobs` lists jobs. `jobs -l` adds PIDs, and `jobs -p` shows only the PIDs.
- `fg %n` makes job *n* the foreground group with `tcsetpgrp`, restores its terminal modes, sends **SIGCONT**, and waits for it.
- `bg %n` sends **SIGCONT** to a stopped job but leaves it in the background.
- `kill %n` sends a signal to the job's whole process group. Job specs work in any built-in that accepts a PID.
- `wait [%n]` blocks until the job finishes.
- `disown %n` removes the job from the table, so bash won't send it SIGHUP when the shell exits. `disown -h` keeps the job listed but still skips the SIGHUP.
- `suspend` stops the shell itself, which is useful inside `su` or a nested shell.

**Job specs:**
- `%n` is job number *n*.
- `%+` or `%%` is the current job, the one most recently stopped or backgrounded.
- `%-` is the previous job.
- `%str` is a job whose command starts with *str*.
- `%?str` is a job whose command contains *str*.
- `%1 &` is shorthand for `bg %1`, and a bare `%1` is shorthand for `fg %1`.

## Hangups and exiting

- If the terminal closes, the kernel sends **SIGHUP** to the session leader, which is bash. Bash forwards SIGHUP to all its jobs and sends SIGCONT to stopped ones so they can act on it.
- With `shopt -s huponexit`, bash also sends SIGHUP to jobs when an interactive login shell exits normally.
- If you try to exit while jobs are stopped, bash warns "There are stopped jobs." A second `exit` really exits. `shopt -s checkjobs` extends the warning to running jobs as well.
- `nohup cmd &` or `setsid cmd` are other ways to keep a process alive after logout. `nohup` makes the process ignore SIGHUP. `setsid` moves it into a new session with no controlling terminal.

## Interactive vs. scripts

Job control is the `monitor` option (`set -m`). It is on by default only in interactive shells. In a non-interactive script:
- Background jobs stay in the script's own process group.
- `fg` and `bg` mostly don't apply.
- Ctrl-Z isn't handled per job.

`&`, `wait`, and `$!` still work in scripts. That's why scripts usually manage children with `wait "$pid"` and `kill "$pid"` rather than `%n` job specs.

## A typical flow

```
$ vim notes.txt        # foreground; press Ctrl-Z
[1]+  Stopped                 vim notes.txt
$ make -j8 > build.log 2>&1 &
[2] 40211
$ jobs
[1]+  Stopped                 vim notes.txt
[2]-  Running                 make -j8 > build.log 2>&1 &
$ fg %1                # vim back, terminal handed to its process group, SIGCONT sent
```
