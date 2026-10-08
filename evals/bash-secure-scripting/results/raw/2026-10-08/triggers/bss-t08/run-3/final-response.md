Job control lets one interactive shell run several pipelines ("jobs") at once and move them between the foreground and the background. Bash, the kernel's terminal driver and process groups all take part.

## The pieces underneath

- **Process groups.** Bash puts each pipeline in its own process group (`setpgid`), so `cat log | grep err | less` is one job made of three processes. Signals from the terminal go to the whole group.
- **Sessions and the controlling terminal.** The interactive shell leads a session tied to a TTY. That terminal has one **foreground process group** at a time, which bash sets with `tcsetpgrp()`.
- **Terminal-generated signals.** The TTY driver turns special keys into signals and sends them to the foreground group only:
  - `Ctrl-C` → `SIGINT` (interrupt)
  - `Ctrl-Z` → `SIGTSTP` (suspend)
  - `Ctrl-\` → `SIGQUIT`
- **Background access to the TTY.** If a background job tries to read from the terminal, the kernel sends it `SIGTTIN` and it stops. If it writes while `stty tostop` is set, it gets `SIGTTOU`. This keeps background jobs from taking over your input.

## Lifecycle of a job

1. **Start in the foreground:** `make`. Bash gives the job's group the terminal and waits for it (`waitpid` with `WUNTRACED`).
2. **Suspend:** pressing `Ctrl-Z` sends `SIGTSTP`, the job stops, `waitpid` returns, and bash takes the terminal back. You'll see `[1]+  Stopped  make`.
3. **Resume in the background:** `bg` (or `bg %1`) sends `SIGCONT`, and the job keeps running without the terminal.
4. **Bring it back:** `fg %1` gives the job the terminal again, sends `SIGCONT` if it was stopped, and bash waits for it.
5. **Start in the background directly:** `cmd &`. Bash prints `[N] PID`, doesn't wait, and stores the PID in `$!`.

When a background job finishes, bash tells you before the next prompt by default. With `set -b` (`notify`) it tells you immediately.

## Built-ins and job specs

| Command | Purpose |
|---|---|
| `jobs` / `jobs -l` | List jobs (with `-l`, also show PIDs) |
| `fg [%job]`, `bg [%job]` | Move a job to the foreground or background |
| `kill %job` | Send a signal to the job's whole process group |
| `wait [%job]` | Block until a job finishes |
| `disown [%job]` | Remove a job from the table so it doesn't get `SIGHUP` |
| `suspend` | Stop the shell itself (for example, a nested shell) |

Job specs: `%1` (by number), `%+` or `%%` (current job, marked `+`), `%-` (previous job, marked `-`), `%vim` (command starts with "vim"), `%?log` (command contains "log").

## Hangups and leaving the shell

- When the terminal closes, bash gets `SIGHUP` and passes it on to all its jobs, sending `SIGCONT` to stopped ones first so they can handle it.
- `disown`, `nohup cmd &` or `shopt -s huponexit` (which sends SIGHUP on a login shell's normal `exit`) change that behaviour.
- If you type `exit` while jobs are stopped, bash warns "There are stopped jobs." A second `exit` really quits. `shopt -s checkjobs` adds a warning for running jobs too.

## Interactive vs. scripts

Job control (`set -m`, the `monitor` option) is on by default only in interactive shells. In a non-interactive script, background jobs stay in the shell's own process group and `Ctrl-Z` doesn't apply. Commands like `fg` fail unless you run `set -m` explicitly. Scripts normally just use `&`, `$!` and `wait`.
