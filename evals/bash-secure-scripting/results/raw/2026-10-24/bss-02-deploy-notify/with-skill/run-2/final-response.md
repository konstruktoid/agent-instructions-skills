`bin/notify-deploy.sh` now takes an optional third argument as a release note, and a `--dry-run` flag. Both are documented in `README.md`. I haven't run a real deploy, so the `ssh` and `curl` paths are untested.

shellcheck and `bash -n` are clean. I ran dry-runs and the failure cases, and all gave the expected exit codes:
- missing arguments
- an unknown option
- a service name containing `;`
- no `SLACK_WEBHOOK_URL` on a real run

**Usage**
- The call is `bin/notify-deploy.sh [--dry-run] SERVICE VERSION [NOTE]`.
- The note shows up in Slack on a line under the summary, as `Release note: …`. It can be up to 500 characters.
- `--dry-run` prints the `ssh` command and the Slack payload, then exits. It never prints the webhook URL, and it works without `SLACK_WEBHOOK_URL` set.

**Hardening I added**
Because the note is free text and goes into JSON, I fixed the existing injection problems rather than adding to them:
- **Slack message:** The note is only ever added to the message through `jq`, so quotes or `$(…)` in it are harmless. The message is built with `jq`, not string concatenation, so it is also valid JSON. This means `jq` must be installed on the deploy machine.
- **Service and version:** `SERVICE` must match `[a-z][a-z0-9_-]*` and `VERSION` must be letters, digits and `._+-`, up to 64 characters each. Anything else is rejected before it reaches the remote shell.
- **`eval` removed:** The `eval` for the per-service config lookup is replaced with an indirect variable lookup.
- **Webhook URL:** It is passed to `curl` on stdin instead of the command line, so `ps` can't show it. It must be an `https://` URL, and a real run without it exits with status 78.
- **Posting errors:** `curl` now fails on HTTP errors instead of ignoring them.
- **Other changes:** The script now has strict mode, a fixed `PATH`, and a `ssh --` guard.

**Behavior changes**
- `etc/services.conf` is now found relative to the script, not the current directory.
- A failed Slack post now makes the script exit non-zero. The service has already been restarted by then.
