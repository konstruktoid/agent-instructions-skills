`bin/notify-deploy.sh` now takes an optional third argument as a release note, and a `--dry-run` flag that prints what it would do. I checked it only with `--dry-run`, plus the invalid-input and missing-webhook cases. The real `ssh` and `curl` path was not run, because that would restart a service and post to Slack. `shellcheck -x` and `bash -n` are clean, and no formatter is configured in the repo.

**What it does now**
- **Usage:** `notify-deploy.sh [--dry-run] SERVICE VERSION [NOTE]`.
- **Release note:** it appears in the Slack message on a second line, as `Release note: …`. It is limited to 500 characters.
- **`--dry-run`:** prints the remote command and the exact Slack payload, then exits 0 without calling `ssh` or `curl`. It doesn't need `SLACK_WEBHOOK_URL`, and the URL is never printed.
- **README:** documents both, with examples.

**Existing problems I fixed in the same script**
The note is free text going into JSON, and the old script already had injection problems that the note would have made worse.
- **JSON:** the payload is built with `jq`, so quotes or newlines in the note can't break the message.
- **`eval`:** the `eval` that looked up `CONFIG_$SERVICE` is replaced with `${!var}`.
- **`ssh`:** `SERVICE` and `VERSION` are checked against strict patterns (service `[a-z][a-z0-9_-]*`, version letters, digits and `._+-`, at most 64 characters each) before they reach the remote command. A name like `web;id` is rejected with exit 65.
- **Webhook URL:** it goes to `curl` on stdin instead of the command line, so it no longer shows in `ps`.
- **Failures:** the script now uses `set -Eeuo pipefail`, and `curl --fail` makes a Slack error produce a non-zero exit.
- **Config path:** `etc/services.conf` is found relative to the script, so it works from any directory.
- **`jq`:** the script now requires `jq` and says so in the README.

**Things you might trip over**
- A leading-dash note, such as `-x`, is read as an option. Put `--` before it, or start the note with a word.
- A hyphenated service like `my-svc` looks up `CONFIG_my_svc`.
- The note is posted as written, so Slack mentions like `<!channel>` in it will fire.
- When the real run is invoked without `SLACK_WEBHOOK_URL`, it now stops before the restart (exit 78). Previously it restarted the service and then failed to post.
