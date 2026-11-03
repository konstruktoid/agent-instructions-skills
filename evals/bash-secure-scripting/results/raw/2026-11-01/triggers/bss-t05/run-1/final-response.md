I didn't change anything: there's no provisioning script in this workspace.

**What I searched:**
- **Every file in the workspace.** The only shell script is `scripts/backup.sh`, and it's a nightly backup (`tar` + `scp`). It doesn't use `mysql` or a password.
- **`mysql` across the whole repo:** no matches.
- **Password-related terms (`passw`, `provision`, `-p$`):** no matches.

None of the CI, Docker, Kubernetes, Terraform or Ansible files contain it either, so the script is probably in another repo or branch, or hasn't been committed yet. Also, this session doesn't give me a tool to edit files. Once you point me at the script, I can write the change for you to apply, or apply it myself if editing is turned on.

**The fix I'll make once I have it:** a password passed on the `mysql` command line can be seen by any local user through `ps` and `/proc/<pid>/cmdline`. It also ends up in shell history and `set -x` output. The script should hand the password to `mysql` through a private options file instead:

```bash
umask 077
creds=''
cleanup() { if [[ -n ${creds} ]]; then rm -f -- "${creds}"; fi; return 0; }
trap cleanup EXIT            # installed before mktemp
creds="$(mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASSWORD}" >"${creds}"
mysql --defaults-extra-file="${creds}" -h "${DB_HOST}" -- "${DB_NAME}" <schema.sql
```

- `printf` is a shell builtin, so the password never shows up as a process argument. It still needs to come in from a file or secret store, not a literal in the script.
- `--defaults-extra-file` must be the first option given to `mysql`.
- Don't use `MYSQL_PWD` as a substitute: MySQL has deprecated it, and other users can read it through `/proc/<pid>/environ`.
- If the server is MySQL 5.6 or later, `mysql_config_editor` or a `~/.my.cnf` with mode 600 also work.

**`scripts/backup.sh` has problems of its own,** which I can fix separately if you'd like:
- No strict mode.
- Unquoted expansions.
- A predictable `/tmp/backup.$$` path, open to symlink and race attacks.
- No cleanup trap, so a failed `tar` or `scp` leaves the archive behind in `/tmp`.
