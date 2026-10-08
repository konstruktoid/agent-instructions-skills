I added the release note as an optional third argument and a `--dry-run` flag to `bin/notify-deploy.sh`, and documented both in the README.

I ran `shellcheck -x` and `bash -n`, and both were clean. I also ran the script in dry-run mode with a normal note, a note containing quotes and `$(id)`, a note with a newline, a bad service name, an unknown option and a missing webhook, and from a different working directory. All behaved as intended. I couldn't test the real ssh restart or the Slack post, because they need the deploy host and a real webhook.

**New behaviour**
- **Release note:** `bin/notify-deploy.sh [--dry-run] SERVICE VERSION [NOTE]`. The note goes on its own "Release note:" line in the Slack message. It can be up to 500 characters with no control characters.
- **Dry run:** it prints the remote command and the Slack payload and exits 0. It never contacts the host or Slack, doesn't need `SLACK_WEBHOOK_URL`, and never prints the webhook URL.

**Other changes to existing behaviour**
- **Slack JSON:** the message used to be built with string interpolation, so a note containing quotes would have broken it. It is now built with `jq`.
- **Injection holes:** the old script passed `$SERVICE` to `eval` and put `$SERVICE` and `$VERSION` unquoted into the ssh command string. It now rejects any service or version that doesn't match a strict pattern. I replaced the `eval` with an indirect variable lookup.
- **Webhook URL:** it now goes to curl on stdin instead of the command line, where `ps` could show it.
- **Strict mode:** I added `set -Eeuo pipefail`.
- **Config path:** `etc/services.conf` is now found relative to the script instead of the current directory.
- **Failed Slack post:** curl now uses `--fail`, so a bad webhook response makes the script exit non-zero. Before, it was silently ignored.
- **Service names with a hyphen:** a hyphen is now mapped to an underscore when looking up `CONFIG_<service>`. Without that, a name like `my-svc` would be an invalid variable name.

**Things to know**
- **Exit codes:** invalid input exits 65, bad usage 64, and a missing or non-https webhook 78.
- **Slack mentions:** the note is plain text, so someone could put `<!channel>` in it and ping the channel. I didn't filter that.
