Job control lets one terminal run several pipelines and choose which one is in the foreground. It depends on three pieces working together: the kernel's process groups and sessions, the terminal driver, and bash itself.

## The building blocks

**Process groups and jobs.** Each pipeline you type (`cmd1 | cmd2 | cmd3`) goes into its own process group, and bash treats that group as one **job**. Signals are sent to the whole group, so Ctrl-C stops every stage of the pipeline, not just one process.

**Sessions and the controlling terminal.** Your login shell leads a *session*, and the session is attached to a terminal (tty/pty). At any moment, exactly one process group in the session is the terminal's **foreground process group**. The kernel tracks this, and bash changes it with `tcsetpgrp()`.

**The terminal driver.** The tty line discipline turns special keys into signals and sends them to the *foreground* group only:
- Ctrl-C → `SIGINT`
- Ctrl-\ → `SIGQUIT`
- Ctrl-Z → `SIGTSTP` (stop/suspend)

This is why Ctrl-C reaches your running program and not the shell. While a job runs in the foreground, bash itself is not in the foreground group.

## What bash does

1. **When it starts in interactive mode,** bash turns on job control (`set -m`, on by default in interactive shells). It puts itself in its own process group, takes the terminal, and ignores `SIGTSTP`, `SIGTTIN` and `SIGTTOU` so it can't be suspended by accident.
2. **When it launches a pipeline,** it forks the children and puts them all in a new process group (`setpgid`).
   - **Foreground job:** bash hands the terminal to that group and waits for it to exit or stop.
   - **Background job (`cmd &`):** bash keeps the terminal, prints something like `[1] 12345` (job number and PID), and shows the prompt again straight away.
3. **When the foreground job stops or exits,** bash gets the status back from `waitpid()` (using `WUNTRACED`, so it also sees stops). It then takes the terminal back and prints the prompt. If the job was stopped, bash reports something like `[1]+  Stopped  vim file`.

## Background jobs and the terminal

A background job that tries to **read** from the terminal gets `SIGTTIN`, which stops it by default. The job then shows as `Stopped (tty input)` until you bring it to the foreground.

Whether a background job can **write** to the terminal depends on the `tostop` terminal setting. With `stty tostop` on, writes trigger `SIGTTOU` and stop the job. With it off (the usual default), the output just appears mixed in with whatever you're doing.

## The user-facing commands

| Command | Effect |
|---|---|
| `cmd &` | Start the job in the background |
| Ctrl-Z | Stop (suspend) the foreground job |
| `jobs` / `jobs -l` | List jobs with their state (Running, Stopped, Done); `-l` adds PIDs |
| `fg [%job]` | Give the job the terminal, send it `SIGCONT`, and wait for it |
| `bg [%job]` | Send `SIGCONT` so a stopped job keeps running in the background |
| `kill %job` | Signal the job's whole process group |
| `wait [%job]` | Block until the background job finishes |
| `disown [%job]` | Remove the job from bash's table so it won't get `SIGHUP` when the shell exits |

**Job specs** are the ways to name a job:
- `%1` is job number 1.
- `%+` or `%%` is the current job (marked `+` in `jobs` output) and `%-` is the previous one (marked `-`).
- `%vim` matches the job whose command starts with "vim", and `%?file` matches the job whose command contains "file".

`$!` holds the PID of the most recent background job.

## A typical sequence

```
$ vim notes.txt        # foreground; vim's group owns the tty
^Z                     # tty sends SIGTSTP to vim's group → it stops
[1]+  Stopped   vim notes.txt
$ make > build.log &   # new group, background; bash keeps the tty
[2] 4242
$ jobs
[1]+  Stopped   vim notes.txt
[2]-  Running   make > build.log &
$ fg %1                # tcsetpgrp(vim's group), SIGCONT, wait
```

## Hangups and exiting

- **When the terminal closes** (you close the window or SSH drops), the kernel sends `SIGHUP` to the session leader, which is bash. Bash then passes `SIGHUP` on to its jobs, sending `SIGCONT` first to any that are stopped so they can receive it. With `shopt -s huponexit`, a login shell does this on a normal `exit` too.
- **To keep a job running after you log out,** use `nohup`, `disown`, `setsid`, or a multiplexer like tmux or screen.
- **If you type `exit` while jobs are stopped,** bash warns "There are stopped jobs." Typing `exit` a second time exits anyway. `shopt -s checkjobs` makes bash warn about running jobs as well.

## Why scripts don't do this

Job control is **off by default in non-interactive shells**. In a script, `&` still runs commands in the background and `wait` still works. But the background commands stay in the shell's own process group, so `fg`, `bg`, Ctrl-Z handling and `%job` names mostly don't apply. Bash also makes background commands in a non-interactive shell ignore `SIGINT` and `SIGQUIT`. You can force job control on with `set -m`, but scripts rarely need it.
