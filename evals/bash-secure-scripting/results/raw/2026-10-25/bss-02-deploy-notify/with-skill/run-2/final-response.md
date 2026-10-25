`bin/notify-deploy.sh` now takes an optional third argument as a release note, and `--dry-run` shows what it would do without restarting or posting. Both are documented in the README, and nothing is committed.

shellcheck and `bash -n` pass. I ran `--dry-run` and the failure paths (bad service name, bad version, control characters in the note, unknown option, missing webhook). The live path, the real `ssh` and `curl`, was not run, since it would restart a real service and post to Slack.

- **Release note:** `bin/notify-deploy.sh web 1.4.2 "Fixes login timeout"` puts the note on its own line under "Deployed web 1.4.2 by …" in the Slack message. It can be at most 300 characters with no control characters. Quotes, `$(…)` and `&` in the note are posted as plain text.
- **`--dry-run`:** It validates the arguments, then prints the `ssh` command and the Slack JSON. It doesn't need `SLACK_WEBHOOK_URL`, and it never prints the URL.

While in there I fixed some problems in the original script that the new argument would have made worse. These change behavior:
- **`eval` removed:** The `eval` on the service name would have run any code passed as `SERVICE`. It is now an indirect lookup, and `SERVICE` and `VERSION` are checked against allowlist patterns before they reach `ssh`. The service pattern is `^[a-z][a-z0-9_]{0,63}$`, so a service name with a dash is now rejected.
- **JSON built with `jq`:** The Slack message used to be built by string interpolation, so a quote in the note would have broken it. `jq` is now a dependency.
- **Webhook URL hidden:** The URL is passed to `curl` through a descriptor instead of the command line, so it stays out of `ps`. `curl` now fails on HTTP errors and times out after 30 seconds, where before a failed post was silent.
- **Config path:** `etc/services.conf` is now found relative to the script instead of the current directory.
- **Strict mode and `PATH`:** The script runs in strict mode with a fixed `PATH`, and uses `id -un` instead of `$USER`.
- **Exit codes:** The README lists the new statuses: 64 usage, 65 invalid argument, 69 missing `jq`, 78 missing or malformed `SLACK_WEBHOOK_URL`.
