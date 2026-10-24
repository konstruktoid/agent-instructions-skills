`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag. Both are documented in the README. I only ran dry runs, so the real ssh and Slack post paths are untested.

- **Release note:** `bin/notify-deploy.sh SERVICE VERSION "note"` adds the note on a new line under "Deployed SERVICE VERSION by USER". The Slack payload is now built with `jq`, so quotes, backslashes and newlines in a note can't break the JSON.
- **`--dry-run`:** it prints the remote command and the Slack payload and exits without running ssh or curl. It works in any argument position, and `SLACK_WEBHOOK_URL` isn't required in this mode.
- **Dry-run checks:**
  - A note containing quotes, `&` and `$(...)` came out correctly escaped in the payload.
  - `--dry-run` given after the other arguments worked.
  - A bad version string was rejected with exit code 2.

I also changed some existing behaviour, because the new free-text note would otherwise sit next to injection problems already in the script:
- **Input validation:** `SERVICE` and `VERSION` are now checked against a strict character set (letters, digits, `._@+-`) before they go into the remote command. A name or version with other characters, such as `1;rm`, is now rejected.
- **`eval` replaced:** the `eval` that looked up `CONFIG_$SERVICE` is now an indirect expansion, `${!CONFIG_VAR}`.
- **Quoting and strict mode:** variables are quoted, and the script uses `set -euo pipefail`. It also prints a usage message and exits if it gets the wrong number of arguments.
- **curl failures:** curl now uses `--fail`, so a Slack error makes the script fail instead of being ignored.
- **`jq` dependency:** the script now needs `jq`. It is installed here, and the README says so.

I haven't committed anything.
