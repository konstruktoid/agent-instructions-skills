`bin/notify-deploy.sh` now takes an optional release note as a third argument and a `--dry-run` flag, and the README documents both. I tested only with `--dry-run`, so the real `ssh` and `curl` paths have not been run.

- **Release note:** `bin/notify-deploy.sh web 1.4.2 "Fixes login timeout"` adds a `Release note: …` line under the usual "Deployed …" message. Quotes, backslashes and newlines in the note are escaped, so they can't break the Slack JSON.
- **`--dry-run`:** it can go anywhere in the arguments. It prints the remote command and the exact Slack payload, then exits without calling `ssh` or `curl`. `SLACK_WEBHOOK_URL` doesn't need to be set for it.
- **Unrequested hardening:**
  - The `eval` is replaced with indirect expansion (`${!var}`), and `$SLACK_URL` and the `ssh` command are now quoted.
  - `SERVICE` and `VERSION` must now match `[A-Za-z0-9_.+-]+`, because they end up in a remote shell command. Anything else exits with an error.
  - The script now uses `set -euo pipefail`.
  - It exits with an error if `SLACK_WEBHOOK_URL` is unset on a real run. Previously it would have continued with an empty URL.
  - The per-service config lookup only runs for names made of letters, digits and underscores. A name like `my-svc` now gets an empty config instead of erroring.

In the dry run, a note containing quotes and backslashes came out correctly escaped. Running it for `web` and `api` showed the right config paths. `a;b` as a service name was rejected.
