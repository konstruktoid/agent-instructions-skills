I couldn't find a provisioning script in this workspace, so I haven't changed anything.

- **No match:** I searched the whole workspace for `mysql`, `passw`, `provision`, `DB_` and `database`, ignoring case. Nothing came up.
- **Only shell script:** the one shell script here is `scripts/backup.sh`, which tars `/srv/ledger/data` and sends it with `scp`. It doesn't use a database or a password.
- **Other files:** the rest is Terraform, Kubernetes, CI configs, an nginx role, Go and Python. None of them call `mysql`.

**Where is the script?** It might be on another branch, in another repo, or embedded somewhere I didn't think to look. Point me to it and I'll fix it.

Also, this session only gives me read and search tools, so I can't edit files or run `shellcheck` here. Once you've pointed me to the script, I can write out the exact change for you to apply, or make it myself in a session with edit access.

**The fix:** keep the password out of the command line, because anything in a command's arguments is visible to other users on the machine (for example in `ps` or `/proc/*/cmdline`). Instead, write a temporary options file that only the script's user can read, and pass it to `mysql` with `--defaults-extra-file`:

```bash
umask 077
cnf=''
cleanup() { if [[ -n ${cnf} ]]; then rm -f -- "${cnf}"; fi; return 0; }
trap cleanup EXIT                       # installed before mktemp
cnf="$(mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASSWORD}" >"${cnf}"
mysql --defaults-extra-file="${cnf}" -h "${DB_HOST}" "${DB_NAME}" <"${sql_file}"
```

A few related points:

- `--defaults-extra-file` has to be the first option on the `mysql` command line.
- `printf` is a shell builtin, so it doesn't start a new process and the password never appears in an argument list.
- Don't use `MYSQL_PWD` instead: MySQL has deprecated it, and other processes can read it from `/proc/<pid>/environ`.
- On MySQL 5.6 or later, `mysql_config_editor` (login paths) is another option.
- Also check where the password comes from in the first place, and make sure there's no `set -x` around this code that would print it to the logs.
