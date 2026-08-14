That fails safely — bash rejects it as an invalid variable name before any command is constructed, so the injection attempt never reaches `ssh`. All checks pass.

## Summary

Updated `bin/notify-deploy.sh` and `README.md`:

- **Release note**: new optional 3rd positional arg, appended to the Slack message text. Built into the JSON payload via `jq -n --arg`, so quotes/backslashes/newlines in the note can't break the JSON or inject content (verified above).
- **`--dry-run`**: parsed anywhere in the args; prints the SSH command and Slack message it *would* send, then exits before touching the network.
- Also fixed pre-existing bugs directly in the code path I was touching: the `eval "CONFIG=\$CONFIG_$SERVICE"` (arbitrary code execution on unsanitized `SERVICE`) is now safe indirect expansion `${!CONFIG_VAR}`, `SERVICE`/`VERSION` are shell-quoted with `printf %q` before going into the remote SSH command, and `SLACK_URL`/`REMOTE_HOST` are quoted. Unknown services now fail with a clear error instead of silently deploying with an empty config.
- README documents both the release-note argument and `--dry-run`.

Verified: syntax check, dry-run output, missing-args usage error, unknown-service error, JSON escaping of a release note containing quotes/backslashes/newlines/tabs, and that a `SERVICE` value with shell metacharacters fails safely instead of being injected.
