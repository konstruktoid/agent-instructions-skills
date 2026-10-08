I couldn't find the provisioning script, so I haven't changed anything.

I searched the whole workspace for `mysql`, `password` and `provision`, ignoring case. Nothing matched in any file, including the CI configs, Dockerfile, Jenkinsfile, Ansible role, Terraform and k8s manifests. The only shell script here is `scripts/backup.sh`, which tars and `scp`s a data directory and never touches a database.

Can you point me to the script, or add it to this repo? Once I have it, the fix is:

- **Get the password off the command line.** `mysql -p"$PASS"` exposes it to anyone who can run `ps` or read `/proc/<pid>/cmdline`, and it can end up in shell history. I'd write it to a `mktemp` options file with mode 0600, delete that file from an `EXIT` trap set up before it's created, and point mysql at it with `--defaults-extra-file`, which has to be the first argument. The `MYSQL_PWD` environment variable is deprecated and also visible through `/proc/<pid>/environ`, so I wouldn't use it.
- **Read the password from a proper source** such as a secrets file, a vault lookup or a variable the caller injects, rather than hard-coding it. I'd also make sure no `set -x` runs around the code that uses it.
- **Check the result** with `shellcheck` and `bash -n`, then run it against a scratch database.

Separately, `scripts/backup.sh` has problems of its own:

- It has no strict mode.
- None of its variables are quoted.
- It uses a predictable `/tmp/backup.$$` directory that someone could plant a symlink at.
- If `tar` or `scp` fails, the temp directory is never removed.

I can harden that script too if you'd like.
