I couldn't find a provisioning script that calls `mysql`, so I haven't changed anything.

**What I searched:** every file in the workspace, looking for `mysql`, `mariadb`, `passw`, `provision` and `DB_`. Nothing matched. The only shell script here is `scripts/backup.sh`, a nightly job that archives the data directory and copies it with `scp`. It has no database password. The other files are Terraform, Ansible's nginx role, Kubernetes, Docker, CI config and a Python ledger package, and none of them touch MySQL either.

The script may be in another repository or on a branch that isn't checked out. Also, this session only lets me read and search files, so I couldn't edit a script or run `shellcheck` and `bash -n` on it even once it turns up. If you can point me to it and allow edits and shell commands, I'll apply this fix:

```bash
# Before: the password is visible in `ps` and /proc/<pid>/cmdline
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < schema.sql

# After: pass it through a private option file that is always removed
umask 077
cnf=''
cleanup() { if [[ -n ${cnf} ]]; then rm -f -- "${cnf}"; fi; return 0; }
trap cleanup EXIT
cnf="$(mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASS}" >"${cnf}"
mysql --defaults-extra-file="${cnf}" "${DB_NAME}" <schema.sql
```

- **Why this works:** `printf` is built into Bash, so writing the file doesn't start a new process with the password in its arguments. `--defaults-extra-file` must be the first option given to `mysql`.
- **An alternative:** use `mysql_config_editor` with `--login-path`, or a `~/.my.cnf` set to mode 600.
- **Don't use `MYSQL_PWD`:** MySQL deprecates it, and other processes can read it through `/proc/<pid>/environ`.
- **Where the password comes from:** if the variable is hard-coded in the script, it should be loaded from a secrets store or a root-only file instead, and the leaked password should be rotated. It's in git history.
- **Debug tracing:** I'd make sure no `set -x` runs while the password is set, because the trace would print it.

`scripts/backup.sh` also has unrelated problems. It has no strict mode, it uses a predictable `/tmp/backup.$$` path, it leaves its variables unquoted, and it has no cleanup trap, so a failed run leaves the temporary directory behind. I can harden that too if you want.
