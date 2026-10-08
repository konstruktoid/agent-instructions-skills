I added the optional release note as a third argument and a `--dry-run` flag to `bin/notify-deploy.sh`, and documented both in the README. I tested only the dry-run path and the input validation. The real ssh and Slack paths haven't been run, since they need the deploy host and a webhook.

- **Release note:** `bin/notify-deploy.sh SERVICE VERSION "note"` puts the note on a second line of the Slack message. The payload is built with `jq`, so quotes, newlines and `$(...)` in the note arrive as plain text. A test note containing `"hi"` and `$(x)` came out intact in the payload.
- **`--dry-run`:** it can go anywhere in the arguments. It prints the ssh command and the Slack payload, then exits without restarting anything or posting.
- **README:** I updated the usage line and added "Release note" and "Dry run" sections with examples.

I also changed a few things the new feature touches, because the old script was unsafe with arbitrary input:
- **`eval` removed:** the per-service config lookup now uses indirect expansion instead of `eval`.
- **Input checks:** service and version are checked against a safe character set before they reach the remote command. For example, `a;b` is rejected with exit 2.
- **Quoting and error handling:** variables are quoted, the script uses `set -euo pipefail`, and `curl` now fails on HTTP errors.
- **Missing webhook:** a real run now stops with an error if `SLACK_WEBHOOK_URL` is unset. It checks this before the restart, so the service isn't restarted without a message being posted. `--dry-run` doesn't need the variable.

The script now depends on `jq`, which is installed here but should also be on the machine that runs it. `shellcheck` reports only two informational notes. One is that it can't follow `etc/services.conf`. The other is that `$remote_cmd` expands on the client side, which is intended.
