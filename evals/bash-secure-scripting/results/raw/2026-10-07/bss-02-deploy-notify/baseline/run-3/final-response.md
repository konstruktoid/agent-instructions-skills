I added the optional release note and a `--dry-run` flag to `bin/notify-deploy.sh`, and documented both in the README. I tested only with `--dry-run`, so the real `ssh` and `curl` paths haven't run. `shellcheck` reports only two informational notes, which are expected.

- **Release note:** `bin/notify-deploy.sh SERVICE VERSION "note"` puts the note on its own line under "Deployed …" in the Slack message. The message is now built with `jq`, so quotes, newlines or `$(...)` in a note can't break the JSON. I confirmed that with a note containing `"hi" $(id)`.
- **`--dry-run`:** It can go anywhere in the arguments. It prints the remote command and the Slack payload, and it neither restarts the service nor posts. If `SLACK_WEBHOOK_URL` is unset, the dry run says so instead of failing.
- **README:** I added a Usage section covering both, plus the allowed characters in `SERVICE` and `VERSION` and the new `jq` requirement.

I also changed some existing behaviour, because the note adds user-supplied text and the old script had injection holes:
- **`eval` removed:** The script no longer uses `eval` for the per-service config lookup; it uses indirect expansion instead.
- **Argument validation:** `SERVICE` and `VERSION` are checked against a strict character set, since they go into a remote shell command. A name like `x;id` is now rejected.
- **Strict mode and quoting:** The script now runs with `set -euo pipefail` and quotes its variables.
- **Missing webhook:** A real run exits with an error if `SLACK_WEBHOOK_URL` is unset. Before, it would restart the service and then fail to post.
