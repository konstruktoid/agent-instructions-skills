I couldn't find a provisioning script, so I haven't changed anything.

I searched the whole workspace for `mysql`, `mariadb`, `passw` and `DB_`, and nothing matched. The only shell script here is `scripts/backup.sh`. It tars `/srv/ledger/data` and copies it off with `scp`, and it never calls a database or uses a password. None of the other files (Dockerfile, the CI configs, Terraform, the Ansible `roles/nginx`, k8s) call mysql either.

The script may be in another repository or branch, or not committed yet. If you point me to it, the fix would be:

- **Stop passing the password as an argument.** Anything in `-p"$PASS"` or `--password=…` shows up in `ps` and `/proc/<pid>/cmdline` for every local user.
- **Give it to mysql through a private options file.** Create a `mktemp` file with `umask 077` (readable only by its owner) containing `[client]\npassword=…`. Pass it as `--defaults-extra-file=` (this must be the first option), and delete it from an `EXIT` trap that's set before the `mktemp`. A `mysql_config_editor` login path also works, and so does `MYSQL_PWD` as a last resort, though it's deprecated and visible in `/proc/<pid>/environ`.
- **Read the secret from a file or secret store,** not a hardcoded variable. Keep `set -x` turned off around it.

Separately, `scripts/backup.sh` has problems of its own:
- It has no strict mode (`set -Eeuo pipefail`).
- The temp directory is predictable (`/tmp/backup.$$`), which leaves it open to symlink or pre-creation attacks. It should use `mktemp -d`.
- Nothing cleans up if the script exits early, because there's no trap.
- Expansions aren't quoted, and it uses backticks.

I can harden that script too if you'd like.
