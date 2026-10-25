`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. `shellcheck -x` and `bash -n` are clean. I ran `--dry-run` with and without a note, with the webhook set and unset, and with invalid input. I did not run a real deploy or post to Slack. The one non-dry run failed at `ssh`, since the deploy host isn't reachable from here, and stopped before posting. The repo has no formatter configuration, so I ran no `shfmt`.

- **Release note:** run `bin/notify-deploy.sh web 1.4.2 'note text'`. The note goes on a new line under the "Deployed … by …" message. It is limited to 500 characters.
- **`--dry-run`:** it prints the `ssh` command and the Slack payload. It doesn't run `ssh`, restart anything or post. It says whether `SLACK_WEBHOOK_URL` is set but never prints the value. It also works with `--` and `-h`.

I also hardened the script, because adding a free-text argument made the existing problems more serious:

- **`eval` removed:** `eval "CONFIG=\$CONFIG_$SERVICE"` would run whatever was in `SERVICE`. It is now an indirect lookup.
- **Input validation:** `SERVICE` and `VERSION` are checked against strict patterns before they reach the remote `ssh` command. Bad input exits with status 65, usage errors with 64.
- **JSON payload:** it is now built with `jq`, so quotes or `$(…)` in the note stay plain text. `jq` is a new requirement and is listed in the README.
- **Webhook URL:** it goes to `curl` on stdin instead of the command line, so it no longer shows up in `ps`. It must be a plain `https://` URL, and `curl` now fails on HTTP errors with a 30-second timeout. A real run exits with 78 if the URL is unset.
- **Smaller changes:**
  - Strict mode is `set -Eeuo pipefail`, and `PATH` is fixed.
  - `etc/services.conf` is found relative to the script rather than the current directory.
  - A service name with a `-` maps to `CONFIG_<name with _>`, since a hyphen can't appear in a variable name.
  - If `USER` is unset, the script uses `id -un`.

`etc/services.conf` is still sourced, so it runs as code. Keep it writable only by people who can already deploy.
