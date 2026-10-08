I couldn't find a provisioning script, so I haven't changed anything.

I searched the whole workspace for `mysql`, `password`/`PASS`, `provision` and `sql`, and nothing matched. The only shell script here is `scripts/backup.sh`, which is a tar-and-scp nightly backup with no database access. Could you tell me where the provisioning script lives, or add it to the workspace? I also don't have a file-editing or shell tool in this session, so once I can see it I'll give you the exact edit to apply.

This is the change it will need:

```bash
# Before: the password shows up in `ps` and /proc/<pid>/cmdline for as long as mysql runs
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < schema.sql

# After: give mysql an option file with mode 0600 that is deleted when the script exits
umask 077
defaults_file=''
cleanup() {
  if [[ -n ${defaults_file} && -f ${defaults_file} ]]; then
    rm -f -- "${defaults_file}"
  fi
  return 0
}
trap cleanup EXIT                 # set the trap before mktemp so no exit path leaves the file
defaults_file="$(mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASS}" >"${defaults_file}"
# printf is a shell builtin, so the password never appears in another process's arguments
mysql --defaults-extra-file="${defaults_file}" -- "${DB_NAME}" < schema.sql
```

Other things I'd fix in the same script:
- **Where the password comes from:** read it from a secret store or a mounted file with mode 0600, or prompt with `read -rs`. It shouldn't be hard-coded or written into a file the repo tracks.
- **Debug tracing:** remove any `set -x` around that code, because it would print the password.
- **Better option if the setup allows it:** `mysql_config_editor` login paths, or `auth_socket` when running as root locally, avoid having a password in the script at all.

Separately, `scripts/backup.sh` has problems of its own:
- It doesn't use strict mode.
- Its temporary directory is predictable (`/tmp/backup.$$`), and it isn't removed if the script fails partway.
- None of its variables are quoted.

I can harden that script too if you'd like.
