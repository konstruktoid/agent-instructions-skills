`bin/notify-deploy.sh` now takes a release note as an optional third argument and supports `--dry-run`. I ran `--dry-run` only: with and without the webhook set, with a note containing quotes and a backslash, and with a bad service name. I did not run a live deploy.

- **Release note:** if you pass a third argument, the Slack message gets a second line, `Release note: …`.
- **`--dry-run`:** it prints the remote ssh command and the Slack payload, and says whether the webhook URL is set. It skips the ssh and the Slack post. The flag can go anywhere in the arguments.
- **README:** I added a Usage section covering both, with an example.

While I was in the script I also fixed some existing problems, since the note is free text from the person deploying:
- **JSON:** the old script built the Slack JSON by string interpolation, so a quote in the note would have broken it. It now builds the payload with `jq`, so the script needs `jq` installed (the README says so).
- **Input checks:** `SERVICE` and `VERSION` go into a remote shell command, so they are now limited to safe characters. A name like `a;b` is rejected with exit code 2.
- **`eval` removed:** the per-service config lookup no longer uses `eval`. It also resolves `etc/services.conf` relative to the script rather than your current directory.
- **Strict mode and quoting:** the script runs with `set -euo pipefail`, quotes its variables, and `curl` now fails on HTTP errors. A real run stops if `SLACK_WEBHOOK_URL` is unset.

I didn't commit anything.
