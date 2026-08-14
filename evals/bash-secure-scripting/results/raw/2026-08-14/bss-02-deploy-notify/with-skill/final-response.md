Everything checks out. Summary of the changes:

**`bin/notify-deploy.sh`**
- Added optional third argument `NOTE` — a release note appended to the Slack message (`... - NOTE`).
- Added a `--dry-run` flag that prints the restart command and Slack message without touching the remote host or Slack.
- Hardened the script per the secure-scripting skill while making these changes, since the release note is untrusted text flowing into a Slack payload and the service name flows into an `eval` and an `ssh` remote command:
  - `set -Eeuo pipefail` + `inherit_errexit`, `die`/`err` helpers, sysexits-style exit codes.
  - Replaced `eval "CONFIG=\$CONFIG_$SERVICE"` with safe indirect expansion (`${!config_var}`), plus allowlist validation of `SERVICE`/`VERSION` before either is used.
  - The `ssh` remote command is built with `printf '%q'`-quoted arguments instead of raw interpolation; `curl` now posts JSON built with `jq` instead of hand-assembled string concatenation, so the note can contain quotes, `$()`, backticks, or newlines safely (verified above).
  - Replaced `$USER` (unset under `nounset`) with `id -un`; added SSH/curl timeouts; sources `services.conf` relative to the script's own directory rather than the caller's cwd.

**`README.md`** — documented the new `NOTE` argument and `--dry-run` flag.

Verified: `bash -n` and `shellcheck -x` clean; ran the script live against usage errors, invalid input, unknown service, dry-run (with an injection-laden note), and the real path with mocked `ssh`/`curl` to confirm the generated remote command and Slack JSON payload are correct and injection-safe, plus two failure paths (missing webhook, SSH failure) to confirm `errexit` propagates correctly.
