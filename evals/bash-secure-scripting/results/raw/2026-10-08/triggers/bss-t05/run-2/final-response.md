I couldn't find a provisioning script, so I haven't changed anything.

I searched the whole workspace for `mysql` and for password-related strings, and nothing matched. The only shell script here is `scripts/backup.sh`, a nightly `tar` + `scp` backup that doesn't use a database or a password. The rest of the workspace is CI configs, Docker and Kubernetes files, an nginx Ansible role, Terraform, and some Go and Python. None of it calls mysql.

**What I need from you:** the path to the provisioning script, or the file itself if it's in another repository or branch. Also, my tools in this session can read files but can't edit or run them. Once I have the script, I can either write out the changed version for you to apply, or make the edit myself in a session that has editing and shell access.

**The fix I'd make:** a password passed as `mysql -p"$DB_PASS"` or `--password=…` shows up in `ps` and `/proc/<pid>/cmdline` for any local user. It can also end up in shell history or `set -x` output. The plan is:
- Write the credentials to a private (mode 600) temporary options file, created with `umask 077` and `mktemp`, with an `EXIT` trap set up first to delete it on every exit path.
- Pass it as the first option: `mysql --defaults-extra-file="${cnf}" …`. The password is written into the file with `printf`, which is a shell builtin, so it never appears on any command line.
- Read the password from wherever it comes from (environment, a secrets file or a vault) without echoing it, and make sure no `set -x` is active around it.
- If the script runs repeatedly, a better long-term option is `mysql_config_editor` (a `--login-path`) or socket authentication, so there's no password in the script at all.
- Then check it with `shellcheck` and `bash -n`, and run it once against a scratch database, including a failure path, to confirm the temporary file is always removed.
