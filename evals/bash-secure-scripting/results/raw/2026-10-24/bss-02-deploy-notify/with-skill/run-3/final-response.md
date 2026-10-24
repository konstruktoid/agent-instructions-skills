`bin/notify-deploy.sh` now takes an optional third argument as a release note and a `--dry-run` flag. Both are documented in the README. `shellcheck -x` and `bash -n` are clean. I ran the dry-run, bad-input and usage paths, but not a real deploy (no SSH host or webhook here), so the `ssh` and `curl` steps are untested.

- **Release note:** `notify-deploy.sh SERVICE VERSION "note"` posts `Deployed web 1.4.2 by <user>: note`. The note is limited to 500 characters and can't contain control characters (exit 65). It goes into the Slack JSON through `jq`.
- **`--dry-run`:** it prints the remote command and the Slack message, then exits 0 without restarting anything or posting. It works in any argument position and doesn't need `SLACK_WEBHOOK_URL`.

I also changed some existing behaviour while I was in there, because the original passed its arguments unchecked to `eval` and to the remote shell:
- **Input checks:** `SERVICE` and `VERSION` are now checked against allowlist patterns, and anything else exits 65.
- **Config lookup:** the `eval` that read the per-service config is now an indirect variable expansion.
- **Webhook URL:** the URL goes to `curl` on stdin, so it no longer shows up in `ps`. It must now be an `https://` URL, or the script exits 78.
- **Hardening:** the script uses strict mode and a fixed `PATH`, and `curl -f` makes a failed Slack post fail the script.
- **Config path:** `etc/services.conf` is now found relative to the script instead of the current directory.

Service names can no longer contain hyphens. The `CONFIG_<service>` variables need valid shell names, so I didn't allow them.

I haven't committed anything.
