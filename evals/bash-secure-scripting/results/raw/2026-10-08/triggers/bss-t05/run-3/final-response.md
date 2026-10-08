I couldn't find a provisioning script in this workspace, so I haven't changed anything.

- **Nothing calls `mysql`.** I searched every file for `mysql` and `password` (case-insensitive), including the CI configs (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `Jenkinsfile`), the `Dockerfile`, `docker-compose.yml` and the Ansible role. None of them matched.
- **The only shell script is `scripts/backup.sh`.** It tars `/srv/ledger/data` and copies it off with `scp`. It has no password and no database step.

Could you point me to the script? It might be on another branch, in another repo, or not committed yet. Once I have it, the fix would be:

- **Stop putting the password on the command line.** Anything passed as `-p"$DB_PASS"` or `--password=…` shows up in `ps` and `/proc/<pid>/cmdline` to every user on the host while the command runs. `MYSQL_PWD` isn't the answer either, because MySQL deprecates it.
- **Write a private client config file instead.** Create it with `mktemp` under `umask 077`, put the password in its `[client]` section, and pass it with `--defaults-extra-file="$cnf"` (it has to be the first option). A `trap … EXIT` installed before the `mktemp` deletes the file on every exit path.
- **Keep the password out of the process table while writing that file.** Use `printf`, which is a Bash builtin, or a here-doc, never `echo` through an external command. Also check that no `set -x` is active around it and that it never gets logged.
- **Read the password from somewhere safer.** Take it from a root-only file or a secrets manager rather than hardcoding it in the variable. If it was ever committed, treat it as exposed and rotate it.

After the edit I'd run `shellcheck` and `bash -n` on the script, then run it once on a normal input and once on a failure path to confirm the temp file is removed either way.

The skill's own reference on secrets (`references/secrets.md`) needed a read permission that wasn't granted, so the steps above are the standard practice rather than that file's exact wording.
