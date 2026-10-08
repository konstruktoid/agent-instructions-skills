This is a conceptual question about interactive shells, so here's the explanation directly.

## Job control in interactive bash

### The pieces
- **Process groups:** Bash puts each pipeline you launch (e.g. `grep foo log | sort`) into its own process group. That group is one **job**. Signals from the terminal go to a whole group at once, which is why Ctrl-C stops every process in a pipeline.
- **Sessions and the controlling terminal:** The shell leads a session tied to a terminal (tty). The terminal driver tracks one **foreground process group**. Only that group can read from the terminal, and it's the group that gets keyboard-generated signals.
- **Job table:** Bash keeps a numbered list of its jobs. Each job is marked Running, Stopped or Done.

### Foreground vs background
- `cmd` runs in the **foreground**. Bash gives the terminal to the job's process group with `tcsetpgrp()` and waits. When the job exits or stops, bash takes the terminal back.
- `cmd &` runs in the **background**. Bash prints `[1] 12345` (job number and PID) and gives you a prompt right away. `$!` holds the PID of the last background job.

### Keyboard signals (sent by the terminal driver, not bash)
| Key | Signal | Default effect |
|---|---|---|
| Ctrl-C | `SIGINT` | terminate |
| Ctrl-\ | `SIGQUIT` | terminate + core dump |
| Ctrl-Z | `SIGTSTP` | stop (suspend) |

All of these go only to the foreground process group. Bash itself ignores them while it's waiting at the prompt.

### Builtins
- `jobs` (or `jobs -l` to include PIDs) lists jobs.
- `fg %n` moves job *n* to the foreground. If it was stopped, bash sends it `SIGCONT`.
- `bg %n` resumes a stopped job in the background with `SIGCONT`.
- `kill %n` sends a signal to a job's whole process group.
- `wait [%n]` blocks until a job finishes.
- `disown [-h] %n` removes a job from the table so bash won't send it `SIGHUP` when the shell exits. `-h` keeps the job in the table but still skips the `SIGHUP`.
- `suspend` stops the shell itself, for example a sub-shell started with `su`.

### Job specs
- `%n` is job number *n*.
- `%+` or `%%` is the current job (the most recent one) and `%-` is the previous one.
- `%str` is the job whose command starts with *str*, and `%?str` is the job whose command contains *str*.
- A bare `%1` works as shorthand for `fg %1`, and `%1 &` for `bg %1`.

### Background jobs and the terminal
- If a background job tries to **read** from the tty, it gets `SIGTTIN` and stops. You'll see `[1]+ Stopped (tty input)`.
- If it **writes** to the tty, the output normally just appears. If `stty tostop` is set, the job gets `SIGTTOU` and stops instead.

### State-change notification
Bash learns that a child stopped or exited from `SIGCHLD` / `waitpid(..., WUNTRACED)`. By default it reports the change just before the next prompt. With `set -b` (`notify`) it reports immediately.

### Exiting the shell
- If you try to exit while jobs are **stopped**, bash warns "There are stopped jobs." A second `exit` really quits.
- With `shopt -s checkjobs`, bash also warns about running jobs.
- When the shell exits because the terminal hung up, it sends `SIGHUP` to all jobs. With `shopt -s huponexit`, it also does this on a normal login-shell exit. `nohup`, `disown` and `setsid` are the usual ways to keep a job alive past that.

### Scripts vs interactive shells
Job control (the `monitor` option, `set -m`) is **on by default only in interactive shells**. In a script, background jobs stay in the shell's own process group, `fg` and `bg` don't work, and Ctrl-Z isn't handled per job. You can turn it on with `set -m`, but scripts rarely need it. `wait` and `$!` work without it.
