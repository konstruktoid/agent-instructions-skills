`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. `shellcheck -x` and `bash -n` are clean. I ran only dry runs and rejected-input cases. The real path (the `ssh` restart and the Slack post) was not run, and I didn't run a formatter.

- **Release note:** the note goes on a new line under "Deployed SERVICE VERSION by USER". It can be up to 500 characters with no control characters (so no newlines). The message is built with `jq`, so quotes and `$(...)` in a note stay plain text. In my dry run, a note containing `"bug"` and `$(id)` came out as literal text.
- **`--dry-run`:** it prints the service, version, config, the exact `ssh` command and the Slack payload, then exits 0. It restarts and posts nothing. It reports only whether the webhook is set, never the URL, and doesn't require it to be set.

While in the script I also fixed a few existing problems, since the new input goes through the same paths:
- **`eval` removed:** it ran on the service name. The name is now checked against an allowlist and the config is looked up by indirect variable expansion.
- **Validation:** the version is checked the same way. Both go into the `ssh` command, so a bad value is rejected with exit 65 before anything runs.
- **Webhook URL:** it was a command-line argument to `curl`, visible in `ps`. It now goes to `curl` on stdin, and `curl --fail` makes a failed post exit non-zero.
- **Other changes:** the script now uses `set -Eeuo pipefail`, a fixed `PATH`, and a path to `etc/services.conf` that no longer depends on the working directory. A missing or non-https webhook URL exits 78 on a real run.

Two behaviour changes to be aware of. A service name with a hyphen, like `my-svc`, now looks up `CONFIG_my_svc`, because bash variable names can't contain hyphens. Versions and service names that the old script accepted but fail the patterns (for example, a version containing a space) are now rejected.

I haven't committed anything.
