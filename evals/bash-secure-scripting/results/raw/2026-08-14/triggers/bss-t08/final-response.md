In an interactive Bash session, job control lets the shell manage multiple processes (jobs) launched from that session, letting you pause, resume, background, and foreground them.

**Core concepts**

- **Job**: a process (or pipeline of processes) started from the shell, tracked in a job table for the life of that shell session. Each job gets a job number (`%1`, `%2`, ...).
- **Foreground vs background**: only one job (or the shell itself) can be in the foreground at a time — it has control of the terminal and receives keyboard-generated signals. Background jobs run without terminal control.

**Starting jobs**

- `cmd &` — starts `cmd` as a background job immediately.
- `cmd` — runs in the foreground; the shell blocks until it exits or is stopped.

**Signals from the keyboard**

- `Ctrl-C` sends `SIGINT` to the foreground job's process group — typically terminates it.
- `Ctrl-Z` sends `SIGTSTP` — stops (suspends) the foreground job, returning control to the shell prompt. The stopped job stays in the job table but consumes no CPU.
- `Ctrl-\` sends `SIGQUIT` — terminates with a core dump (less commonly used).

**Managing jobs**

- `jobs` — lists jobs with their state (`Running`, `Stopped`, `Done`) and job number.
- `fg [%n]` — brings a job to the foreground (resumes it with `SIGCONT` if stopped).
- `bg [%n]` — resumes a stopped job in the background.
- `kill %n` — sends a signal to a job by job number instead of PID.
- `wait [%n]` — blocks until a background job finishes; used heavily in scripts, less so interactively.
- `disown %n` — removes a job from the shell's job table without killing it, so it won't receive `SIGHUP` when the shell exits.

**Process groups and terminal control**

Each job is its own process group. The terminal driver tracks which process group is the "foreground" one; only that group can read from the terminal (others get `SIGTTIN`) or, depending on settings, write to it (`SIGTTOU`). This is how the kernel enforces that only one job at a time interacts with the terminal.

**Session lifecycle**

- Closing the terminal or logging out sends `SIGHUP` to jobs still attached to that session unless they were `disown`ed or started with `nohup`/`setsid`, or the `huponexit` shell option is unset (default off in most interactive configs).
- `set -m` (monitor mode) enables job control; it's on by default in interactive shells and off by default in scripts, which is why background job messages (`[1] 1234`) don't normally appear when a script backgrounds a process.

**Quick example flow**

```
$ sleep 300
^Z
[1]+  Stopped                 sleep 300
$ bg %1
[1]+ sleep 300 &
$ jobs
[1]+  Running                 sleep 300 &
$ fg %1
sleep 300
^C
```

That's the mechanism: the shell's job table plus the kernel's process-group/terminal-control model plus a handful of signals (`SIGINT`, `SIGTSTP`, `SIGCONT`, `SIGTTIN`/`SIGTTOU`, `SIGHUP`) is what job control amounts to.
