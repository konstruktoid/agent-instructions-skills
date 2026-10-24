I couldn't find the provisioning script, so I haven't changed anything.

I searched this workspace for `mysql`, `mariadb`, `passw`, `provision` and `DB_` and nothing matched. The only shell script here is `scripts/backup.sh`, a nightly `tar` and `scp` backup with no database step. The other files are `Dockerfile`, `docker-compose.yml`, `k8s/deployment.yml`, `infra/main.tf`, the CI configs and the Ansible `roles/nginx`, and none of them call `mysql`.

**Can you tell me where the script is?** It may be in another repository or branch, or not committed yet. Once I have it, the fix I'd make is:

- **Stop using `-p"$DB_PASS"` or `--password=...`.** Anything on the command line can be seen by other users on the host through `ps` and `/proc/<pid>/cmdline`.
- **Pass the password in an options file instead.** The script would create a temporary file with `mktemp` under `umask 077`, so only its owner can read it. It would write a `[client]` section into it using `printf`, which is built into Bash and so doesn't put the password on a command line either. Then it would run `mysql --defaults-extra-file="$tmp" ...`, which must be the first option. A cleanup step that runs whenever the script exits would delete the file.
- **Or skip the temporary file if the setup allows it.** `mysql_config_editor` (a stored `--login-path`) or socket authentication for a local root account would avoid it entirely.
- **Avoid the other leak routes.** That means not exporting `MYSQL_PWD`, which MySQL itself says is insecure, and keeping `set -x` away from any line that handles the password.
- **Check the result.** I'd run `shellcheck` and `bash -n` on the script, then run it.

**A separate problem in `scripts/backup.sh`:** it uses a predictable `/tmp/backup.$$` directory, leaves its variables unquoted, has no strict mode and doesn't clean up if it fails partway. I can fix that too, but it's a different change from the one you asked for.
