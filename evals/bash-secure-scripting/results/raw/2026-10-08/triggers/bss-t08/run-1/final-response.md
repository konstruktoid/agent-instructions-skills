Bash job control lets one interactive shell run several pipelines ("jobs"), switch which one gets the terminal, and suspend or resume them. It works through the kernel's process-group and session machinery, together with the terminal driver.

## The kernel pieces underneath

- **Session.** Your login terminal session is led by the shell. The terminal (tty) is that session's *controlling terminal*.
- **Process groups.** Bash puts every pipeline it launches into its own process group, so `grep foo log | sort | less` is one group with three processes. That group is the job.
- **Foreground process group.** At any moment the tty has exactly one foreground process group (set with `tcsetpgrp()`). Only that group may read from the terminal, and it is the one that receives keyboard-generated signals:
  - `Ctrl-C` sends `SIGINT`
  - `Ctrl-Z` sends `SIGTSTP` (stop)
  - `Ctrl-\` sends `SIGQUIT`
- **Background groups.** If a background job tries to read from the tty, it gets `SIGTTIN` and stops. If it writes while `stty tostop` is set, it gets `SIGTTOU`. This keeps background jobs from fighting over your keyboard.

Bash ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU` itself, so `Ctrl-Z` never suspends the shell.

## What bash does

1. **Launching a job.** It forks, puts the children into a new process group and records them in its job table.
   - Foreground (`cmd`): bash hands the terminal to that group and `waitpid()`s on it.
   - Background (`cmd &`): bash keeps the terminal and prints `[1] 12345` (job number, PID).
2. **Job stops or finishes.** Bash learns about it through `SIGCHLD`/`waitpid(WUNTRACED)`, takes the terminal back and updates the job table. It prints `[1]+ Stopped ...` or `Done` before the next prompt, or immediately if `set -b` is on.

## Commands

| Command | Effect |
|---|---|
| `jobs` / `jobs -l` | List jobs (`-l` adds PIDs). `+` marks the current job, `-` the previous one |
| `fg [%n]` | Give the terminal to job *n* and send `SIGCONT` if it was stopped |
| `bg [%n]` | Send `SIGCONT` to a stopped job but leave it in the background |
| `kill %n` | Signal the whole job (its process group) |
| `wait [%n]` | Block until the job finishes |
| `disown [%n]` | Remove the job from the table so bash won't send it `SIGHUP` on exit (`-h` keeps it listed but still skips the `SIGHUP`) |
| `suspend` | Stop the shell itself (e.g. a nested shell) |

Ways to refer to a job: `%1`, `%%` or `%+` (current), `%-` (previous), `%vim` (command starts with "vim"), `%?log` (command contains "log"). Typing `%1` alone works like `fg %1`, and `%1 &` works like `bg %1`.

## Typical flow

```
$ vim notes.txt        # foreground
^Z                     # SIGTSTP → [1]+ Stopped  vim notes.txt
$ make > build.log 2>&1 &
[2] 4242
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make > build.log 2>&1 &
$ fg %1                # back into vim
```

## Exit and hangup behaviour

- If you try to exit while jobs are stopped, bash warns "There are stopped jobs." A second `exit` really exits.
- When an interactive login shell gets `SIGHUP` (e.g. the terminal closes), it sends `SIGHUP` to all its jobs, and stopped jobs also get `SIGCONT` so they can act on the hangup. Running jobs get `SIGHUP` on a normal `exit` only if `shopt -s huponexit` is set.
- To keep something running after you log out, use `nohup cmd &`, `disown`, `setsid`, or a multiplexer like tmux or screen.

## Interactive only

Job control is controlled by `set -m` (monitor mode), which is on by default only in interactive shells. In scripts it is off: background jobs stay in the shell's process group, `fg` and `bg` don't work, and `Ctrl-Z` signals the whole group. That's why scripts manage background work with `$!` and `wait` instead.
