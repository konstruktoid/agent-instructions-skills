`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. I only ran dry runs. I never ran the real `ssh` or Slack `curl` path, so the stdin-config `curl` call and the `ssh --` form are untested against real endpoints. Nothing is committed.

**Release note**
- The note goes on a new line under "Deployed SERVICE VERSION by USER" in the Slack message.
- It is limited to 500 characters and can't contain control characters, which rules out newlines.

**`--dry-run`**
- The flag works anywhere on the command line. It prints the `ssh` command and the Slack payload, then exits 0 without restarting or posting.
- It never prints the webhook URL, only whether `SLACK_WEBHOOK_URL` is set. A real run now exits with status 78 if it isn't.

I also hardened the script, because adding a free-text argument made the old code unsafe:
- **`eval` removed:** `eval "CONFIG=\$CONFIG_$SERVICE"` is replaced with indirect expansion, `${!config_var}`.
- **Input validation:** the service name must match `[a-z][a-z0-9_]*` and the version `[A-Za-z0-9][A-Za-z0-9._+-]*`, each up to 64 characters. Anything else exits with status 65. Previously both went straight into the remote shell command.
- **JSON payload:** it is built with `jq`, so quotes and backslashes in the note can't break it.
- **Webhook URL:** it is passed to `curl` on stdin instead of on the command line, where `ps` could show it.
- **Smaller changes:**
  - Strict mode (`set -Eeuo pipefail`) and a fixed `PATH`.
  - `etc/services.conf` is now found relative to the script instead of the current directory.
  - `curl` now fails on an HTTP error instead of ignoring it.

Services with a hyphen in the name are now rejected. The old `eval` version couldn't read their config either, because a hyphen isn't valid in a variable name.

`shellcheck -x` and `bash -n` are clean. I ran dry runs with a note containing quotes, and with an injection attempt in the service name, a space in the version, a newline in the note, a missing argument, and no webhook set. The rejected inputs exited 65, or 64 for a missing argument, and the missing webhook exited 78. I didn't run `shfmt` because it isn't installed here.
