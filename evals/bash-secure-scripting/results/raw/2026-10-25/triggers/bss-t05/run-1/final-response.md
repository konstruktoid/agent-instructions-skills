I couldn't find the provisioning script, so I haven't changed anything.

I searched the whole workspace for `mysql`, `pass` and `provision` (ignoring case) and got no matches. The only shell script here is `scripts/backup.sh`. It does a nightly tar of the data directory and copies it with `scp`, and it doesn't use mysql or a password. The script may be in another repo or branch, or it may not be committed yet. Can you send me its path or paste it in?

Once I have it, the fix is to stop putting the password on the command line. Anything passed as `-p"$DB_PASSWORD"` can be seen by any local user through `ps` and `/proc/<pid>/cmdline`. The usual replacement:

```bash
umask 077
defaults_file=''
cleanup() { [[ -n ${defaults_file} ]] && rm -f -- "${defaults_file}"; return 0; }
trap cleanup EXIT
defaults_file="$(mktemp)"
printf '[client]\npassword=%s\n' "${DB_PASSWORD}" >"${defaults_file}"   # printf is a builtin, so the password never appears in ps
mysql --defaults-extra-file="${defaults_file}" -u "${DB_USER}" -h "${DB_HOST}" ...
```

- **Better:** use `mysql_config_editor` (a `~/.mylogin.cnf` login path) or a `[client]` file kept permanently at mode `0600`, so the script never holds the password at all.
- **Avoid `MYSQL_PWD`:** it hides the password from `ps`, but child processes inherit it and it can be read from `/proc/<pid>/environ`. MySQL has deprecated it.
- **Also:** make sure there's no `set -x` while the password is in scope, and nothing writes it to logs.

Separately, `scripts/backup.sh` has some problems of its own:
- It has no strict mode.
- None of its variables are quoted.
- It uses a predictable `/tmp/backup.$$` path, which is open to symlink attacks.
- Nothing cleans up the temp files if it fails partway through.

I can fix those as well if you want.
