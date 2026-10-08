# Job control in an interactive bash session

## What a job is

A **job** is a pipeline or command the shell started and tracks. Each job is a **process group** (every process in the pipeline shares one PGID). Bash gives each job a small number (`%1`, `%2`, …) separate from PIDs.

Job control is on by default in interactive shells (`set -m`, or `set -o monitor`). It is off in scripts. Scripts have no controlling terminal and don't need it.

## The terminal side

- The shell and its jobs share one **controlling terminal**.
- The terminal has one **foreground process group**. Only that group can read from the terminal. The kernel delivers keyboard signals (`Ctrl-C`, `Ctrl-Z`, `Ctrl-\`) to it.
- Bash puts each job in its own process group. It hands the terminal to the job with `tcsetpgrp()` when the job runs in the foreground. It takes the terminal back when the job stops or exits.
- **Background** jobs are not in the foreground group. If one tries to read from the terminal, it gets `SIGTTIN` and stops. If `stty tostop` is set, writing to the terminal does the same with `SIGTTOU`.

## Job states

| State | Meaning |
|---|---|
| Running (foreground) | Owns the terminal. The shell waits for it. |
| Running (background) | Runs concurrently. The prompt returns immediately. |
| Stopped | Suspended by `SIGTSTP`, `SIGSTOP`, `SIGTTIN` or `SIGTTOU`. It is not scheduled. |
| Done / Exit N | Finished. Bash reports it at the next prompt. |

## Everyday commands

- `cmd &` starts a job in the background. Bash prints `[1] 12345`, the job number and the PID of the last process.
- `Ctrl-Z` sends `SIGTSTP` to the foreground job, which stops it and returns you to the prompt.
- `jobs` lists jobs. `-l` adds PIDs and `-p` prints only PIDs.
- `bg [%n]` sends `SIGCONT` to a stopped job and leaves it running in the background.
- `fg [%n]` resumes a job in the foreground and gives it the terminal.
- `kill %n` signals a job. This is useful because `kill` accepts job specs.
- `wait [%n|pid]` blocks until the job finishes and returns its exit status.
- `disown [-h] [%n]` removes a job from the table. With `-h` it keeps the job but stops bash from sending it `SIGHUP`.
- `suspend` stops the shell itself.

## Job specs

- `%n` is job number n.
- `%%` or `%+` is the current job. `%-` is the previous one.
- `%str` is the job whose command begins with `str`.
- `%?str` is the job whose command contains `str`.
- A bare `%1` works as shorthand for `fg %1`. `%1 &` works as shorthand for `bg %1`.

The `+` and `-` markers in `jobs` output show the current and previous jobs. The current job is the most recently stopped or backgrounded one. It is the default for `fg` and `bg`.

## Notifications and exit

- Bash normally reports job status changes just before it prints the next prompt. `set -b` (`notify`) reports them immediately.
- If you exit with stopped jobs, bash warns "There are stopped jobs." A second `exit` immediately afterward kills them. With the `checkjobs` shopt it also warns about running jobs.
- When an interactive shell gets `SIGHUP` (for example, the terminal closes), it forwards `SIGHUP` to its jobs. Ways around this:
  - `nohup cmd &`
  - `disown -h`
  - `shopt -s huponexit` does the opposite and sends `SIGHUP` on a normal exit.
  - A terminal multiplexer such as `tmux` or `screen`.

## Pipelines and details

- The whole pipeline is one job. `Ctrl-Z` stops all of its processes together.
- `$!` holds the PID of the most recent background job. `$?` after `wait` gives its exit status.
- A job in a subshell, such as `( a; b ) &`, is one job. Bash tracks the subshell, not the commands inside it.
- Background jobs inherit stdin from `/dev/null` only when job control is off. With it on, a backgrounded job that reads the terminal is stopped by `SIGTTIN`. Redirect stdin (`< /dev/null`) if that's not what you want.
- `Ctrl-C` goes to the foreground group only, so background jobs aren't affected.
- Programs that trap or ignore `SIGTSTP` or `SIGINT`, such as editors, handle those keys themselves. Bash can't suspend them the usual way.

## Typical flow

```
$ sleep 300          # runs in foreground
^Z                   # SIGTSTP
[1]+  Stopped        sleep 300
$ bg                 # SIGCONT, now in background
[1]+ sleep 300 &
$ jobs -l
$ fg %1              # back in foreground
^C                   # SIGINT, job ends
```

## Under the hood

When bash launches a job with job control enabled, it does the following:

1. It forks each pipeline member and calls `setpgid()` so they share a new process group.
2. For a foreground job, it calls `tcsetpgrp()` to give that group the terminal.
3. It waits with `waitpid(..., WUNTRACED)` so it also learns when a child stops, not only when it exits.
4. When the job stops or finishes, it takes the terminal back and updates its job table.

The shell ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU` for itself. Children restore the default handlers, so they can be stopped.
