I couldn't find the provisioning script in this workspace, so I haven't changed anything.

- **Nothing matches.** I searched the whole workspace for `mysql`, `passw` and `provision` (case-insensitive) and got no hits.
- **The only shell script is `scripts/backup.sh`.** It's a nightly `tar` + `scp` backup with no database step and no password. It does have its own problems (no strict mode, a guessable `/tmp/backup.$$`, unquoted variables, and it only cleans up if it gets to the end), but that's a different job.
- **I couldn't make the edit anyway.** This session only lets me search and read files. I can't edit files or run `shellcheck` or `bash -n`.

Could you tell me where the script lives, or add it to this workspace? Once I can see it and edit files, the fix is:

1. **Take the password off the command line.** Remove `-p"$password"`/`--password=…` from the `mysql` call. Anything in the arguments shows up to every local user through `ps` and `/proc/<pid>/cmdline`.
2. **Pass it in a private option file instead.** Create a temporary file with `mktemp` under `umask 077`, so only the owner can read it. Set the cleanup `trap … EXIT` (plus INT/TERM handlers that re-raise the signal) *before* creating the file. Write `[client]` / `user=` / `password=` into it with `printf`. `printf` is built into bash, so the password never becomes a command argument. Then call `mysql --defaults-extra-file="$cnf" …`. That flag must come first in the argument list. Two alternatives: a `mysql_config_editor` login path, or an existing root-owned `~/.my.cnf` with mode 0600. The `MYSQL_PWD` environment variable is deprecated and can also leak, so I'd avoid it.
3. **Stop the password reaching the script in plain text.** Don't hardcode it or read it from a file the repo tracks; get it from a secrets store, a root-only file or a systemd credential. Make sure `set -x` is never on around it. Treat the old password as compromised and rotate it, since it has already been visible in the process table and maybe in shell history or CI logs.
4. **Check the result.** Run `shellcheck`, `bash -n` and a test run on a good input and a failing one (wrong password, missing variable). Confirm it exits non-zero, `ps` never shows the password, and the temporary file is gone afterwards.
