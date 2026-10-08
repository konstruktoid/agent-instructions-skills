I couldn't find the provisioning script, so I haven't changed anything.

**What I searched:**
- Nothing in the workspace contains `mysql`, `password`/`passwd`, `provision`, or `DB_`, case-insensitive.
- The only shell script is `scripts/backup.sh`, a nightly `tar` + `scp` backup. It has no database step and no password.
- The other files (Dockerfile, CI configs, Ansible role, Terraform, k8s manifest, Go and Python sources) don't call mysql either.

I also don't have a file-editing or shell tool in this session. Even once we find the script, I can show you the exact change, but you'll have to apply it and run `shellcheck` and `bash -n` yourself.

**Can you tell me where the script is?** It may be in another repository or branch, or in a file that hasn't been committed yet. Its path or contents would be enough.

**This is the change I'll make.** Any password given as an argument (`mysql -p"$DB_PASS"` or `--password=...`) can be read by any local user through `ps` or `/proc/<pid>/cmdline`. It can also end up in shell history or `set -x` output. The fix is to give mysql the password in a temporary config file that only the script's user can read:

```bash
umask 077
defaults_file=''
cleanup() {
  if [[ -n ${defaults_file} && -f ${defaults_file} ]]; then
    rm -f -- "${defaults_file}"
  fi
  return 0
}
trap cleanup EXIT          # installed before mktemp
defaults_file="$(mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASS}" >"${defaults_file}"
unset DB_PASS

mysql --defaults-extra-file="${defaults_file}" -h "${DB_HOST}" "${DB_NAME}" <"${sql_file}"
```

`printf` is built into Bash, so the password never appears in a process's argument list. `--defaults-extra-file` has to be the first option on the mysql command line. I'd also make sure the password isn't printed by `set -x` or echoed to the logs anywhere else in the script.

Alternatively, `mysql_config_editor` can store the login in an obfuscated `~/.mylogin.cnf` for use with `--login-path`. `MYSQL_PWD` also avoids the argument list, but MySQL has deprecated it, so I'd avoid it.

**Separately, `scripts/backup.sh` has problems of its own:**
- It has no strict mode.
- None of its variables are quoted.
- Its temp directory is a predictable `/tmp/backup.$$`, which is open to symlink attacks.
- It has no cleanup trap, so the temp directory is left behind if `tar` or `scp` fails.

I can rewrite that too if you want.
