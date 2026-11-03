I couldn't find the provisioning script in this workspace, so nothing has been changed.

- A search of the whole workspace for `mysql`, `passw`, `provision` and `DB_` found nothing.
- The only shell script here is `scripts/backup.sh`. It runs `tar` and `scp` and doesn't touch a database.
- None of the other files (Terraform, Ansible role, Dockerfile, CI configs, k8s manifest, Python) mention MySQL or a database password either.

Also, I can only read and search files in this session. I don't have a tool to edit them or to run `shellcheck`. So even with the script in hand, I could write the fix but not apply or test it.

**The fix:** don't put the password in `mysql`'s arguments, because any user on the host can read them through `ps` or `/proc/<pid>/cmdline`. Write it to a private, temporary option file and point `mysql` at that:

```bash
creds=''
cleanup() { [[ -n ${creds} ]] && rm -f -- "${creds}"; return 0; }
trap cleanup EXIT          # set before mktemp so the file is always removed

creds="$(umask 077 && mktemp)"
printf '[client]\nuser=%s\npassword=%s\n' "${DB_USER}" "${DB_PASSWORD}" >"${creds}"
mysql --defaults-extra-file="${creds}" -h "${DB_HOST}" "${DB_NAME}" <provision.sql
unset DB_PASSWORD
```

- `printf` is a shell builtin, so writing the file never starts a process that would show the password in its arguments.
- `--defaults-extra-file` must be the first option given to `mysql`.
- Don't swap this for `MYSQL_PWD`. Other processes can read a program's environment too, and MySQL has deprecated that variable.
- There should be no `set -x` anywhere near this code, because it would print the password into the logs.
- The password should come from a file readable only by its owner or a secrets manager, never from a file the repository tracks.

**To finish this:** tell me where the script is (a path, or a branch it was committed on), or paste it in. With edit and shell access, I'll make the change and run it through `shellcheck` and `bash -n`.

Separately, `scripts/backup.sh` has problems of its own. It doesn't stop when a command fails, it doesn't quote its variables, and it uses a predictable `/tmp/backup.$$` path. That file isn't removed if the script fails partway through. I can fix that too if you want.
