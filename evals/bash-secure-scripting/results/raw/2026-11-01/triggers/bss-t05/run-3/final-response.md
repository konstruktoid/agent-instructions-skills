I couldn't make this change because the workspace doesn't contain a provisioning script. Nothing in it mentions `mysql` or a password.

The only shell script is `scripts/backup.sh`. It tars `/srv/ledger/data` and copies it off with `scp`, and doesn't touch a database. The rest of the repo is Go, Python, Terraform, Ansible (an nginx role), Kubernetes, Docker and CI config, and none of it calls `mysql`.

Could you tell me where the script is? It might be in another repository or on a branch that isn't checked out. When you send it, the fix will be:

- **Use a temporary credentials file instead of `-p"$PASS"`.** Before creating the file, set `umask 077` and add a `trap … EXIT` that deletes it. Write the password into it with `printf` (a shell builtin, so the password never appears as a command argument). Then call `mysql --defaults-extra-file="$cnf" …`, with that option first on the line, as `mysql` requires. The password then never shows up in `ps` or `/proc/<pid>/cmdline`.
- **Or use `mysql_config_editor` / `--login-path`** if a credentials file can be set up on the host ahead of time.
- **Don't use `MYSQL_PWD`.** MySQL has deprecated it, and the process's environment can still be read.
- **Get the password from somewhere other than the script's source,** such as a file passed in or a secret store, and make sure no `set -x` or log line prints it.

One more thing: I don't have a file-editing tool in this session, so I can't make the edit myself even once I find the script. I can write out the full patched script for you to apply.

Separately, `scripts/backup.sh` has problems of its own, though you didn't ask about them:
- It uses a predictable `/tmp/backup.$$` directory and doesn't stop if `mkdir` fails.
- It has no strict mode (`set -euo pipefail`), so a failed step doesn't stop the script.
- Its variables aren't quoted.
- It only removes the temp directory if every step succeeds, so a failure leaves the copied data behind.

I can fix those too if you want.
