I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I couldn't test an actual provisioning run because the script needs root, `useradd` and MySQL. I only checked syntax and the validation path, where a file containing `Bad;name` was rejected with exit 1 before anything was created.

- **`--from-file FILE`**: reads one account name per line and skips blank lines and `#` comments. It adds to any names passed as arguments, so the cron job (`provision-user.sh $(cat …/next)`) works as before.
- **`--shell SHELL`**: passes the shell to `useradd -s`. It must be an absolute path that is executable and listed in `/etc/shells`.
- **Summary line**: each account prints `provisioned NAME (shell: …)`. If one account fails, the script reports it on stderr, continues with the rest and exits non-zero at the end.

Because the names now come from a file, I also changed these things in the old script:

- **Username check:** every name must match `[a-z_][a-z0-9_-]{0,31}`, and all are checked before any account is created. The old script put names unquoted into shell and SQL commands.
- **Admin password:** it now goes to `mysql` through a temporary 0600 defaults file instead of `-p…` on the command line, where `ps` could show it.
- **Account passwords:** they now come from `/dev/urandom` (24 alphanumeric characters) instead of `$RANDOM$RANDOM$RANDOM`.
- **Config path:** `etc/db.conf` is now found relative to the script, not the current directory.
- **File permissions:** the script sets `umask 077`, so new files are created 0600 (the README says the log is created that way).

**Passwords in the log:** I kept the existing behaviour of writing the generated passwords in plaintext to `/var/log/provision.log`. You may want to change that.

I haven't committed anything.
