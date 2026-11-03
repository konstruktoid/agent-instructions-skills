Job control in interactive bash is a cooperation between the shell, the kernel's terminal (TTY) driver, and process groups.

## The building blocks

**Process groups and sessions**
- When you log in or open a terminal, bash becomes a **session leader**, and the terminal becomes that session's **controlling terminal**.
- Each pipeline you run (e.g. `grep foo file | sort | less`) goes into its own **process group**, and bash calls that group a **job**. Every process in the pipeline shares one process group ID (PGID), which is normally the PID of the first process.
- At any moment one process group is the terminal's **foreground process group**. Bash sets it with `tcsetpgrp()`.

**Why this matters**
The TTY driver sends keyboard-generated signals to the *whole foreground process group*, not to one process:
- `Ctrl-C` → `SIGINT`
- `Ctrl-\` → `SIGQUIT`
- `Ctrl-Z` → `SIGTSTP` (stop/suspend)

So `Ctrl-C` kills every stage of a pipeline at once, and it leaves bash alone, because bash is not in that group while a job runs in the foreground.

## Foreground vs. background

| Action | What bash does |
|---|---|
| `cmd` | Puts `cmd` in a new process group, gives that group the terminal, and `waitpid()`s until it exits or stops. Then bash takes the terminal back. |
| `cmd &` | Puts `cmd` in a new process group but keeps the terminal for itself. Prints `[1] 12345` (job number and PID) and returns to the prompt right away. |
| `Ctrl-Z` | The TTY sends `SIGTSTP`, the job stops, and `waitpid()` reports the stop to bash. Bash prints `[1]+ Stopped` and takes the terminal back. |

**Background jobs and the terminal:**
- If a background job tries to **read** from the terminal, the kernel sends it `SIGTTIN`, which stops it. It can't steal your keystrokes.
- If it tries to **write**, it normally can. If `stty tostop` is set, it gets `SIGTTOU` and stops instead.

## The built-in commands

- `jobs` lists jobs. `jobs -l` adds PIDs. In the output, `+` marks the current job and `-` the previous one.
- `fg [%job]` gives the job the terminal, sends it `SIGCONT` if it was stopped, and waits for it.
- `bg [%job]` sends a stopped job `SIGCONT` but leaves it in the background.
- `kill %job` signals the whole process group, e.g. `kill -STOP %2` or `kill %1`.
- `wait [%job]` blocks until the job finishes.
- `disown [%job]` removes the job from bash's table, so bash won't send it `SIGHUP` when it exits. `disown -h` keeps the job listed but still skips the `SIGHUP`.
- `suspend` stops bash itself, which is useful in a nested shell or after `su`.

**Ways to refer to a job:**
- `%1` is job number 1.
- `%%` or `%+` is the current job, and `%-` is the previous one.
- `%vim` is the job whose command starts with "vim".
- `%?log` is the job whose command contains "log".
- A bare `%1` on its own line works like `fg %1`, and `%1 &` works like `bg %1`.

## Notifications and state tracking

Bash watches for `SIGCHLD` and reaps child state changes with `waitpid(..., WUNTRACED | WCONTINUED)`. By default it reports finished background jobs (`[1]+ Done ...`) just before printing the next prompt. With `set -b` (`set -o notify`), it reports them immediately instead.

## Hangups and exiting

- When the terminal closes, the session leader (bash) gets `SIGHUP`. Bash passes `SIGHUP` on to all its jobs, sending `SIGCONT` first to any that are stopped so they can handle it.
- If you type `exit` while jobs are **stopped**, bash warns "There are stopped jobs." Typing `exit` a second time exits anyway.
- With `shopt -s huponexit`, bash also sends `SIGHUP` to jobs when an interactive login shell exits normally.
- To keep a job alive after you log out, use `nohup`, `disown`, `setsid`, or a multiplexer like tmux or screen.

## Interactive vs. non-interactive

Job control (`set -m` / `set -o monitor`) is **on by default only in interactive shells**. In scripts it's off:
- Background jobs stay in the shell's own process group.
- `Ctrl-Z` handling, `fg`, and `bg` don't apply in the usual way.
- Background commands ignore `SIGINT` and `SIGQUIT`.

You can run `set -m` in a script to turn it on, but scripts usually rely on `wait` and `$!` instead.

## A typical flow

```
$ vim notes.txt        # foreground; vim owns the terminal
^Z                     # SIGTSTP → [1]+ Stopped  vim notes.txt
$ make -j8 > build.log 2>&1 &   # [2] 4242, runs in background
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make -j8 > build.log 2>&1 &
$ fg %1                # SIGCONT + terminal handed back to vim
```

In short, bash puts each pipeline in its own process group, decides which group owns the terminal, and uses `SIGCONT` and `waitpid()` to move jobs between running, stopped, foreground and background. The kernel's TTY driver does the rest.
