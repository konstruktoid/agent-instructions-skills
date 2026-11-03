`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. I only ran it with `--dry-run`, so the real ssh restart and Slack post are untested.

I ran a dry run with a note containing quotes and `$(id)`. The payload came out as plain text, and nothing was executed. `shellcheck` reports only an info-level note (SC2029) about `$REMOTE_CMD` expanding on the client side, which is intended here.

- **Release note:** `bin/notify-deploy.sh web 1.4.2 "Fixes login timeout"` adds a `Release note: …` line to the Slack message. I build the payload with `jq`, so quotes and special characters in the note can't break the JSON.
- **`--dry-run`:** it prints the remote command and the Slack payload, and says whether the webhook URL is set without printing it. It doesn't run ssh or curl. The flag works in any position.
- **README:** it has a new "Options" section covering both.

I also changed some existing behaviour, because I was editing those lines anyway:
- **Input checks:** `SERVICE` and `VERSION` are checked against a safe character set, because they go into the remote shell command. Anything with other characters is now rejected.
- **No more `eval`:** the per-service `CONFIG_<service>` lookup uses indirect expansion instead.
- **Quoting and errors:** variables are quoted, and the script uses `set -euo pipefail`. It prints usage and exits 2 if the arguments are wrong, and curl now fails on an HTTP error. A real run also errors out if `SLACK_WEBHOOK_URL` is unset, before anything is restarted.
- **`jq` dependency:** the script now needs `jq` installed. It is present on this machine.
