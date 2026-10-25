# Job control in an interactive bash session

Job control lets one terminal run several pipelines at once. You can suspend them, resume them, and move them between the **foreground**, which owns the terminal, and the **background**, which doesn't.

## The pieces underneath

1. **Process groups.** Bash puts each pipeline in its own process group, so `cmd1 | cmd2 | cmd3` is one job and one group. Signals sent to a job go to the whole group.
2. **Sessions and the controlling terminal.** Your login shell leads a session that is attached to a TTY. Only one process group in that session can be the **foreground process group** at a time.
3. **Terminal ownership.** Bash uses `tcsetpgrp()` to tell the kernel which group is in the foreground. Keyboard-generated signals go only to that group:
   - `Ctrl-C` sends `SIGINT`
   - `Ctrl-\` sends `SIGQUIT`
   - `Ctrl-Z` sends `SIGTSTP` (suspend)
4. **Background TTY access.** If a background job tries to *read* from the terminal, the kernel stops it with `SIGTTIN`. If it tries to *write* and `stty tostop` is set, it is stopped with `SIGTTOU`. By default, background output still goes to the screen.
5. **Watching job state.** Bash calls `waitpid()` with `WUNTRACED`/`WCONTINUED`, so it notices when a job stops, continues or exits. It then updates its job table and tells you, normally just before the next prompt. With `set -b` it tells you immediately.

## Day-to-day use

| Action | Effect |
|---|---|
| `cmd &` | Start the job in the background. Bash prints `[1] 12345` (job number and PID). |
| `Ctrl-Z` | Suspend the foreground job. It shows as `Stopped`. |
| `jobs` / `jobs -l` | List jobs, with `-l` adding PIDs. `+` marks the current job and `-` the previous one. |
| `fg [%job]` | Give the job the terminal, send `SIGCONT`, and wait for it. |
| `bg [%job]` | Send `SIGCONT` to a stopped job and let it keep running in the background. |
| `kill %job` | Signal the job's whole process group. |
| `wait [%job]` | Block until the job finishes. |
| `disown [%job]` | Remove the job from bash's table, so bash won't send it `SIGHUP` when the shell exits. |

**Ways to name a job:** `%1` (job number), `%+` or `%%` (current job), `%-` (previous job), `%vim` (command starts with "vim"), `%?log` (command contains "log").

Typing `%1` on its own works like `fg %1`, and `%1 &` works like `bg %1`.

## Hangups and exiting

- When the terminal closes, bash gets `SIGHUP`. It then sends `SIGHUP` to every job, and first sends `SIGCONT` to stopped jobs so they can actually receive it.
- With `shopt -s huponexit`, an interactive login shell also sends `SIGHUP` to its jobs when you exit normally.
- If you type `exit` while jobs are stopped, bash warns "There are stopped jobs." A second `exit` goes through anyway.
- Ways to keep a job alive after logout:
  - `nohup cmd &`, which ignores `SIGHUP` and redirects output
  - `disown`
  - `setsid cmd`, which gives it a new session with no controlling TTY
  - running it inside `tmux` or `screen`

## Why it's interactive-only

Job control is controlled by `set -m` (monitor mode). It is on by default in interactive shells and off in scripts. In a script, background jobs therefore stay in the shell's own process group, `Ctrl-Z` handling and `fg`/`bg` don't apply, and you manage children with `$!`, `wait` and `kill PID`. You can force job control on in a script with `set -m`, but it is rarely what you want.
