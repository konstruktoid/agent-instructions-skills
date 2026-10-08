I couldn't find the script you mean, so I haven't changed anything.

I searched the whole workspace for `mysql` (case-insensitive) and for `pass`, `provision` and `DB_`. None of them matched. The only shell script here is `scripts/backup.sh`, which does a tar and `scp` and has no database or password handling. The other files are CI configs, a Dockerfile, Terraform, Ansible roles, and some Python and Go.

The script may be on another branch, in another repository, or not committed yet. It could also be inline in a CI step or the Dockerfile under a different name. I don't want to invent a script and guess at its contents.

Can you give me the path, or tell me which branch or repo it's in?

Once I have it, the fix is to stop putting the password in `mysql`'s arguments, where `ps` and `/proc` can show it to other users. Which option I'd use depends on how the script gets the password:
- **Option file:** write a `[client]` file with `password=…` into a `mktemp` file with mode 600, and pass it with `--defaults-extra-file=`. It has to be the first option on the command line. A trap on `EXIT` removes the file.
- **Environment variable:** set `MYSQL_PWD` for that one command only. It's simpler, but MySQL deprecates it, and other processes running as the same user can still read it from `/proc/<pid>/environ`.
- **Source of the password:** read it from a root-only file, a secrets manager, or a prompt, not from a variable set in the script or passed through the caller's environment.

I'd also check that `set -x` doesn't expose the password, and that it doesn't end up in a tracked file or a log.
