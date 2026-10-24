I couldn't find a provisioning script that calls mysql in this workspace, so I haven't changed anything.

- **Search:** Nothing in the repository mentions `mysql`, `password`/`passwd`, `provision` or `db_` (case-insensitive).
- **Shell scripts:** The only one is `scripts/backup.sh`. It does a nightly `tar` of `/srv/ledger/data` and sends it with `scp`, with no database step and no credentials.
- **Other files:** None of the Terraform, CI, Kubernetes, Compose, Ansible or Dockerfile files contain a password or a mysql call either.

The script is probably in another repository or branch, or it hasn't been committed yet. Please tell me its path, or add it here, and I'll fix it. The fix will be:

- **Remove the password from the command line.** Anything passed as `-p"$DB_PASS"` can be read by any local user through `ps` or `/proc/<pid>/cmdline`. Setting it in the `MYSQL_PWD` environment variable has a similar problem.
- **Give it to mysql in a private options file.** Create the file with `mktemp` under `umask 077`, write a `[client]` section with `printf`, and pass it as `mysql --defaults-extra-file="$cnf"`. That option has to come first on the command line. A cleanup trap that removes the file is set up before the file is created. If the machine is set up for it, `mysql_config_editor` / `--login-path` is an alternative.
- **Read the password from a secret file, stdin or a secrets manager**, not from a variable hard-coded in the script, and keep `set -x` away from it.
- **Apply the general hardening at the same time:** strict mode (`set -Eeuo pipefail`), quoted variables, and checks with `shellcheck` and `bash -n`.

Separately, `scripts/backup.sh` has problems of its own that I can fix if you want:
- It uses a predictable temp path (`/tmp/backup.$$`), which can be hijacked with a symlink.
- It has no strict mode, and its variables aren't quoted.
- It has no trap, so the temp data stays behind if the script fails partway.
