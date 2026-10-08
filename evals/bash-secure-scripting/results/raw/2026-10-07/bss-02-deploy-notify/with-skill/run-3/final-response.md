`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. I tested the dry-run path and the failure paths below. I did not test the real ssh and Slack post, because there is no deploy host or webhook here.

**What I ran:** `shellcheck -x` and `bash -n` are clean. There is no `shfmt` on this machine, so I did not run a formatter check.
- A dry run with a note containing quotes, `$(id)` and a newline produced correct JSON, and nothing in the note was executed.
- A service name like `web;id` was rejected with exit 65.
- Too few arguments gave the usage message and exit 64.
- A control character in the note was rejected with exit 65.
- A real run without `SLACK_WEBHOOK_URL` stopped with an error and exit 1.

**The new options**
- **Release note:** `bin/notify-deploy.sh SERVICE VERSION "note"` adds the note on a new line in the Slack message. It is limited to 500 characters, and control characters other than newline and tab are rejected.
- **Dry run:** `--dry-run` can go anywhere in the arguments. It prints the remote command and the Slack payload, then exits without restarting the service or posting. It doesn't need `SLACK_WEBHOOK_URL` and never prints it.

**Other changes I made while in the script**
- **JSON payload:** The old script built the Slack JSON by string concatenation, so a note with a quote or newline would have broken it. The payload is now built with `jq`.
- **`eval` removed:** The per-service config lookup used `eval` on the service name, which I replaced with a safe indirect lookup.
- **Input validation:** The service name and version are checked against allowlist patterns before they go into the remote ssh command. Anything else is rejected with exit 65, which is new behavior for callers.
- **Webhook URL:** It is now passed to `curl` on stdin instead of as an argument, so it no longer shows in `ps`.
- **Hardening:** The script now has `set -Eeuo pipefail` and a fixed `PATH`. It loads `etc/services.conf` relative to the script rather than the current directory, and `curl` now fails on HTTP errors.

`jq` is now a dependency of the script.
