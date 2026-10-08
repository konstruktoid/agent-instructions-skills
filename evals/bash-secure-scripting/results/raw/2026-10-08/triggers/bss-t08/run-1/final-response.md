Job control is how an interactive Bash session runs several pipelines ("jobs") at once and moves them between the foreground and background. Some of the work is done by Bash and some by the kernel's terminal (TTY) driver.

## The core pieces

**1. Process groups and sessions**
- When you log in or open a terminal, the shell becomes a **session leader**. The terminal becomes the session's **controlling terminal**.
- Each pipeline you run (`cmd1 | cmd2 | cmd3`) goes into its own **process group**. That group is the "job". Bash calls `setpgid()` on each child so every process in the pipeline shares one process group ID (PGID).
- At any moment, exactly one process group is the terminal's **foreground process group**. Bash sets it with `tcsetpgrp()`.

**2. Foreground vs. background**
- **Foreground job:** its process group owns the terminal. It can read keyboard input and receives keyboard-generated signals. Bash waits for it to finish or stop before showing the prompt again.
- **Background job** (started with a trailing `&`): Bash doesn't wait for it. Bash takes the terminal back right away and prints something like `[1] 12345` (job number and PID of the last process in the pipeline).

**3. Signals from the terminal driver**
The TTY driver, not Bash, turns special keys into signals and sends them to the **whole foreground process group**:

| Key | Signal | Default effect |
|---|---|---|
| `Ctrl-C` | `SIGINT` | terminate |
| `Ctrl-\` | `SIGQUIT` | terminate + core dump |
| `Ctrl-Z` | `SIGTSTP` | stop (suspend) |

Bash ignores these signals itself while it waits, so it survives and keeps control.

**4. Background jobs touching the terminal**
- If a background job tries to **read** from the terminal, the kernel sends its group `SIGTTIN`, which stops it by default.
- If it tries to **write** and `stty tostop` is set, it gets `SIGTTOU`. Without `tostop`, background output is simply mixed into your screen.

**5. How Bash notices changes**
Bash calls `waitpid()` with `WUNTRACED`/`WCONTINUED` (and handles `SIGCHLD`) to learn when children exit, stop or continue. It updates its job table and normally reports the change just before the next prompt. With `set -b` (`notify`) it reports immediately.

## User-facing commands

- `jobs` lists jobs with their state (`Running`, `Stopped`, `Done`). `jobs -l` also shows PIDs.
- `fg [%job]`: Bash makes the job's group the terminal's foreground group, sends `SIGCONT` if the job is stopped, then waits for it.
- `bg [%job]`: Bash sends `SIGCONT` to a stopped job and leaves it in the background.
- `kill %job`: sends a signal to the job's whole process group.
- `wait [%job]`: blocks until the job finishes.
- `disown [%job]`: removes the job from Bash's table so it won't be sent `SIGHUP` when the shell exits. `disown -h` keeps the job in the table but still skips the `SIGHUP`.
- `suspend`: stops the shell itself, for example a sub-shell started from another shell.

**Ways to name a job:**
- `%1`: job number 1
- `%%` or `%+`: the current job (the most recent one stopped or backgrounded)
- `%-`: the previous job
- `%vim`: the job whose command starts with "vim"
- `%?log`: the job whose command contains "log"
- A bare `%1` on its own line is shorthand for `fg %1`, and `%1 &` is shorthand for `bg %1`.

## A typical flow

```
$ vim notes.txt        # foreground job
^Z                     # TTY sends SIGTSTP → vim stops
[1]+  Stopped   vim notes.txt
$ make > build.log 2>&1 &
[2] 4242
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make > build.log 2>&1 &
$ fg %1                # tcsetpgrp + SIGCONT → vim resumes in foreground
```

## Hangups and exit
- When the terminal closes, the session leader (Bash) gets `SIGHUP`. Bash passes `SIGHUP` on to all its jobs and sends `SIGCONT` to stopped ones first so they can handle it.
- With `shopt -s huponexit`, a normal `exit` from a login shell also sends `SIGHUP` to jobs.
- If you try to exit while jobs are stopped, Bash warns "There are stopped jobs." A second `exit` goes ahead anyway. With `shopt -s checkjobs`, Bash also warns about running jobs.
- `nohup`, `disown` and `setsid` are the usual ways to keep a job alive after logout.

## Interactive only
Job control is on by default in interactive shells (`set -m`, also called `monitor`). In non-interactive scripts it is off: background jobs share the shell's process group, `fg`/`bg` aren't useful, and background commands have `SIGINT`/`SIGQUIT` ignored and stdin redirected from `/dev/null`. You can turn it on in a script with `set -m`, but that's rarely what you want. In scripts, use `&` together with `wait` and `$!` instead.
