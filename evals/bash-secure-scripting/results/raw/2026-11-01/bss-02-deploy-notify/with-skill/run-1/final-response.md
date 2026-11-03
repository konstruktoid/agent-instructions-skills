`bin/notify-deploy.sh` now takes an optional third argument as a release note, and it has a `--dry-run` flag. Both are documented in the README. I couldn't run the real ssh and Slack path here, so that part is untested. ShellCheck and `bash -n` are clean.

**Usage:** `bin/notify-deploy.sh [--dry-run] SERVICE VERSION [NOTE]`
- **Release note:** it goes on a new line under "Deployed SERVICE VERSION by USER" in the Slack message. It can be up to 500 characters.
- **`--dry-run`:** it prints the ssh command and the Slack text, then exits. It doesn't restart anything or post anything, doesn't need `SLACK_WEBHOOK_URL`, and never prints it.

**Hardening:** the old script had injection holes, so I fixed these while I was in there, and they change behaviour for existing callers:
- **Input validation:** `SERVICE` and `VERSION` are checked against allowlists and rejected with exit 64 otherwise. Before, they went straight into an `eval` and an ssh remote command.
- **No `eval`:** the per-service config lookup uses indirect expansion instead. `etc/services.conf` is now found relative to the script, not the current directory.
- **Safe message building:** `jq` builds the JSON, so a note with quotes or `$(…)` can't break out of the message. `jq` is now a required dependency; I noted that in the README.
- **Webhook URL:** it's passed to curl through a config file descriptor instead of as an argument, so it no longer shows up in the process table. It must now be an `https://` URL or the script exits 78. `curl` now fails on HTTP errors and times out after 30 seconds.
- **Strict mode:** `set -Eeuo pipefail` is on, and a missing `SLACK_WEBHOOK_URL` now stops the script before the service is restarted.

**Checks run:**
- A dry run with a hostile note (`fix "quotes" & $(id)`) printed it literally.
- `web;id` as the service was rejected with exit 64.
- An unknown option gave a usage message and exit 64.
- With the webhook unset, a real run exited 78 before reaching ssh.
- A dry run from another working directory worked.
