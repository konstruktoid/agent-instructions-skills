Job control is how an interactive bash shell lets you run several pipelines, stop and resume them, and choose which one has the terminal. It depends on three pieces working together: the kernel's process groups and sessions, the terminal driver, and bash's own bookkeeping.

## The pieces underneath

**Process groups and sessions.** Every process belongs to a process group, and every process group belongs to a session. Your login terminal session is led by the shell. When bash runs a pipeline such as `grep foo log | sort | less`, it puts all of its processes into one new process group. The group ID is the PID of the first process. To bash, that whole group is one **job**.

**The controlling terminal and the foreground group.** A terminal has one *foreground process group* at a time. Bash sets it with `tcsetpgrp()`. This decides two things:
- **Who receives keyboard signals.** When you press Ctrl-C, Ctrl-Z or Ctrl-\, the terminal driver sends `SIGINT`, `SIGTSTP` or `SIGQUIT` to every process in the foreground group. Bash doesn't send these signals itself.
- **Who may read the terminal.** If a background process tries to read from the terminal, the kernel sends it `SIGTTIN`, which stops it. If it tries to write while `stty tostop` is set, it gets `SIGTTOU`.

**Bash's role.** While a foreground job runs, bash gives that job the terminal and waits on it with `waitpid(..., WUNTRACED)`. When the job exits or stops, bash takes the terminal back and prints a prompt. Bash ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU` itself, so the shell isn't suspended along with your job.

## Day-to-day use

| Action | What happens |
|---|---|
| `cmd &` | Starts the job in its own process group without giving it the terminal. Bash prints `[1] 12345` (job number and PID of the last process) and returns to the prompt. |
| **Ctrl-Z** | The terminal sends `SIGTSTP` to the foreground group, and the job stops. Bash sees that through `WUNTRACED`, takes the terminal back and reports `[1]+ Stopped`. |
| `jobs` / `jobs -l` | Lists jobs with their state (Running, Stopped, Done). `-l` adds PIDs. |
| `fg %n` | Gives job *n* the terminal, sends it `SIGCONT`, and waits for it. |
| `bg %n` | Sends job *n* `SIGCONT` but keeps it in the background, so it runs without the terminal. |
| `kill %n` | Sends a signal to the whole process group, so every process in the pipeline gets it. |
| `wait %n` | Blocks until the job finishes. |
| `disown %n` | Removes the job from bash's table, so bash won't send it `SIGHUP` when it exits. |

**Job specs:** `%n` is job number *n*. `%+` or `%%` is the current job (the most recent one), and `%-` is the previous job. `%str` matches a job whose command starts with *str*, and `%?str` matches one whose command contains *str*. A bare `%1` on its own line works like `fg %1`, and `%1 &` works like `bg %1`.

## Notifications and hangups

- **State changes.** Bash learns about job changes through `SIGCHLD`. It normally reports them just before the next prompt, so they don't interrupt your typing. `set -b` (`notify`) reports them immediately instead.
- **Hangups.** When the terminal hangs up, for example when you close an SSH session, bash gets `SIGHUP`. It sends `SIGHUP` to all its jobs, and also sends `SIGCONT` to stopped ones so they can handle it. It also does this on a normal `exit` if `shopt -s huponexit` is set.
- **Ways to keep a job alive:** `disown`, `disown -h` (keep the job listed but don't send it `SIGHUP`), `nohup cmd &`, or `setsid`, which starts the command in a new session with no controlling terminal.
- **Exiting with stopped jobs.** Bash warns "There are stopped jobs" and only exits on your second attempt. `shopt -s checkjobs` also warns about running jobs.

## Interactive versus script

Job control is the `monitor` option (`set -m`). It's on by default in interactive shells and off in scripts. With it off:
- Background jobs stay in the shell's own process group instead of getting their own.
- Background commands have `SIGINT` and `SIGQUIT` ignored, so Ctrl-C at the terminal doesn't kill them.
- `fg`, `bg` and Ctrl-Z suspension don't work. `wait` and `$!` still work.

That's why a script should manage its children with `$!`, `wait` and `trap` rather than with `%job` syntax.

## Small details worth knowing

- **`$!`** is the PID of the last process in the most recent background pipeline, not the group ID.
- **Subshells and pipelines.** Inside a subshell, job control is turned off. By default, each part of a pipeline runs in a subshell. `shopt -s lastpipe` runs the last part in the current shell, but only when job control is off.
- **A stopped background job** shows as `Stopped (tty input)` when it tried to read the terminal and got `SIGTTIN`. `fg` it to give it input.
