`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both.

I tested the dry run and the argument-rejection cases, but not a real deploy. The real path stops at `ssh`, because `deploy.example.internal` doesn't resolve here. ShellCheck and `bash -n` are clean. `shfmt` isn't installed, so I didn't run the formatter check.

- **Release note:** `bin/notify-deploy.sh web 1.4.2 "Fixes the login timeout"` puts the note on its own line under "Deployed web 1.4.2 by <user>". It can be up to 500 characters with no control characters.
- **`--dry-run`:** it prints the `ssh` command and the Slack JSON, then exits 0 without restarting anything or posting. It works anywhere among the arguments. It doesn't need `SLACK_WEBHOOK_URL` set and never prints the URL.

Adding a free-text field made the existing injection holes worse, so I fixed them in the same change:
- **`eval` removed:** the per-service config lookup now uses `${!var}`, and the service name must match `^[a-z][a-z0-9_]*$`.
- **Remote command guarded:** `ssh` sends a string that the remote shell re-parses, so the version is also checked (letters, digits, `.`, `_`, `+`, `-`). Anything else exits 2.
- **JSON built safely:** the Slack payload is now built with `jq`, so quotes or `$(...)` in a note stay literal. Before, they would have broken or altered the JSON.
- **Webhook URL kept off the command line:** `curl` now gets it on stdin instead of as an argument, so it no longer shows up in `ps`. It must be an `https://` URL, and it's checked before the restart, so a bad URL can't fail after the deploy has already run.
- **Strict mode and robustness:**
  - `set -Eeuo pipefail` replaces `set -e`.
  - `curl` fails on HTTP errors and times out after 30 seconds.
  - `etc/services.conf` is found relative to the script rather than the current directory.

Behaviour changes to be aware of:
- **Extra requirement:** the script now needs `jq` locally.
- **Hyphens:** service names with hyphens are rejected, because they can't be shell variable names. `web` and `api` work as before.
- **Exit codes:** 64 means usage error, 2 means invalid input, and 78 means a missing or bad webhook URL.

A note containing `<!channel>` would still ping the Slack channel, since I didn't escape Slack's own markup.
